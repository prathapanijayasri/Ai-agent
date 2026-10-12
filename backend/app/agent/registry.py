import json
from typing import Callable, Dict, Type, Any
from pydantic import BaseModel
import inspect

class BaseTool:
    name: str
    description: str
    input_schema: Type[BaseModel]

    def execute(self, **kwargs) -> Any:
        raise NotImplementedError("Tool must implement execute method")

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry.")
        return self._tools[name]

    def get_all_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_gemini_tools(self) -> list[Dict[str, Any]]:
        gemini_tools = []
        for tool in self._tools.values():
            schema = tool.input_schema.model_json_schema()
            
            gemini_tools.append({
                "function_declarations": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "OBJECT",
                            "properties": schema.get("properties", {}),
                            "required": schema.get("required", [])
                        }
                    }
                ]
            })
        return gemini_tools

registry = ToolRegistry()
