import openai
from typing import Callable

from .static import StaticVar
from .commands.graphs import Graph

def recognize_instruction(instruction: str, model: str, commands: dict, 
        verbosity: int = 0) -> StaticVar:
    """
    Analyzes an instruction and creates data to create a graph of commands
    that will fulfill the instruction.

    Args:
        instruction (str): The user's instruction.
        model (str): Name of the model.
        commands (dict): The commands that the model can use, described in
            natural language.
        verbosity (int): Level of detail printed by the function.

    Returns:
        a StaticVar of string: commands data (the answer from the instruction recognition model).
    """
    messages = [
        {
        'role': 'system', 
        'content':
            """You are a tool that, based on the user's prompt, detects the series of commands that must be executed, arguments that each command will have, and the relationship between each command (for example, what data generated by a command will be used as an argument for another)."""
            """\n*IMPORTANT*: *WRITE in the LANGUAGE that the USER writes his/her prompt in*."""
            """\n*IMPORTANT*: You can ONLY use the given commands. NEVER try to use OTHERS."""

            f"""\n\nCommands:\n{commands}"""

            """\n\nDepending on the prompt, you will use different commands and different arguments and relationships between commands. The only way you can see data generated by other commands from a command is by passing them as arguments."""

            """\n\n*Your response will have this format, ALWAYS stick to it*:"""
            """\n[[command_id, "COMMAND_NAME", {"arg1": value1, "arg2": value2, ...}, [[next_command_id, "dependent_on_data", required_value], [...], ...]], [...]]"""
            """\nTo reference data generated by a command, use __&i.data__. 'i' is the ID of the command; 'data' is the name of the generated data, and works like a Python value (if it's a list, you can use __&i.data[i]__, __&i.data[i:j]__, etc.; in a dictionary, __&i.data["key"]__, etc.)."""
            """\nYou can ONLY reference data in the arguments of the nodes."""
            """\nThe structure will ultimately be like a graph. The next_command_id defines which command will be executed next, dependent_on_data is the name of the data generated by the current command which will be used as a condition (null if it won't be used), and required_value is what value the dependent_on_data must have to execute the next command (or null if it doesn't matter)."""
            """\nA command can execute multiple next commands."""
            """\nBe concise but *solid* with the structure."""
            """\n*Consider that the user might write incorrectly and their inputs might be ambiguous*."""
            """\nThe only way to reference the data of other commands is by using the __&i.data__ referencing. Commands DO NOT KNOW each other's data."""
            """\nProvide all the relevant context in the arguments of the commands, so that you're not ambiguous."""
            """\nBe creative and logic when using the commands' arguments and data references."""

            """\n\nFor example:"""

            """\n\nExample 1:"""
            """\nUser prompt: 'Write an article about Lenz's Law, copy it to my clipboard and save it as a file.'"""
            """\nYour response might be: '[[1, "%s", {"about": "Article about Lenz's Law"}, [[2, null, null]]], [2, "%s", {"content": "__&1.thought__"}, [[3, null, null]]], [3, "%s", {"content": "__&1.thought__", "file_name": "Article about Lenz's Law"}, []]]'""" % ("THINK", "WRITE_CLIPBOARD", "WRITE_FILE")
            +
            """\n\nExample 2:"""
            """\nUser prompt: 'Read my clipboard, write a scientific article about the content in it, and save it as a file with a name related to the article.'"""
            """\nYour response might be: '[[1, "%s", {}, [[1, null, null]]], [2, "%s", {"about": "Scientific article about __&1.content__"}, [[3, null, null]]], [3, "%s", {"about": "Name including extension to save a file about this article: __&2.thought__"}, [[4, null, null]]], [4, "%s", {"content": "__&2.thought__", "file_name": "__&3.thought__"}, []]]'""" % ("READ_CLIPBOARD", "THINK", "THINK", "WRITE_FILE")
            +
            """\n\nExample 3:"""
            """\nUser prompt: 'Look up the best courses on ASP.Net on Google and show me the first page that appears, if it is relevant.'"""
            """\nYour response might be: '[[1, "%s", {"query": "best courses on ASP.Net"}, [[2, null, null]]], [2, "%s", {"url": "__&1.urls[0]__"}, [[3, null, null]]], [3, "%s", {"condition": "Is this a relevant course on ASP.Net? __&2.text__"}, [[4, "result", 1], [5, "result", 0]]], [4, "%s", {"content": "Relevant course: __&1.urls[0]__"}, []], [5, "%s", {"content": "It is not relevant."}, []]]'""" % ("SEARCH_GOOGLE", "READ_WEBPAGE", "IF", "WRITE_TO_USER", "WRITE_TO_USER")
            +

            """\n\nThe structure is JSON-like (so, use double quotes to create str, etc.)"""
        }
    ]
    messages.append({"role": "user", "content": instruction})
    print(f"Input tokens used by messages (graph creation): ~{len(str(messages)) / 4} tokens.")

    print("Getting answer from model...")
    response = openai.ChatCompletion.create(
        model=model, messages=messages,
    )

    raw_commands_data = StaticVar(response["choices"][0]["message"]["content"])

    if verbosity >= 2:
        print(f"\n\n~ ~ ~ ~ Commands graph string generated by the LLM\n\n{raw_commands_data.val}\n\n~ ~ ~ ~")

    return raw_commands_data

