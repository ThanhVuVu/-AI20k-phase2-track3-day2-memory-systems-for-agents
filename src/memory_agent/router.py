import re
from typing import List

class MemoryRouter:
    """
    Analyzes user input to decide which memory layers to query.
    """
    def route(self, query: str) -> List[str]:
        query_lower = query.lower()
        targets = ["short-term"] # Always include short-term for context

        # User Preference -> Redis (Long-term)
        if any(word in query_lower for word in ["like", "prefer", "want", "favorite", "hobby", "format", "style", "allergy", "tên", "thích", "muốn", "sở thích", "dị ứng"]):
            targets.append("long-term")
        
        # Factual Recall -> ChromaDB (Semantic)
        if any(word in query_lower for word in ["what", "when", "where", "discuss", "project", "details", "remember", "fact", "là gì", "khi nào", "ở đâu", "thảo luận", "dự án", "chi tiết", "nhớ"]):
            targets.append("semantic")
        
        # Experience/Process Recall -> JSON (Episodic)
        if any(word in query_lower for word in ["how did we", "last time", "previous", "experience", "solve", "process", "error", "làm thế nào", "lần trước", "trước đây", "kinh nghiệm", "giải quyết", "quy trình", "lỗi"]):
            targets.append("episodic")

        # Deduplicate while preserving order
        seen = set()
        return [x for x in targets if not (x in seen or seen.add(x))]
