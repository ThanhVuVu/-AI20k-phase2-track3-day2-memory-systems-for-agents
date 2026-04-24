from .backends.short_term import ShortTermMemory
from .backends.long_term import LongTermMemory
from .backends.episodic import EpisodicMemory
from .backends.semantic import SemanticMemory
from .router import MemoryRouter
from typing import Dict, Any, List

class MemoryManager:
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.router = MemoryRouter()

    def get_context(self, query: str) -> Dict[str, Any]:
        targets = self.router.route(query)
        context = {
            "short_term": self.short_term.get_messages(),
            "long_term": {},
            "episodic": [],
            "semantic": []
        }

        if "long_term" in targets:
            context["long_term"] = self.long_term.get_profile()
        
        if "episodic" in targets:
            context["episodic"] = self.episodic.search_episodes(query)
        
        if "semantic" in targets:
            context["semantic"] = self.semantic.search(query)

        return context

    def store_interaction(self, query: str, response: str):
        # Store in short-term
        self.short_term.add_message("user", query)
        self.short_term.add_message("assistant", response)
        
        # Store in semantic
        self.semantic.add_interaction(f"User: {query}\nAssistant: {response}")

    def store_episode(self, task: str, interactions: List[Dict[str, Any]], outcome: str):
        self.episodic.add_episode(task, interactions, outcome)

    def update_user_profile(self, updates: Dict[str, Any]):
        self.long_term.update_profile(updates)
