from typing import Callable

from .models import model_exists, CHAT_MODELS

class Config():
    def __init__(self, chat_model: str, commands: dict[str, dict], command_name_to_func: dict[str, Callable]):
        assert model_exists(chat_model), f"Model name must be one of: {CHAT_MODELS}"
        self.chat_model = chat_model
        self.commands = commands
        self.command_name_to_func = command_name_to_func
