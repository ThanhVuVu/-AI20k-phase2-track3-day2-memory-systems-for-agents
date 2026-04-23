from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from .mock_runtime import actor_answer, evaluator, reflector
from .schemas import AttemptTrace, QAExample, ReflectionEntry, RunRecord

@dataclass
class BaseAgent:
    agent_type: Literal["react", "reflexion"]
    max_attempts: int = 1
    def run(self, example: QAExample) -> RunRecord:
        reflection_memory: list[str] = []
        reflections: list[ReflectionEntry] = []
        traces: list[AttemptTrace] = []
        final_answer = ""
        final_score = 0
        for attempt_id in range(1, self.max_attempts + 1):
            print(f"  [Attempt {attempt_id}] Processing QID: {example.qid} ({self.agent_type})...", end="\r")
            # 1. Actor: Lấy câu trả lời
            actor_res = actor_answer(example, attempt_id, self.agent_type, reflection_memory)
            answer = actor_res["content"]
            
            # 2. Evaluator: Đánh giá câu trả lời
            eval_res = evaluator(example, answer)
            judge = eval_res["judge"]
            
            # Tính toán Token và Latency thực tế
            token_estimate = actor_res["tokens"] + eval_res["tokens"]
            latency_ms = actor_res["latency"] + eval_res["latency"]
            
            trace = AttemptTrace(
                attempt_id=attempt_id, 
                answer=answer, 
                score=judge.score, 
                reason=judge.reason, 
                token_estimate=token_estimate, 
                latency_ms=latency_ms
            )
            
            final_answer = answer
            final_score = judge.score
            traces.append(trace)
            
            if judge.score == 1:
                break
            
            # 3. Reflexion logic: Chỉ thực hiện nếu agent_type là 'reflexion' và còn lượt thử
            if self.agent_type == "reflexion" and attempt_id < self.max_attempts:
                refl_res = reflector(example, attempt_id, judge)
                reflection_obj = refl_res["reflection"]
                
                # Cập nhật thông tin cho trace và memory
                reflections.append(reflection_obj)
                reflection_memory.append(f"Attempt {attempt_id} Error: {reflection_obj.lesson}. Strategy: {reflection_obj.next_strategy}")
                
                # Cộng dồn token/latency của reflector vào trace hiện tại
                trace.token_estimate += refl_res["tokens"]
                trace.latency_ms += refl_res["latency"]

        total_tokens = sum(t.token_estimate for t in traces)
        total_latency = sum(t.latency_ms for t in traces)
        
        # Lấy failure_mode từ kết quả judge của attempt cuối cùng
        failure_mode = "none" if final_score == 1 else judge.failure_mode
        
        status = "[green]PASS[/green]" if final_score == 1 else "[red]FAIL[/red]"
        print(f"  QID: {example.qid} | Result: {status} | Attempts: {len(traces)} | Tokens: {total_tokens}")
        
        return RunRecord(
            qid=example.qid, 
            question=example.question, 
            gold_answer=example.gold_answer, 
            agent_type=self.agent_type, 
            predicted_answer=final_answer, 
            is_correct=bool(final_score), 
            attempts=len(traces), 
            token_estimate=total_tokens, 
            latency_ms=total_latency, 
            failure_mode=failure_mode, 
            reflections=reflections, 
            traces=traces
        )

class ReActAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="react", max_attempts=1)

class ReflexionAgent(BaseAgent):
    def __init__(self, max_attempts: int = 3) -> None:
        super().__init__(agent_type="reflexion", max_attempts=max_attempts)
