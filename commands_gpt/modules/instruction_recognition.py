import openai
import json
from typing import Any, Callable

from .commands.graphs import CommandNode
from .static import StaticVar
from . import regex
from .commands import graphs

def recognize_instruction(instruction: str, model: str, commands: dict) -> dict[str, Any]:
    """
    Analyzes an instruction and creates data to create a graph of commands
    that will fulfill the instruction.

    Args:
        instruction (str): The user's instruction.
        model (str): Name of the model.
        commands (dict): The commands that the model can use, described in
            natural language.

    Returns:
        tuple: A dict containing keys:
        
            'commands_data': data of the commands (to create a graph).

            'data_references': data references (data that will be injected).
            
            'raw_commands_data': string commands data (the answer from the instruction recognition model).
    """
    messages = [
        {
        'role': 'system', 
        'content':
            """You are a tool that, based on the user's prompt, detects the series of commands that must be executed, arguments that each command will have, and the relationship between each command (for example, what data generated by a command will be used as an argument for another)."""
            """\n*IMPORTANT*: *WRITE in the LANGUAGE that the USER writes his/her prompt in*."""

            f"""\n\nCommands:\n{commands}"""

            """\n\nDepending on the prompt, you will use different commands and different arguments and relationships between commands. The only way you can see data generated by other commands from a command is by passing them as arguments."""

            """\n\nYour response will have this format:"""
            """\n[[command_id, [previous_command_id, dependent_on_data, required_value], "COMMAND_NAME", {"arg1": value1, "arg2": value2, ...}], [...]]"""
            """\nTo reference data generated by a command, use __&i.data__. 'i' is the ID of the command; 'data' is the name of the generated data, and works like a Python value (if it's a list, you can use __&i.data[i]__, __&i.data[i:j]__, etc.; in a dictionary, __&i.data["key"]__, etc.)"""
            """\nThe structure will ultimately be like a graph. The previous_command_id defines after which command the current one will be executed, dependent_on_data is the name of the data generated by the previous command which will be used as a condition (null if it won't be used), and required_value is what value the dependent_on_data must have to execute the current one (or null if it doesn't matter)."""
            """\nBe concise with the structure."""

            """\n\nFor example:"""

            """\n\nExample 1:"""
            """\nUser prompt: 'Write an article about Lenz's Law, copy it to my clipboard and save it as a file.'"""
            """\nYour response might be: '[[1, [], "%s", {"about": "Article about Lenz's Law"}], [2, [1, null, null], "%s", {"content": "__&1.thought__"}], [3, [2, null, null], "%s", {"content": "__&1.thought__", "file_name": "Article about Lenz's Law"}]]'""" % ("THINK", "WRITE_CLIPBOARD", "WRITE_FILE")
            +
            """\n\nExample 2:"""
            """\nUser prompt: 'Read my clipboard, write a scientific article about the content in it, and save it as a file with a name related to the article.'"""
            """\nYour response might be: '[[1, [], "%s", {}], [2, [1, null, null], "%s", {"about": "Scientific article about __&1.content__"}], [3, [2, null, null], "%s", {"about": "Name including extension to save a file about this article: __&2.thought__"}], [4, [3, null, null], "%s", {"content": "__&2.thought__", "file_name": "__&3.thought__"}]]'""" % ("READ_CLIPBOARD", "THINK", "THINK", "WRITE_FILE")
            +
            """\n\nExample 3:"""
            """\nUser prompt: 'Look up the best courses on ASP.Net on Google and show me the first page that appears, if it is relevant.'"""
            """\nYour response might be: '[[1, [], "%s", {"query": "best courses on ASP.Net"}], [2, [1, null, null], "%s", {"url": "__&1.urls[0]__"}], [3, [2, null, null], "%s", {"condition": "Is this a relevant course on ASP.Net? __&2.text__"}], [4, [3, "result", 1], "%s", {"content": "Relevant course: __&1.urls[0]__"}], [5, [3, "result", 0], "%s", {"content": "It is not relevant."}]]'""" % ("SEARCH_GOOGLE", "READ_WEBPAGE", "IF", "WRITE_TO_USER", "WRITE_TO_USER")
        }
    ]
    messages.append({"role": "user", "content": instruction})
    print(f"Tokens used by messages: ~{len(str(messages)) / 4} tokens.")

    print("Recognizing...")
    response = openai.ChatCompletion.create(
        model=model, messages=messages,
    )

    raw_commands_data = StaticVar(response["choices"][0]["message"]["content"])

    data_references = regex.find_data_references_indices(raw_commands_data.val)
    commands_data = regex.nullify_all_data_references(raw_commands_data.val)
    commands_data = json.loads(commands_data)

    return {"commands_data": commands_data, "data_references": data_references,
        "raw_commands_data": raw_commands_data}

def recognize_instruction_and_create_graph(prompt: str, model: str, 
        commands: dict[str, dict], command_name_to_func: dict[str, Callable]) -> \
        tuple[dict[str, CommandNode], dict[str, Any]]:
    graph_data = recognize_instruction(prompt, model, commands)
    return graphs.build_dependency_graph(graph_data["commands_data"], commands, command_name_to_func), graph_data
