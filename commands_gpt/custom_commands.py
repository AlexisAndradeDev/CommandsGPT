"""
You are free to modify this module to create new commands.
You don't need to create them in this file; just pass the command functions
(as seen in main.py)
"""
from typing import Any
from pathlib import Path

from commands_gpt.config import Config
from commands_gpt.commands.graphs import Graph

commands = {
    "WRITE_TO_USER": {
        "description": "Writes something to the interface to communicate with the user.",
        "arguments": {
            "content": {"description": "Content to write.", "type": "string"},
        },
        "generates_data": {},
    },
    "REQUEST_USER_INPUT": {
        "description": "Asks the user to input data through the interface.",
        "arguments": {
            "message": {"description": "Message displayed to the user related to the data that will be requested (example: 'Enter your age').", "type": "string"},
        },
        "generates_data": {
            "input": {"description": "Data entered by the user", "type": "string"},
        },
    },
    "WRITE_FILE": {
        "description": "Write a file.",
        "arguments": {
            "content": {"description": "Content that will be written.", "type": "string"},
            "file_path": {"description": "Complete path of the file that will be written.", "type": "string"},
        },
        "generates_data": {},
    },
}

# Commands functions
# The name of the function is irrelevant
# The first argument must be the Config object, followed by the Graph object
# The arguments must match the arguments from the commands dictionary
# The return value must be a dictionary which keys must match the "generates_data" keys
# The data types must match the ones declared in the commands dictionary

def write_to_user_command(config: Config, graph: Graph, content: str) -> dict[str, Any]:
    print(f">>> {content}")
    return {}

def request_user_input_command(config: Config, graph: Graph, message: str) -> dict[str, Any]:
    input_ = input(f"{message}\n*: ")
    results = {
        "input": input_,
    }
    return results

def write_file_command(config: Config, graph: Graph, content: str, file_path: str) -> dict[str, Any]:
    file_dir = Path(file_path).parent
    assert file_dir.exists(), f"Container directory '{file_dir}' does not exist."
    with open(file_path, "w+", encoding="utf-8") as f:
        f.write(content)
        f.close()
    return {}

# add your functions here
command_name_to_func = {
    "WRITE_TO_USER": write_to_user_command,
    "REQUEST_USER_INPUT": request_user_input_command,
    "WRITE_FILE": write_file_command,
}
