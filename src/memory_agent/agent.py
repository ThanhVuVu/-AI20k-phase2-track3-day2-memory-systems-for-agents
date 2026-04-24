from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from .memory_manager import MemoryManager
from .context_manager import ContextManager
import openai
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger("MemoryAgent")
load_dotenv()

class MemoryState(TypedDict):
    query: str
    messages: List[Dict[str, Any]]
    user_profile: Dict[str, Any]
    episodes: List[Dict[str, Any]]
    semantic_hits: List[Dict[str, Any]]
    response: str
    memory_manager: MemoryManager
    context_manager: ContextManager

def retrieve_memory_node(state: MemoryState):
    mm = state["memory_manager"]
    query = state["query"]
    
    context = mm.get_context(query)
    logger.info(f"Retrieved Context: Profile Keys={list(context['long_term'].keys())}, Semantic Hits={len(context['semantic'])}, Episodes={len(context['episodic'])}")
    
    return {
        "user_profile": context["long_term"],
        "episodes": context["episodic"],
        "semantic_hits": context["semantic"],
        "messages": context["short_term"]
    }

def generate_response_node(state: MemoryState):
    cm = state["context_manager"]
    mm = state["memory_manager"]
    
    system_instruction = "You are a helpful AI assistant with multi-layered memory. Use the provided context to answer the user."
    
    # Context Management (Auto-trimming & Priority Eviction)
    prompt = cm.manage(
        system_instruction=system_instruction,
        profile=state["user_profile"],
        semantic=state["semantic_hits"],
        conversation=state["messages"]
    )
    logger.info(f"Final Managed Prompt Length: {len(prompt)} chars")
    
    # Call LLM
    try:
        # Using NVIDIA NIM (OpenAI-compatible)
        client = openai.OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        )
        response = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": state["query"]}
            ]
        ).choices[0].message.content
    except Exception as e:
        response = f"[NVIDIA NIM Mock Response for: {state['query']}] Based on your context, I'm processing your request. (Error: {str(e)})"
    
    # Store in memory
    mm.store_interaction(state["query"], response)
    
    # Check for profile updates (simplified logic)
    query_lower = state["query"].lower()
    if any(word in query_lower for word in ["dị ứng", "allergy", "tên tôi là", "tên là", "sở thích là"]):
        import re
        # Name extraction
        name_match = re.search(r"(?:tên tôi là|tên là)\s*([^.]+)", query_lower)
        if name_match:
            mm.update_user_profile({"name": name_match.group(1).strip()})
        
        # Allergy extraction
        allergy_match = re.search(r"(?:dị ứng|allergy)\s*(?:là|is)?\s*([^.]+)", query_lower)
        if allergy_match:
            mm.update_user_profile({"allergy": allergy_match.group(1).strip()})
        
        # Hobby extraction
        hobby_match = re.search(r"(?:sở thích là)\s*([^.]+)", query_lower)
        if hobby_match:
            mm.update_user_profile({"hobby": hobby_match.group(1).strip()})

    return {"response": response}

def create_memory_agent():
    workflow = StateGraph(MemoryState)
    
    workflow.add_node("retrieve_memory", retrieve_memory_node)
    workflow.add_node("generate_response", generate_response_node)
    
    workflow.set_entry_point("retrieve_memory")
    workflow.add_edge("retrieve_memory", "generate_response")
    workflow.add_edge("generate_response", END)
    
    return workflow.compile()

class AgentExecutor:
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.context_manager = ContextManager()
        self.agent = create_memory_agent()

    def run(self, query: str):
        initial_state = {
            "query": query,
            "messages": [],
            "user_profile": {},
            "episodes": [],
            "semantic_hits": [],
            "response": "",
            "memory_manager": self.memory_manager,
            "context_manager": self.context_manager
        }
        result = self.agent.invoke(initial_state)
        return result["response"]
