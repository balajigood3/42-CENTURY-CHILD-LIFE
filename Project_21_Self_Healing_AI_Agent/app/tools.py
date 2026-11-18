from pathlib import Path
import ast
import operator
import re

class ToolError(Exception):
    pass

class SafeTools:
    """Allowlisted deterministic tools. File access is confined to workspace/."""
    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.allowed = {"calculator", "uppercase", "word_count", "read_file", "write_file"}

    def _safe_path(self, relative: str) -> Path:
        candidate = (self.workspace / relative).resolve()
        if candidate != self.workspace and self.workspace not in candidate.parents:
            raise ToolError("Path is outside the permitted workspace.")
        return candidate

    def call(self, name: str, **kwargs):
        if name not in self.allowed:
            raise ToolError(f"Tool '{name}' is not allowlisted.")
        if name == "calculator":
            return str(self._calculate(str(kwargs.get("expression", ""))))
        if name == "uppercase":
            return str(kwargs.get("text", "")).upper()
        if name == "word_count":
            return str(len(re.findall(r"\b\w+\b", str(kwargs.get("text", "")))))
        if name == "read_file":
            path = self._safe_path(str(kwargs.get("path", "")))
            if not path.is_file():
                raise ToolError("File does not exist.")
            return path.read_text(encoding="utf-8")
        if name == "write_file":
            path = self._safe_path(str(kwargs.get("path", "")))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(kwargs.get("content", "")), encoding="utf-8")
            return f"Wrote {path.relative_to(self.workspace)}"
        raise ToolError("Unsupported tool.")

    @staticmethod
    def _calculate(expression: str):
        # Parse only arithmetic expressions; never use eval().
        tree = ast.parse(expression, mode="eval")
        ops = {
            ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.Pow: operator.pow, ast.Mod: operator.mod,
            ast.USub: operator.neg, ast.UAdd: operator.pos,
        }
        def visit(node):
            if isinstance(node, ast.Expression):
                return visit(node.body)
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in ops:
                left, right = visit(node.left), visit(node.right)
                if isinstance(node.op, ast.Pow) and abs(right) > 8:
                    raise ToolError("Exponent is outside the safe limit.")
                return ops[type(node.op)](left, right)
            if isinstance(node, ast.UnaryOp) and type(node.op) in ops:
                return ops[type(node.op)](visit(node.operand))
            raise ToolError("Only basic arithmetic is allowed.")
        result = visit(tree)
        if abs(result) > 10**12:
            raise ToolError("Result exceeds the safe limit.")
        return result
