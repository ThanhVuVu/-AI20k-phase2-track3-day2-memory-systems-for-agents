from typing import List, Dict, Any

class ShortTermMemory:
    """
    Stores the immediate N messages in memory for local context.
    Uses a sliding window approach.
    """
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self.messages: List[Dict[str, Any]] = []

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_messages(self) -> List[Dict[str, Any]]:
        return self.messages

    def clear(self):
        self.messages = []
