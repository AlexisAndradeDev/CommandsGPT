import tempfile
import os
import shutil
from pathlib import Path

from commands_gpt.fine_tuning import autogenerate_fine_tuning_data
from commands_gpt.commands.commands_funcs import add_essential_commands
from custom_commands import commands, command_name_to_func
add_essential_commands(commands, command_name_to_func)

trainer_model = "gpt-4-0314"
TEMP_ROOT_DIR = Path(tempfile.gettempdir())
TEMP_FOLDER = TEMP_ROOT_DIR / str(hash(os.times()))
os.makedirs(TEMP_FOLDER)

JSONL_PATH = TEMP_FOLDER / "fine_tuning.jsonl"
autogenerate_fine_tuning_data(
    trainer_model, commands, JSONL_PATH, iteration_per_command=3,
    wait_for_approval=False, request_commands_combinations=True,
    combinations_percentage_to_use=0.1, max_commands_per_combination=3,
    max_number_of_combinations=50,
)

# TODO: Fine-tune davinci model automatically

# recognition_model = "davinci"

# shutil.rmtree(TEMP_FOLDER)