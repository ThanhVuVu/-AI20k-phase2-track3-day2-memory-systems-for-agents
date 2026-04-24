import json
import os
from datetime import datetime
from typing import List, Dict, Any

class EpisodicMemory:
    """
    Structured append-only JSON file capturing complete "episodes".
    """
    def __init__(self, storage_path: str = "data/memory/episodes.jsonl"):
        self.storage_path = storage_path

    def add_episode(self, task: str, interactions: List[Dict[str, Any]], outcome: str):
        episode = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "interactions": interactions,
            "outcome": outcome
        }
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(episode, ensure_ascii=False) + "\n")

    def search_episodes(self, query: str) -> List[Dict[str, Any]]:
        """
        Simple keyword search over past episodes.
        """
        results = []
        if not os.path.exists(self.storage_path):
            return results
        
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            for line in f:
                episode = json.loads(line)
                if query.lower() in episode["task"].lower() or any(query.lower() in i["content"].lower() for i in episode["interactions"]):
                    results.append(episode)
        return results[-3:] # Return last 3 relevant episodes
