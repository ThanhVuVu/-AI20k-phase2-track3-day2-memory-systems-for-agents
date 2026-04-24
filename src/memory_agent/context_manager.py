import tiktoken
from typing import List, Dict, Any

class ContextManager:
    def __init__(self, model_name: str = "gpt-3.5-turbo", max_tokens: int = 4000):
        self.encoder = tiktoken.encoding_for_model(model_name)
        self.max_tokens = max_tokens
        self.threshold = 0.8 * max_tokens

    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))

    def manage(self, system_instruction: str, profile: Dict[str, Any], semantic: List[Dict[str, Any]], conversation: List[Dict[str, Any]]) -> str:
        """
        Implements 4-Level Priority Eviction:
        1. Priority 1 (Keep): System Instructions & Core User Preferences.
        2. Priority 2 (Keep): High-relevance semantic chunks from ChromaDB.
        3. Priority 3 (Trim): Middle-part of the current conversation buffer (sliding window).
        4. Priority 4 (Discard): Metadata and redundant system logs (implicitly handled by not including them).
        """
        
        # Priority 1: System & Profile
        p1_content = f"System: {system_instruction}\nUser Profile: {profile}"
        p1_tokens = self.count_tokens(p1_content)

        # Priority 2: Semantic Chunks
        p2_content = "Relevant past info:\n" + "\n".join([f"- {s['content']}" for s in semantic])
        p2_tokens = self.count_tokens(p2_content)

        # Priority 3: Conversation Buffer
        # We start with all messages and trim from the middle if needed
        conv_lines = [f"{m['role']}: {m['content']}" for m in conversation]
        
        total_tokens = p1_tokens + p2_tokens + self.count_tokens("\n".join(conv_lines))

        if total_tokens > self.threshold:
            # Need to trim Priority 3 (Conversation Buffer)
            while total_tokens > self.threshold and len(conv_lines) > 2:
                # Remove from middle: keep first (system/initial) and last (most recent)
                # In sliding window, we usually remove oldest, but prompt says "middle-part"
                # Let's remove the second message until only first and last remain
                conv_lines.pop(1)
                total_tokens = p1_tokens + p2_tokens + self.count_tokens("\n".join(conv_lines))

        return f"{p1_content}\n\n{p2_content}\n\nConversation:\n" + "\n".join(conv_lines)
