import ast
import operator as op

from tools import Tool

_OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
        ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg, ast.FloorDiv: op.floordiv}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("only numbers and + - * / ** % // are allowed")


class Calculator(Tool):
    name = "calculator"
    description = "Evaluate an arithmetic expression exactly (never do maths in your head)."
    args_doc = '{"expression": "2 + 2 * 10"}'

    def execute(self, expression):
        return _eval(ast.parse(str(expression), mode="eval").body)
