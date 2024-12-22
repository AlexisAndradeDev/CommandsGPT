CHAT_MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "o1-preview", "o1-mini"]

def model_exists(model_name: str) -> bool:
    return True

def understanding_level(model_name: str) -> int:
    """
    Returns an integer representing how well the model creates the graph. 
    """    
    if model_name in ["gpt-4", "gpt-4-turbo", "gpt-4o"]:
        level = 3
    elif model_name in ["gpt-3.5-turbo"]:
        level = 2
