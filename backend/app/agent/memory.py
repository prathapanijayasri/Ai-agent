from typing import List
from .state import Message
from ..core.config import settings

class MemoryManager:
    def __init__(self, max_messages: int = None):
        self.max_messages = max_messages or settings.MAX_CONTEXT_MESSAGES
        self.messages: List[Message] = []

    def add_message(self, message: Message):
        self.messages.append(message)
        self._prune_history()

    def _prune_history(self):
        if len(self.messages) > self.max_messages:
            # Simple pruning: keep the newest max_messages
            # In a real system, we might summarize older messages
            self.messages = self.messages[-self.max_messages:]

    def get_context(self) -> List[Message]:
        return self.messages

    def get_gemini_history(self) -> list:
        history = []
        for msg in self.messages:
            if msg.role == "user":
                history.append({"role": "user", "parts": [{"text": msg.content}]})
            elif msg.role == "model":
                parts = []
                if msg.content:
                    parts.append({"text": msg.content})
                if msg.tool_call_id:
                    # Not perfectly aligned with google-genai history format yet, 
                    # but provides a placeholder for structured tool call history
                    pass
                if parts:
                    history.append({"role": "model", "parts": parts})
        return history
