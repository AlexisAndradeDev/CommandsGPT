import openai
import json
from pathlib import Path
from tqdm import tqdm
from time import sleep
from itertools import combinations, chain
from random import shuffle
from math import ceil

from .instruction_recognition import recognize_instruction

def autogenerate_random_instruction_using_a_command(model: str, commands: dict, 
        commands_combination: str) -> str:
    messages = [
        {
        'role': 'system', 
        'content':
            """You are a tool that creates random NATURAL and COMMON instructions that are achievables using the specified commands as if YOU WERE THE USER."""
            """\n*IMPORTANT*: You can ONLY use the given commands. DO NOT generate instructions that CANNOT BE DONE with JUST the specified commands."""
            """\n*IMPORTANT*: JUST write the INSTRUCTION. Nothing else."""

            f"""\n\nCommands:\n{commands}"""

            """\n\nFor example:"""

            """\nUser: 'Generate an instruction using the THINK and WRITE_FILE commands.'"""
            """\nYour answer (a random instruction using the requested commands): 'Write an article about Lenz's Law and save it as a file.'"""

            """\nUser: 'Generate an instruction using the REQUEST_USER_INPUT, THINK and WRITE_TO_USER commands.'"""
            """\nYour answer (a random instruction using the requested commands): 'Ask me my favorite color and write an article about it.'"""
        }
    ]

    messages.append({"role": "user", "content": f"Generate an instruction using these commands: [{commands_combination}]."})
    print(f"Input tokens used by messages (instruction generation): ~{len(str(messages)) / 4} tokens.")

    print("Getting answer from model...")
    response = openai.ChatCompletion.create(
        model=model, messages=messages,
    )

    instruction = response["choices"][0]["message"]["content"]
    return instruction

def combination_to_str(combination: tuple[str]):
    return ",".join(combination)

def get_commands_combinations(commands: list[str],
        max_commands_per_combination: int = 4) -> list[tuple[str]]:
    max_commands_per_combination = min(len(commands), max_commands_per_combination)
    combinations_ranges = [
        combinations(commands, i) 
        for i in range(2, max_commands_per_combination + 1)
    ]
    combined_combinations = list(chain.from_iterable(combinations_ranges))
    return combined_combinations

def autogenerate_random_instructions(model: str, commands: dict, 
        iterations_per_combination: int = 1, wait_for_approval: bool = False,
        request_commands_combinations: bool = True,
        combinations_percentage_to_use: float = 0.1, 
        max_commands_per_combination: int = 4, 
        max_number_of_combinations: int | None = None) -> dict[str, list[str]]:
    instructions = {}

    commands_combinations = []
    commands_combinations.extend(list(commands.keys()))

    # add combinations of commands
    if request_commands_combinations:
        print("\n\nAdding combinations of commands...")
        combinations_ = get_commands_combinations(
            commands, max_commands_per_combination=max_commands_per_combination,
        )
        shuffle(combinations_)

        num_of_elements_to_keep = int(ceil(combinations_percentage_to_use * len(combinations_)))
        # add combinations as strings
        commands_combinations.extend(
            [
                combination_to_str(combination)
                for combination in combinations_[:num_of_elements_to_keep]
            ]
        )

        del combinations_
    
    if max_number_of_combinations is not None:
        commands_combinations = commands_combinations[:max_number_of_combinations]

    print(f"\nNumber of combinations created: {len(commands_combinations)}")
    print(f"\nNumber of instructions that will be created: {len(commands_combinations) * iterations_per_combination}")

    print("\n\nAutogenerating instructions examples...")
    for commands_combination in tqdm(commands_combinations):
        print(f"\n\n~ ~ {commands_combination} ~ ~")
        instructions[commands_combination] = []

        for i in range(iterations_per_combination):
            print(f"\n- - Iteration: {i + 1} - -")

            while True:
                sleep(0.35)
                instruction = autogenerate_random_instruction_using_a_command(
                    model, commands, [commands_combination, ],
                )
                print(f"Generated: {instruction}")

                if wait_for_approval:
                    while True:
                        replace_ = input("Replace this instruction by generating other? [y/n]")
                        if replace_ in ["y", "n"]:
                            break
                        else:
                            print("Enter 'y' or 'n'.")

                    if replace_ == "n":
                        break
                else:
                    break

            instructions[commands_combination].append(instruction)

    return instructions

def generate_graphs_as_strings_for_instructions(model:str, commands: dict, 
        instructions: dict[str, list[str]], wait_for_approval: bool = False) \
        -> dict[str, list[str]]:
    graphs_as_strings = {}

    print(f"\n\nGenerating graphs strings for instructions...")
    for commands_combination in tqdm(instructions):
        print(f"\n\n~ ~ {commands_combination} ~ ~")
        graphs_as_strings[commands_combination] = []

        for i, instruction in enumerate(instructions[commands_combination]):
            print(f"\n- - Iteration: {i + 1} - -")

            while True:
                sleep(0.35)
                graph_as_str = recognize_instruction(instruction, model, commands).val
                print(f"Generated: {graph_as_str}")

                if wait_for_approval:
                    while True:
                        replace_ = input("Replace this graph by generating other? [y/n]")
                        if replace_ in ["y", "n"]:
                            break
                        else:
                            print("Enter 'y' or 'n'.")

                    if replace_ == "n":
                        break
                else:
                    break

            graphs_as_strings[commands_combination].append(graph_as_str)

    return graphs_as_strings

def autogenerate_fine_tuning_data(model: str, commands: dict, jsonl_file_path: str, 
        iteration_per_command: int = 1, wait_for_approval: bool = False,
        request_commands_combinations: bool = True,
        combinations_percentage_to_use: float = 0.1,
        max_commands_per_combination: int = 4,
        max_number_of_combinations: int | None = None):

    instructions = autogenerate_random_instructions(
        model, commands, iteration_per_command, wait_for_approval, 
        request_commands_combinations, combinations_percentage_to_use,
        max_commands_per_combination, max_number_of_combinations,
    )

    graphs_as_strings = generate_graphs_as_strings_for_instructions(
        model, commands, instructions, wait_for_approval,
    )

    file_path = Path(jsonl_file_path)
    assert file_path.parent.exists(), f"Container directory {str(file_path.parent)} for JSONL file does not exist."
    print(f"JSONL file will be created at: {str(file_path)}")

    print("\n\n~ ~ Saving fine-tuning examples as a JSONL file...")
    with open(file_path, "w+") as f:
        for command in tqdm(instructions):
            for instruction, graph_as_str in zip(instructions[command], graphs_as_strings[command]):
                # see https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset
                prompts_suffix = "\n\n###\n\n"
                add_to_completions_suffix = "###" # suffix is "]###"

                line = json.dumps({"prompt": f"{instruction}{prompts_suffix}", "completion": f" {graph_as_str}{add_to_completions_suffix}"})
                f.write(f"{line}\n")
        f.close()
    print("Saved!")
