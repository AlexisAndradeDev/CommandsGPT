from .models import model_exists, CHAT_MODELS

VERBOSITY_LEVELS = [0, 1, 2]

class Config():
    def __init__(self, chat_model: str, verbosity: int = 1):
        assert model_exists(chat_model), f"Model name must be one of: {CHAT_MODELS}"
        self.chat_model = chat_model
        assert verbosity in VERBOSITY_LEVELS, f"Verbosity must be one of: {VERBOSITY_LEVELS}"
        self.verbosity = verbosity
