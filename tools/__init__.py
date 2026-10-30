class Tool:
    """Base class for all tools."""
    name = "base_tool"
    description = "base tool"
    def run(self, *args, **kwargs):
        raise NotImplementedError("Tool must implement run()")

def build_tools():
    from .expense_auditor import ExpenseAuditorTool
    return {
        "expense_auditor": ExpenseAuditorTool()
    }