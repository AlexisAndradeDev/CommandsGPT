import json
from typing import Any, Callable

from ..recognizers import AbstractRecognizer
from .. import regex
from ..config import Config

# next commands field indexes
NEXT_COMMAND_ID = 0
DEPENDENT_ON_DATA = 1
REQUIRED_VALUE = 2

class CommandNode:
    def __init__(self, data: dict, commands: dict[str, dict], 
            command_name_to_func: dict[str, Callable]):
        self.id = data["id"]
        self.command_name = data["name"]

        assert self.command_name in commands, f"Command '{self.command_name}' does not exist."
        assert self.command_name in command_name_to_func, f"Command '{self.command_name}' does not have a function declaration."

        self.command = command_name_to_func[self.command_name]

        self.arguments = data["arguments"]
        self.next_commands: list[list[int | str | Any]] = data["next_commands"]

        self.data_generated = None

    def __str__(self):
        return f"CommandNode(id={self.id}, command={self.command})"

    def execute_command(self, config: Config, graph, arguments: dict[str, Any]):
        print(f"\n\nRunning '{self.command_name}' command with id {self.id}...")
        if config.verbosity >= 2:
            print(f"Using arguments: {arguments}")
        self.data_generated = self.command(config, graph, **arguments)
    
    def get_next_commands_to_execute(self) -> list[int]:
        next_commands_to_execute = []
        for next_command in self.next_commands:
            next_command_id = next_command[NEXT_COMMAND_ID]
            dependent_on_data = next_command[DEPENDENT_ON_DATA]
            required_value = next_command[REQUIRED_VALUE]

            if dependent_on_data is None: # doesn't matter the result of current node
                next_commands_to_execute.append(next_command_id)
            else: # next command execution depends on the result of current node
                if self.data_generated[dependent_on_data] == required_value:
                    next_commands_to_execute.append(next_command_id)
        return next_commands_to_execute

class Graph:
    def __init__(self, recognizer: AbstractRecognizer, commands_data_str: str):
        self.set_start_data(recognizer, commands_data_str)
        self.initialize()

    def set_start_data(self, recognizer: AbstractRecognizer, commands_data_str: str):
        self.recognizer = recognizer
        self.commands_data_str = commands_data_str
        self.commands = recognizer.commands
        self.command_name_to_func = recognizer.command_name_to_func

    def build_graph(self, commands_data_str: str):
        self.set_start_data(self.recognizer, commands_data_str)

        graph_build_data = generate_graph_build_data(commands_data_str)
        (self.commands_data_str_by_node,
         self.commands_data,
         self.data_references_in_each_command) = graph_build_data

        self.build_nodes()

    def build_node(self, command_data: dict) -> CommandNode:
        node = CommandNode(command_data, self.commands, self.command_name_to_func)
        if node.id in self.reached_nodes_ids:
            # recover results of the node
            reached_node = self.nodes[node.id]
            node.data_generated = reached_node.data_generated
        return node

    def build_nodes(self):
        for command_data in self.commands_data.values():
            node = self.build_node(command_data)
            self.nodes[node.id] = node

    def initialize(self):
        self.reached_nodes_ids: list[int] = []
        self.nodes: dict[str, CommandNode] = {}
        self.build_graph(self.commands_data_str)
            
    def execute_node(self, node_id: int, config: Config) -> list[int]:
        node = self.nodes[node_id]

        # inject data references to current node's arguments
        injected_command_data_str = self.commands_data_str_by_node[node.id]
        for node_to_inject_id in self.data_references_in_each_command[node.id]:
            node_to_inject = self.nodes[node_to_inject_id]
            # update node data
            injected_command_data_str = regex.inject_node_data(
                injected_command_data_str, node_to_inject.id,
                node_to_inject.data_generated,
            )
        injected_command_data = get_node_command_data(injected_command_data_str)

        # update node
        node = self.build_node(injected_command_data)
        self.nodes[node.id] = node

        node.execute_command(config, self, node.arguments)
        self.reached_nodes_ids.append(node.id)
        
        next_commands_to_execute = node.get_next_commands_to_execute()
        return next_commands_to_execute

    def print_graph(self, explain_graph: bool):
        print("\n\n--- Commands graph ---")

        print("\n~~ Graph ~~")
        for node in self.nodes.values():
            print(f"\n{node.id}. {node.command_name}")
            
            if node.next_commands:
                print(f"\tCommands executed by this node:")
                for next_command_id, dependent_on_data, required_value in node.next_commands:
                    next_node = self.nodes[next_command_id]
                    print(f"\t{next_node.id}. {next_node.command_name}")
                    if dependent_on_data is not None:
                        print(f"\t\tIf '{dependent_on_data}' generated data has value: {required_value}.")

        if explain_graph:
            print("\n~~ Explanation ~~")
            explanation = self.recognizer.explain_graph_in_natural_language(self.commands_data_str)
            print(explanation)

        print("\n--- -------------- ---\n")

    def execute_commands(self, config: Config):
        self.initialize()
        if config.verbosity >= 1:
            self.print_graph(config.explain_graph)

        first_node_id = sorted(self.nodes.keys())[0]
        next_commands_to_execute = self.execute_node(first_node_id, config)
        new_next_commands_to_execute = []
        while True:
            new_next_commands_to_execute.clear()
            for next_command_id in next_commands_to_execute:
                new_next_commands_to_execute.extend(self.execute_node(next_command_id, config))
            next_commands_to_execute = new_next_commands_to_execute.copy()

            if not next_commands_to_execute:
                break

