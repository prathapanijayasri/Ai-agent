from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    role: str # "user", "model", "tool"
    content: str
    name: Optional[str] = None # Name of the tool if role is "tool"
    tool_call_id: Optional[str] = None # Used to link tool results

class AgentState(BaseModel):
    conversation_id: str
    messages: List[Message] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
