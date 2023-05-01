import re
from typing import Any, Dict

def get_indexed_data(data_name: str, generated_data_by_node: Dict[str, Any]) -> Any:
    # Get the index/key from the data name
    start_index = data_name.index('[')
    end_index = data_name.index(']')
    index = data_name[start_index + 1:end_index]
    data_name = data_name[:start_index]

    # Get the data from the generated data dictionary
    data = generated_data_by_node.get(data_name)
    if isinstance(data, (list, tuple)):
        return data[int(index)]
    elif isinstance(data, dict):
        return data[index]
    else:
        raise AssertionError(f"Could not get data for {data_name}. Indexes for type {type(data)} are not supported.")

def replace_generated_data_by_node(match_obj, generated_data_by_node: Dict[str, Any]) -> str:
    # Get the data name from the matched object
    data_name = match_obj.group(1)

    # Check if the data name has an index/key
    if '[' in data_name and ']' in data_name:
        value = get_indexed_data(data_name, generated_data_by_node)
    else:
        value = generated_data_by_node[data_name]

    # Replace newlines with escaped newlines
    return str(value).replace(r"\n", "\\n")

def inject_node_data(raw_commands_data: str, node_id, generated_data_by_node: dict[str, Any]):
    pattern = rf"__&{node_id}\.(\w+)__"
    return re.sub(pattern, lambda m: replace_generated_data_by_node(m, generated_data_by_node), raw_commands_data)

def nullify_all_data_references(raw_commands_data: str):
    """Replaces all __&i.data__ by null."""
    pattern = r"__&(\d+)\.(\w+(?:\[\d+\])*)__"
    return re.sub(pattern, "null", raw_commands_data)

def find_data_references_indices(raw_commands_data: str) -> dict[int, dict[str, list[tuple]]]:
    """
    Returns a dictionary with the ID of each command and the name of the generated data, along with their start and end positions
    in the raw commands data string.

    Args:
        raw_commands_data (str): A string containing raw commands data that has not yet been converted to JSON.

    Returns:
        A dictionary where the keys are command IDs and the values are dictionaries representing the generated data for that
        command. These inner dictionaries have keys that are names of generated data variables and values that are lists of tuples.
        Each tuple in these lists contains the starting and ending positions of the generated data variable within the
        raw_commands_data input string.

    Example:
        >>> find_data_references_indices('''[1, [], "SEARCH_GOOGLE", {"query": "mejores cursos sobre ASP.Net"}], [2, [1, None, None], "READ_WEBPAGE", {"url": "__&1.urls[0]__"}], [3, [2, None, None], "IF", {"condition": "¿Es un curso relevante sobre ASP.Net? __&2.text__"}], [4, [3, "result", 1], "WRITE_TO_USER", {"content": "Curso relevante: __&1.urls[0]__"}], [5, [3, "result", 0], "WRITE_TO_USER", {"content": "No es relevante."}]''')
        {1: {'urls[0]': [(115, 129), (299, 313)]}, 2: {'text': [(214, 225)]}}
    """
    pattern = r"__&(\d+)\.(\w+(?:\[\d+\])*)__"
    matches = re.finditer(pattern, raw_commands_data)
    references = {}
    for match in matches:
        command_id = int(match.group(1))
        generated_data_name = match.group(2)
        start_index = match.start()
        end_index = match.end()

        if command_id not in references:
            references[command_id] = {}

        if generated_data_name not in references[command_id]:
            references[command_id][generated_data_name] = []

        references[command_id][generated_data_name].append((start_index, end_index))

    return references
