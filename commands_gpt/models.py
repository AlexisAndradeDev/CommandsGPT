CHAT_MODELS = ["gpt-4-0314", "gpt-3.5-turbo"]

def model_exists(model_name: str):
    return False if model_name not in CHAT_MODELS else True