# CommandsGPT

An implementation of GPT-4 to recognize instructions. It recognizes which commands it must run to fulfill the user's instruction, using a graph where each node is a command and the data generated by each command can be passed to other commands.

Create new commands easily by describing them using natural language and coding the functions corresponding to the commands.

# Installation

Install the `commandsgpt` module.

```
pip install commandsgpt
```

If you're using a virtual environment:
```
pipenv install commandsgpt
```

# Basic usage

Create a `commands` dictionary that will store the commands described in natural language. Create the functions that will be called when the commands are executed (they must match the arguments and return values of the `commands` dict; the first parameter of these functions must be a Config object). Create a `command_name_to_func` dictionary that will take the name of a command and return the corresponding function.

*Example of commands dictionary*
```
commands = {
    "REQUEST_USER_INPUT": {
        "description": "Asks the user to input data through the interface.",
        "arguments": {
            "message": {"description": "Message displayed to the user related to the data that will be requested (example: 'Enter your age').", "type": "string"},
        },
        "generates_data": {
            "input": {"description": "Data entered by the user", "type": "string"},
        },
    },
    ...
}
```

*Example of a command function*
```
def request_user_input_command(config: Config, graph: Graph, message: str) -> dict[str, Any]:
    input_ = input(f"{message}\n*: ")
    results = {
        "input": input_,
    }
    return results
```

*Example of command_name_to_func dictionary*
```
command_name_to_func = {
    "REQUEST_USER_INPUT": request_user_input_command,
    ...
}
```

Add the ***essential commands*** to your commands dictionaries.
* These are the default commands that implement core logic to the model's thinking, like an IF command.
* If you already defined your own core logic commands (IF command, THINK command, etc.), then you are free not to use them.

```
from commands_gpt.commands.commands_funcs import add_essential_commands
add_essential_commands(commands, command_name_to_func)
```

Your `config` object: 
```
config = Config("gpt-4-0314", verbosity=1) # verbosity is optional
```

Create an instruction:

```
instruction = input("Enter your instruction: ")
```

Pass your instruction to the recognizer model:

```
graph = recognize_instruction_and_create_graph(
    instruction, config.chat_model, commands, command_name_to_func,
)
```

Finally, execute the graph of commands:

```
graph.execute_commands(config)
```

# Basic example

```
from typing import Any
from pathlib import Path
from commands_gpt.instruction_recognition import recognize_instruction_and_create_graph
from commands_gpt.commands.graphs import execute_commands
from commands_gpt.config import Config

# Commands Natural Language Dict

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

def write_to_user_command(config: Config, graph: Graph, content: str) -> dict[str, Any]:
    # add newlines because regex data injection replaces newline characters
    # by \\n substrings.
    content_with_newlines = "\n".join(content.split("\\n"))
    print(f">>> {content_with_newlines}")
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

# Command name to function dict
command_name_to_func = {
    "WRITE_TO_USER": write_to_user_command,
    "REQUEST_USER_INPUT": request_user_input_command,
    "WRITE_FILE": write_file_command,
}

from commands_gpt.commands.commands_funcs import add_essential_commands
add_essential_commands(commands, command_name_to_func)

chat_model = "gpt-4-0314"

config = Config(chat_model, verbosity=1)

instruction = input("Enter your prompt: ")
graph = recognize_instruction_and_create_graph(
    instruction, config.chat_model, commands, command_name_to_func,
)
graph.execute_commands(config)
```

# Adding custom commands

You can add and modify your own custom commands by creating two dictionaries:

* commands: The commands that the model can use, described in natural language. The keys are the name of the commands, and the values are dictionaries.

    * The nested dictionaries have keys *description*, *arguments* and *generates_data*.

    * **description**: Description of the command in natural language.

    * **arguments**: Arguments that the function of the command receives. It's a dictionary which keys are the names of the arguments, and the values are dictionaries that describe the arguments. 

        * The nested dictionaries have keys *description* and *type*.
        * **description**: Description of the argument in natural language.


        * **type**: Data type. E.g.: "string", "boolean", "int".

    * **generates_data**: The data generated by the command that other commands will be able to access. It's a dictionary which keys are the names of the data field, and the values are dictionaries that describe the data field.

        * The nested dictionaries have keys *description* and *type*.

        * **description**: Description of the data field in natural language.

        * **type**: Data type. E.g.: "string", "boolean", "int".

***Example***
```
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
```

* command_name_to_func: The keys of this dictionary are the name of the commands, and the values are the function.

    * The name of the function is irrelevant.

    * The first argument must be the Config object. The second argument is the Graph object.

    * The arguments must match the arguments from the commands dictionary.

    * The return value must be a dictionary which keys must match the "generates_data" key.

    * The data types must match the ones declared in the commands dictionary.

***Example***
```
def write_to_user_command(config: Config, graph: Graph, content: str) -> dict[str, Any]:
    # add newlines because regex data injection replaces newline characters
    # by \\n substrings.
    content_with_newlines = "\n".join(content.split("\\n"))
    print(f">>> {content_with_newlines}")
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
```
