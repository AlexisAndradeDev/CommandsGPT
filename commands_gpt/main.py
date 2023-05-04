from commands_gpt.instruction_recognition import recognize_instruction_and_create_graph
from commands_gpt.commands.graphs import Graph
from commands_gpt.config import Config
from custom_commands import commands, command_name_to_func

# Don't forget to add the essential commands to your commands dicts
# I recommend you to do so! They implement core logic to the model's thinking,
# like an IF command.
# If you already defined your own core logic commands (IF command, THINK command, etc.),
# then you are free not to use them.
from commands_gpt.commands.commands_funcs import add_essential_commands
add_essential_commands(commands, command_name_to_func)

chat_model = "gpt-4-0314"

config = Config(chat_model)

instruction = input("Enter your prompt: ")
graph = recognize_instruction_and_create_graph(
    instruction, config.chat_model, commands, command_name_to_func,
)
graph.execute_commands(config)