def recognize_instruction_and_create_graph(prompt: str, model: str, 
        commands: dict[str, dict], command_name_to_func: dict[str, Callable],
        verbosity: bool = 0) -> Graph:
    raw_commands_data = recognize_instruction(prompt, model, commands, verbosity=verbosity)
    graph = Graph(raw_commands_data, commands, command_name_to_func)
    return graph

def explain_graph_in_natural_language(raw_commands_data: str, commands: dict[str, dict]) -> str:
    messages = [
        {
        'role': 'system', 
        'content':
            """You are a tool that, given a graph of commands, explains in natural language what the graph does, how the nodes connect, and all the details about the graph, commands and nodes."""
            """\n*IMPORTANT*: *WRITE in the LANGUAGE that the USER writes his/her prompt in*."""

            f"""\n\nCommands:\n{commands}"""

            """\n\nThe graph of commands has this format:"""
            """\n[[command_id, "COMMAND_NAME", {"arg1": value1, "arg2": value2, ...}, [[next_command_id, "dependent_on_data", required_value], [...], ...]], [...]]"""
            """\nTo reference data generated by a command, use __&i.data__. 'i' is the ID of the command; 'data' is the name of the generated data, and works like a Python value (if it's a list, you can use __&i.data[i]__, __&i.data[i:j]__, etc.; in a dictionary, __&i.data["key"]__, etc.)."""
            """\nThe structure will ultimately be like a graph. The next_command_id defines which command will be executed next, dependent_on_data is the name of the data generated by the current command which will be used as a condition (null if it won't be used), and required_value is what value the dependent_on_data must have to execute the next command (or null if it doesn't matter)."""
            """\nA command can execute multiple next commands."""

            """\n\nExamples of graphs of commands generated from the user prompt:"""

            """\n\nExample 1:"""
            """\nUser prompt: 'Write an article about Lenz's Law, copy it to my clipboard and save it as a file.'"""
            """\nThe response might be: '[[1, "%s", {"about": "Article about Lenz's Law"}, [[2, null, null]]], [2, "%s", {"content": "__&1.thought__"}, [[3, null, null]]], [3, "%s", {"content": "__&1.thought__", "file_name": "Article about Lenz's Law"}, []]]'""" % ("THINK", "WRITE_CLIPBOARD", "WRITE_FILE")
            +
            """\n\nExample 2:"""
            """\nUser prompt: 'Read my clipboard, write a scientific article about the content in it, and save it as a file with a name related to the article.'"""
            """\nThe response might be: '[[1, "%s", {}, [[1, null, null]]], [2, "%s", {"about": "Scientific article about __&1.content__"}, [[3, null, null]]], [3, "%s", {"about": "Name including extension to save a file about this article: __&2.thought__"}, [[4, null, null]]], [4, "%s", {"content": "__&2.thought__", "file_name": "__&3.thought__"}, []]]'""" % ("READ_CLIPBOARD", "THINK", "THINK", "WRITE_FILE")
            +
            """\n\nExample 3:"""
            """\nUser prompt: 'Look up the best courses on ASP.Net on Google and show me the first page that appears, if it is relevant.'"""
            """\nThe response might be: '[[1, "%s", {"query": "best courses on ASP.Net"}, [[2, null, null]]], [2, "%s", {"url": "__&1.urls[0]__"}, [[3, null, null]]], [3, "%s", {"condition": "Is this a relevant course on ASP.Net? __&2.text__"}, [[4, "result", 1], [5, "result", 0]]], [4, "%s", {"content": "Relevant course: __&1.urls[0]__"}, []], [5, "%s", {"content": "It is not relevant."}, []]]'""" % ("SEARCH_GOOGLE", "READ_WEBPAGE", "IF", "WRITE_TO_USER", "WRITE_TO_USER")
            +

            """\n\nThe structure is JSON-like."""
        }
    ]
    messages.append({"role": "user", "content": raw_commands_data})
    print(f"Input tokens used by messages (graph explanation): ~{len(str(messages)) / 4} tokens.")

    print("Getting answer from model...")
    response = openai.ChatCompletion.create(
        model="gpt-4-0314", messages=messages,
    )

    explanation = response["choices"][0]["message"]["content"]

    return explanation