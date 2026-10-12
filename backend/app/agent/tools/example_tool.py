from pydantic import BaseModel, Field
from ..registry import BaseTool, registry

class CalculatorInput(BaseModel):
    expression: str = Field(..., description="The mathematical expression to evaluate, e.g., '25 * 4'")

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Evaluates a mathematical expression and returns the result."
    input_schema = CalculatorInput

    def execute(self, expression: str, **kwargs) -> dict:
        try:
            # Safely evaluate mathematical expressions using built-in eval with restrictions
            # For a real production app, use a safer math parsing library.
            allowed_names = {"__builtins__": None}
            result = eval(expression, allowed_names, {})
            return {"result": result}
        except Exception as e:
            return {"error": f"Failed to evaluate expression: {str(e)}"}

calculator_tool = CalculatorTool()
registry.register(calculator_tool)
