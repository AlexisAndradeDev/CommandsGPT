import ast
import operator

# supported operations.
OPERATIONS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

def evaluate_expr(node):
    if isinstance(node, ast.Constant):
        return node.n
    elif isinstance(node, ast.BinOp):
        left = evaluate_expr(node.left)
        right = evaluate_expr(node.right)
        operator = OPERATIONS[type(node.op)]
        return operator(left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = evaluate_expr(node.operand)
        if isinstance(node.op, ast.USub):
            return -operand
        elif isinstance(node.op, ast.UAdd):
            return +operand
        else:
            raise TypeError("Unsupported unary operation.")
    else:
        raise TypeError("Unsupported operation.")

def safe_eval_math_expr(expression: str) -> int | float | complex:
    """
    Returns the result of a mathematical operation in a string.

    Example:
        >>> safe_eval("4 * (3 + 5) - 2")
        30
    """
    try:
        parsed_expr = ast.parse(expression, mode='eval')
    except SyntaxError:
        raise ValueError(f"Invalid expression: {expression}.")

    return evaluate_expr(parsed_expr.body)
