from .models import model_exists, CHAT_MODELS

VERBOSITY_LEVELS = [0, 1, 2]

class Config():
    def __init__(self, chat_model: str, verbosity: int = 1, explain_graph: bool = True,
            save_graph_as_file: bool = False):
        assert model_exists(chat_model), f"Model name must be one of: {CHAT_MODELS}"
        self.chat_model = chat_model
        assert verbosity in VERBOSITY_LEVELS, f"Verbosity must be one of: {VERBOSITY_LEVELS}"
        self.verbosity = verbosity
        assert type(explain_graph) is bool, f"Explain graph flag must be boolean type."
        self.explain_graph = explain_graph
        assert type(save_graph_as_file) is bool, f"Save graph as file flag must be boolean type."
        self.save_graph_as_file = save_graph_as_file

        if verbosity >= 1:
            print(f"Verbosity set to {verbosity}.")