def get_node_data_references(command_data_str: str) -> dict:
    data_references = regex.find_data_references_indices(command_data_str)
    return data_references

def unescape_node_arguments(arguments: dict):
    for name, value in arguments.items():
        if type(value) is str:
            arguments[name] = regex.unescape_str_in_json(value)
        # TODO: Unescape strings inside of lists/dicts/tuples arguments.

def get_node_command_data(command_data_str: str) -> dict:
    nullified_data_str = regex.nullify_all_data_references(command_data_str)
    command_data_as_list = json.loads(nullified_data_str, strict=False)

    id_ = command_data_as_list[0]
    name = command_data_as_list[1]
    arguments = command_data_as_list[2]

    unescape_node_arguments(arguments)

    next_commands: list[list[int | str | Any]] = command_data_as_list[3]
    assert all(
        map(
            lambda next_command:
                (type(next_command[0]) is int and 
                    type(next_command[1]) in [str, type(None)]),
            next_commands,
        )
    ), f"Next commands field must match data types: list[list[int, str, Any]].\n{next_commands}"

    command_data = {
        "id": id_,
        "name": name,
        "arguments": arguments,
        "next_commands": next_commands,
    }

    return command_data

def generate_graph_build_data(commands_data_str: str):
    """
    Parses a commands data string to a JSON to create the graph data

    Args:
        commands_data_str (str): A string containing the data to create a graph/command.

    Returns:
        a tuple: Containing:
            commands_data_str_by_node (dict of str): Commands data as a string.
                Keys are the ID of the commands; values are the commands data
                as strings.
        
            commands_data: data of the commands as JSON (to create a graph).

            data_references_in_each_command: data references that appear inside of each command (data that will be injected).
                A key is the ID of a command. The value stores a dictionary of data references inside of that particular command.
    """
    data_references_in_each_command = {}

    commands_data = {}
    commands_data_str_by_node = {}
    for line_num, command_data_str in enumerate(commands_data_str.splitlines(), start=1):
        data_references = get_node_data_references(command_data_str)
        try:
            command_data = get_node_command_data(command_data_str)
        except Exception as e:
            print(f"!!! Can't decode command data string to JSON in line {line_num}: {command_data_str}")
            raise e

        command_id = command_data["id"]

        commands_data_str_by_node[command_id] = command_data_str
        commands_data[command_id] = command_data
        data_references_in_each_command[command_id] = data_references

    return commands_data_str_by_node, commands_data, data_references_in_each_command