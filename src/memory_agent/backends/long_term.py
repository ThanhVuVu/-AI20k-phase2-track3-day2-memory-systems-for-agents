import json
import os
from typing import Dict, Any

class LongTermMemory:
    """
    Persistent key-value storage for user profile and preferences.
    Simulates Redis using a local JSON file.
    """
    def __init__(self, storage_path: str = "data/memory/long_term.json"):
        self.storage_path = storage_path
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def set(self, key: str, value: Any):
        self.data[key] = value
        self._save()

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def update_profile(self, updates: Dict[str, Any]):
        """
        Updates user profile with conflict handling (new values override old ones).
        """
        if "profile" not in self.data:
            self.data["profile"] = {}
        
        self.data["profile"].update(updates)
        self._save()

    def get_profile(self) -> Dict[str, Any]:
        return self.data.get("profile", {})
