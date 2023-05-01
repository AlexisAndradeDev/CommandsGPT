from commands_gpt.modules.instruction_recognition import recognize_instruction_and_create_graph
from commands_gpt.modules.commands.graphs import execute_commands
from commands_gpt.modules.config import Config

config = Config("gpt-4-0314")

instruction = input("Enter your prompt: ")
graph, graph_data = recognize_instruction_and_create_graph(instruction, config.chat_model)
execute_commands(config, graph, graph_data)