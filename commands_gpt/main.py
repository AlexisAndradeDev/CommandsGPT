from commands_gpt.recognizers import ComplexRecognizer
from commands_gpt.commands.graphs import Graph
from commands_gpt.config import Config
from custom_commands import commands, command_name_to_func

# Don't forget to add the essential commands to your commands dicts
# I recommend you to do so! They implement core logic to the model's thinking,
# like an IF command.
# If you already defined your own core logic commands (IF command, THINK command, etc.),
# then you are free not to use them.
# Also, if you are using a SingleRecognizer, it might be better not to
# use the essential commands, as they probably wouldn't be necessary
from commands_gpt.commands.commands_funcs import add_essential_commands
add_essential_commands(commands, command_name_to_func)

chat_model = "o1-preview"

config = Config(chat_model, verbosity=2, explain_graph=False, save_graph_as_file=False)

instruction = input("Enter your prompt: ")

recognizer = ComplexRecognizer(config, commands, command_name_to_func)

commands_data_str = recognizer.recognize(instruction)
graph = Graph(recognizer, commands_data_str)
graph.execute_commands(config)