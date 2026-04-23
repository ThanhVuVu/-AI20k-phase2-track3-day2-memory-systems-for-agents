from __future__ import annotations
import os
import time
import json
from typing import Any, Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv
from .schemas import JudgeResult, QAExample, ReflectionEntry
from .utils import normalize_answer

load_dotenv()

# Cấu hình NVIDIA API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)
MODEL = "meta/llama-3.1-8b-instruct"

def call_llm(system_prompt: str, user_prompt: str, response_format: Optional[Dict] = None) -> Dict[str, Any]:
    start_time = time.time()
    
    extra_args = {}
    if response_format:
        extra_args["response_format"] = response_format

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        **extra_args
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    return {
        "content": response.choices[0].message.content,
        "tokens": response.usage.total_tokens,
        "latency": latency_ms
    }

def actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> Dict[str, Any]:
    from .prompts import ACTOR_SYSTEM
    
    context_str = "\n".join([f"Title: {c.title}\nText: {c.text}" for c in example.context])
    reflections = "\n".join([f"- {r}" for r in reflection_memory])
    
    user_prompt = f"Question: {example.question}\n\nContext:\n{context_str}\n\n"
    if agent_type == "reflexion" and reflection_memory:
        user_prompt += f"Previous Reflections:\n{reflections}\n\nPlease use the feedback above to improve your answer."
    
    return call_llm(ACTOR_SYSTEM, user_prompt)

def evaluator(example: QAExample, answer: str) -> Dict[str, Any]:
    from .prompts import EVALUATOR_SYSTEM
    
    user_prompt = f"Question: {example.question}\nCorrect Answer: {example.gold_answer}\nAgent Answer: {answer}"
    
    result = call_llm(EVALUATOR_SYSTEM, user_prompt, response_format={"type": "json_object"})
    
    try:
        content = json.loads(result["content"])
        # Xử lý nếu LLM trả về nhiều lỗi (lấy cái đầu tiên) và xóa khoảng trắng
        raw_mode = content.get("failure_mode", "wrong_final_answer")
        clean_mode = str(raw_mode).split(",")[0].strip()
        
        result["judge"] = JudgeResult(
            score=content.get("score", 0),
            reason=content.get("reason", "N/A"),
            failure_mode=clean_mode,
            missing_evidence=content.get("missing_evidence", []),
            spurious_claims=content.get("spurious_claims", [])
        )
    except:
        # Fallback to simple normalization if JSON fails
        score = 1 if normalize_answer(example.gold_answer) == normalize_answer(answer) else 0
        result["judge"] = JudgeResult(score=score, reason="Fallback evaluation due to JSON parsing error")
        
    return result

def reflector(example: QAExample, attempt_id: int, judge: JudgeResult) -> Dict[str, Any]:
    from .prompts import REFLECTOR_SYSTEM
    
    user_prompt = f"Question: {example.question}\nFailure Reason: {judge.reason}\nMissing Evidence: {judge.missing_evidence}"
    
    result = call_llm(REFLECTOR_SYSTEM, user_prompt, response_format={"type": "json_object"})
    
    try:
        content = json.loads(result["content"])
        result["reflection"] = ReflectionEntry(
            attempt_id=attempt_id,
            failure_reason=judge.reason,
            lesson=content.get("lesson", "N/A"),
            next_strategy=content.get("next_strategy", "N/A")
        )
    except:
        result["reflection"] = ReflectionEntry(
            attempt_id=attempt_id,
            failure_reason=judge.reason,
            lesson="Analyze failure and retry",
            next_strategy="Retry with more focus"
        )
        
    return result
