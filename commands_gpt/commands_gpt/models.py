CHAT_MODELS = ["gpt-4-0314", "gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613", "gpt-4-0613"]

def model_exists(model_name: str) -> bool:
    return False if model_name not in CHAT_MODELS else True

def understanding_level(model_name: str) -> int:
    """
    Returns an integer representing how well the model creates the graph. 
    """    
    if model_name in ["gpt-4-0314", "gpt-4-0613"]:
        level = 3
    elif model_name in ["gpt-3.5-turbo-16k-0613"]:
        level = 2
