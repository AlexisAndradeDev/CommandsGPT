import functools
import json
from typing import Any, Callable

from .. import regex
from ..static import StaticVar
from ..config import Config

@functools.total_ordering
class CommandNode:
    def __init__(self, data: list, commands: dict[str, dict], command_name_to_func: dict[str, Callable]):
        self.id = data[0]
        self.previous_command_id = data[1][0] if data[1] else None
        self.dependent_on_data = data[1][1] if data[1] else None
        self.required_value = data[1][2] if data[1] else None
        self.command_name = data[2]

        assert self.command_name in commands, f"Command '{self.command_name}' does not exist."
        assert self.command_name in command_name_to_func, f"Command '{self.command_name}' does not have a function declaration."

        self.command = command_name_to_func[self.command_name]
        self.arguments = data[3] if len(data) > 3 else None

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self):
        return f"CommandNode(id={self.id}, previous_command_id={self.previous_command_id}, dependent_on_data={self.dependent_on_data}, required_value={self.required_value}, command={self.command})"

    def execute_command(self, config: Config, graph, arguments: dict[str, Any]):
        print(f"\n\nRunning '{self.command_name}' command with id {self.id}...")
        if config.verbosity >= 2:
            print(f"Using arguments: {arguments}")
        self.data_generated = self.command(config, graph, **arguments)

class Graph:
    def __init__(self, raw_commands_data: StaticVar, commands: dict[str, dict], 
            command_name_to_func: dict[str, Callable]):
        self.build_graph(raw_commands_data, commands, command_name_to_func)

    def build_graph(self, raw_commands_data: StaticVar, commands: dict[str, dict], 
            command_name_to_func: dict[str, Callable]):
        self.raw_commands_data = raw_commands_data
        self.commands = commands
        self.command_name_to_func = command_name_to_func
        self.commands_data, self.data_references = generate_graph_data(raw_commands_data.val)
        self.build_nodes()

    def build_nodes(self):
        self.nodes: dict[str, CommandNode] = {}
        for command_data in self.commands_data:
            node = CommandNode(command_data, self.commands, self.command_name_to_func)
            self.nodes[node.id] = node

    def initialize_graph(self):
        self.generated_data = {}
    
    def inject_node_data(self, node_id: int, data_generated_by_node: dict[str, Any]):
        # inject data generated by the node to the data string
        new_raw_commands_data = StaticVar(regex.inject_node_data(
            self.raw_commands_data.val, node_id, data_generated_by_node,
        ))

        # rebuild graph
        self.build_graph(new_raw_commands_data, self.commands, self.command_name_to_func)
    
    def execute_node(self, node_id: int, config: Config):
        node = self.nodes[node_id]

        if node.id in self.generated_data:
            # already executed
            return self.generated_data[node.id]

        if node.previous_command_id is not None:
            previous_node_data_generated = self.execute_node(node.previous_command_id, config)

            if node.dependent_on_data:
                if previous_node_data_generated[node.dependent_on_data] != node.required_value:
                    return {}

        node.execute_command(config, self, node.arguments)
        self.generated_data[node.id] = node.data_generated

        if node.id in self.data_references:
            self.inject_node_data(node.id, node.data_generated)

        return node.data_generated

    def print_graph(self):
        print("\n\n--- Commands graph ---")
        for node in self.nodes.values():
            print(f"\n{node.id}. {node.command_name}")
            if node.previous_command_id:
                print(f"\n\tExecuted after node «{node.previous_command_id}».")
            if node.dependent_on_data:
                print(f"\n\t\tResult field '{node.dependent_on_data}' of node «{node.previous_command_id}» must have value «{node.required_value}» in order to execute this node.")
        print("\n--- -------------- ---\n")

    def execute_commands(self, config: Config):
        self.initialize_graph()
        if config.verbosity >= 1:
            self.print_graph()

        for node_id in sorted(self.nodes.keys()):
            self.execute_node(node_id, config)

def generate_graph_data(raw_commands_data):
    """
    Parses a commands data string to a JSON to create the graph data

    Args:
        raw_commands_data (str): A string containing raw commands data that has not yet been converted to a JSON.

    Returns:
        a tuple: Containing:
        
            commands_data: data of the commands (to create a graph).

            data_references: data references (data that will be injected).
    """
    data_references = regex.find_data_references_indices(raw_commands_data)
    commands_data = regex.nullify_all_data_references(raw_commands_data)

    # TODO: Fix JSON parsing error that is sometimes raised when newline characters are written.
    try:
        commands_data = json.loads(commands_data, strict=False)
    except Exception as e:
        print(f"!!! Raw commands data: {raw_commands_data}")
        raise e

    return commands_data, data_references