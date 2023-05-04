from .models import model_exists, CHAT_MODELS

class Config():
    def __init__(self, chat_model: str):
        assert model_exists(chat_model), f"Model name must be one of: {CHAT_MODELS}"
        self.chat_model = chat_model
