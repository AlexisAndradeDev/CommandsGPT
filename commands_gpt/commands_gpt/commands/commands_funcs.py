from typing import Any, Callable

from ..chat import get_answer_from_model
from ..config import Config
from .graphs import Graph
from ..util.math_expr import safe_eval_math_expr

ESSENTIAL_COMMANDS = {
    "THINK": {
        "description": "Generates a thought in your 'mind' without writing it down yet. This command allows you to create new ideas, reflect, and analyze information. For example, when asked to 'Write a three-paragraph article about Lenz's Law,' you would first use this command to generate the article and then use another to write it.",
        "arguments": {
            "about": {"description": "What to think about. Example: 'Three-paragraph article about Lenz's Law.'", "type": "string"},
        },
        "generates_data": {
            "thought": {"description": "Text generated by thinking.", "type": "string"},
        },
    },
    "IF": {
        "description": "Returns the Boolean value of a condition.",
        "arguments": {
            "condition": {"description": "Condition. Can be in natural language.", "type": "string"},
        },
        "generates_data": {
            "result": {"description": "Result of the condition: 0 or 1.", "type": "boolean"},
        },
    },
    "CALCULATE": {
        "description": "Evaluates a mathematical expression in a str. Supports +, -, *, /, %, **, //. Can be entered in natural language.",
        "arguments": {
            "expression": {"description": "Math expression. '(-1) ** (1/2)', 'Negative one raised to 1/2.'", "type": "string"},
        },
        "generates_data": {
            "result": {"description": "Result of evaluation", "type": "int or float or complex"},
        },
    },
    # TODO: Create a FOR command to increment a counter variable
}

# Commands functions
# Must be named 'LowercaseCommandName_command'
# The first argument must be the Config object, followed by the Graph object
# The arguments must match the arguments from the ESSENTIAL_COMMANDS dictionary
# The return value must be a dictionary which keys must match the "generates_data" keys
# The data types must match the ones declared in the ESSENTIAL_COMMANDS dictionary

def think_command(config: Config, graph: Graph, about: str) -> dict[str, Any]:
    messages = [
        {
            "role": "system", 
            "content": "You are a model used when executing a 'THINK' command, which function is to reflect, think, write, or ideate."
        },
    ]
    thought = get_answer_from_model(about, config.chat_model, messages)

    results = {
        "thought": thought,
    }
    return results

def if_command(config: Config, graph: Graph, condition: str) -> dict[str, Any]:
    messages = [
        {
            "role": "system", 
            "content": f"You are a model that evaluates conditions, both in natural language and symbolic language. Given a condition, you respond with the number «1» (true) or «0» (false). DO NOT write ANYTHING ELSE EVER.",
        },
    ]
    result = get_answer_from_model(condition, config.chat_model, messages)
    try:
        result = bool(result)
    except Exception as e:
        print(f"Could not convert result from IF command '{result}' to boolean.")
        raise e

    results = {
        "result": result,
    }
    return results

def calculate_command(config: Config, graph: Graph, expression: str) -> dict[str, Any]:
    try:
        result = safe_eval_math_expr(expression)
    except ValueError:
        # TODO: convert from natural language to math expression
        messages = [
            {
                "role": "system",
                "content": f"You are a model that takes a math expression in natural language and returns JUST the math expression, without any words. 'Negative one raised to the 1/2 plus eight' -> '(-1) ** (1/2) + 8'"
            }
        ]
        expression_ = get_answer_from_model(expression, config.chat_model, messages)
        result = safe_eval_math_expr(expression_)

    results = {
        "result": result,
    }
    return results

ESSENTIAL_COMMAND_NAME_TO_COMMAND_FUNC = {
    key: eval(f"{key.lower()}_command")
    for key in ESSENTIAL_COMMANDS
}

def get_command(command_name: str) -> Callable:
    """
    Returns the function corresponding to the name.

    Args:
        command_name (str): Name of the function.

    Returns:
        function: The corresponding function.
    """    
    return ESSENTIAL_COMMAND_NAME_TO_COMMAND_FUNC[command_name]

def add_commands(commands: dict[str, dict], command_name_to_func: dict[str, dict],
        new_commands: dict[str, dict], new_command_name_to_func: dict[str, Callable]):
    commands.update(new_commands)
    command_name_to_func.update(new_command_name_to_func)

def add_essential_commands(commands: dict[str, dict], command_name_to_func: dict[str, dict]):
    add_commands(commands, command_name_to_func, ESSENTIAL_COMMANDS, ESSENTIAL_COMMAND_NAME_TO_COMMAND_FUNC)
