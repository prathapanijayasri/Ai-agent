from app.agent.tools.example_tool import CalculatorTool, CalculatorInput
import pytest

def test_calculator_tool_valid():
    tool = CalculatorTool()
    result = tool.execute("25 * 4")
    assert result == {"result": 100}

def test_calculator_tool_invalid():
    tool = CalculatorTool()
    result = tool.execute("25 *")
    assert "error" in result
