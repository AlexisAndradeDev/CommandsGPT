# CommandsGPT

An implementation of GPT-4 to recognize instructions. It recognizes which commands it must run to fulfill the user's instruction, using a graph where each node is a command and the data generated by each command can be passed to other commands.

Create new commands easily by describing them using natural language and coding the functions corresponding to the commands.

# Installation

* Install the `commandsgpt` module.

```
pip install commandsgpt
```

If you're using a virtual environment:
```
pipenv install commandsgpt
```

* You also have to install the OpenAI package:

```
pip install openai
```

or

```
pipenv install openai
```

* Set an environment variable OPENAI_API_KEY to store your OpenAI key.

# Usage

Create a `commands` dictionary that will store the commands described in natural language. 

```python
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

Now, create the functions that will be called when the commands are executed.

* The name of the function is irrelevant.
* The first parameter must be the Config object; the second one must be the Graph object. Normally, you won't work directly with these objects, so you don't have to worry about them. Just use them as the first two parameters.
* The following parameters must match those described in the commands dictionary (name and data type).
* The return value must be a dictionary. Its keys, values and data types must match the return values described in the commands dictionary.

*Example of a command function*

```python
from commands_gpt.config import Config
from commands_gpt.commands.graphs import Graph

def request_user_input_command(config: Config, graph: Graph, message: str) -> dict[str, Any]:
    input_ = input(f"{message}\n*: ")
    results = {
        "input": input_,
    }
    return results
```

Create a `command_name_to_func` dictionary that will take the name of a command and return the corresponding function.

*Example of command_name_to_func dictionary*
```python
command_name_to_func = {
    "REQUEST_USER_INPUT": request_user_input_command,
    ...
}
```

Add the ***essential commands*** to your commands dictionaries.
* These are the default commands that implement core logic to the model's thinking, like an IF command.
* If you already defined your own core logic commands (IF command, THINK command, CALCULATE command, etc.), then you are free not to use them.

```python
from commands_gpt.commands.commands_funcs import add_essential_commands
add_essential_commands(commands, command_name_to_func)
```

Your `config` object:
```python
# keyword arguments are optional
config = Config("gpt-4-0314", verbosity=1, explain_graph=True, save_graph_as_file=False)
```

Create an instruction:

```python
instruction = input("Enter your instruction: ")
```

Create a recognizer:

```python
recognizer = ComplexRecognizer(config, commands, command_name_to_func)
```

Pass your instruction to the recognizer model:

```python
commands_data_str = recognizer.recognize(instruction)
```

Create the graph of commands and execute it:

```python
graph = Graph(recognizer, commands_data_str)
graph.execute_commands(config)
```

# Example

Create two files: `custom_commands.py` and `main.py`.

## custom_commands.py

```python
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
    "CONCATENATE_STRINGS": {
        "description": "Concatenates two strings. \"Hello\" and \"World\": \"HelloWorld\"",
        "arguments": {
            "str1": {"description": "String 1.", "type": "string"},
            "str2": {"description": "String 2.", "type": "string"},
            "sep": {"description": "Separator between the strs. Ex: \"\\n\", \",\", \"\".", "type": "string"},
        },
        "generates_data": {
            "concatenated": {"description": "Concatenated string.", "type": "str"},
        },
    },
}

# Commands functions

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

def concatenate_strings_command(config: Config, graph: Graph, str1: str, 
        str2: str, sep: str) -> dict[str, Any]:
    concatenated = f"{sep}".join((str1, str2))
    results = {
        "concatenated": concatenated,
    }
    return results

# add your functions here
command_name_to_func = {
    "WRITE_TO_USER": write_to_user_command,
    "REQUEST_USER_INPUT": request_user_input_command,
    "WRITE_FILE": write_file_command,
    "CONCATENATE_STRINGS": concatenate_strings_command,
}
```

## main.py
```python
from commands_gpt.recognizers import ComplexRecognizer
from commands_gpt.commands.graphs import Graph
from commands_gpt.config import Config
from custom_commands import commands, command_name_to_func

from commands_gpt.commands.commands_funcs import add_essential_commands
add_essential_commands(commands, command_name_to_func)

chat_model = "gpt-4-0314"

config = Config(chat_model, verbosity=2, explain_graph=False, save_graph_as_file=False)

instruction = input("Enter your prompt: ")

recognizer = ComplexRecognizer(config, commands, command_name_to_func)

commands_data_str = recognizer.recognize(instruction)
graph = Graph(recognizer, commands_data_str)
graph.execute_commands(config)
```
