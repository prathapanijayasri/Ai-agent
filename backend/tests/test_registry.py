import pytest
from app.agent.registry import ToolRegistry, BaseTool
from pydantic import BaseModel

class DummyInput(BaseModel):
    test_arg: str

class DummyTool(BaseTool):
    name = "dummy"
    description = "A dummy tool."
    input_schema = DummyInput
    
    def execute(self, test_arg: str, **kwargs):
        return {"result": test_arg}

def test_registry():
    registry = ToolRegistry()
    tool = DummyTool()
    registry.register(tool)
    
    assert registry.get_tool("dummy") == tool
    
    with pytest.raises(ValueError):
        registry.get_tool("missing_tool")

    gemini_schema = registry.get_gemini_tools()
    assert len(gemini_schema) == 1
    assert gemini_schema[0]["function_declarations"][0]["name"] == "dummy"
