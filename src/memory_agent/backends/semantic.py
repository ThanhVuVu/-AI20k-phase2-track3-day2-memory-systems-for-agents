import chromadb
from chromadb.utils import embedding_functions
import os
from typing import List, Dict, Any

class SemanticMemory:
    """
    Vector database to store and retrieve embeddings of past interactions.
    """
    def __init__(self, storage_path: str = "data/memory/chroma"):
        self.client = chromadb.PersistentClient(path=storage_path)
        # Using default embedding function (sentence-transformers/all-MiniLM-L6-v2)
        # or can use OpenAI if API key is provided
        self.collection = self.client.get_or_create_collection(name="interactions")

    def add_interaction(self, content: str, metadata: Dict[str, Any] = None):
        meta = metadata or {"type": "interaction"}
        self.collection.add(
            documents=[content],
            metadatas=[meta],
            ids=[str(self.collection.count() + 1)]
        )

    def search(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        formatted_results = []
        if results['documents']:
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                formatted_results.append({"content": doc, "metadata": meta})
        return formatted_results

    def clear(self):
        self.client.delete_collection(name="interactions")
        self.collection = self.client.get_or_create_collection(name="interactions")
