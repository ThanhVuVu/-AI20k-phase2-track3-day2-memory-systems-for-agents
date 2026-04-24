# Multi-Layered AI Memory System for LangGraph Agents

This repository implements a sophisticated memory management system for LLM agents using LangGraph.

## Architecture

1.  **Memory Manager**: Orchestrates 4 layers of memory.
    *   **Short-term**: Local context buffer (sliding window).
    *   **Long-term**: User profiles and preferences (KV store/Redis-like).
    *   **Episodic**: past task sessions (JSON Logs).
    *   **Semantic**: Vector search for factual recall (ChromaDB).
2.  **Memory Router**: Intent-based routing to select appropriate memory layers based on query analysis.
3.  **Context Manager**: Automated token counting and priority-based eviction (4 levels).
4.  **LangGraph Agent**: A modular graph-based agent that integrates memory retrieval and generation.

## Project Structure

```
src/memory_agent/
├── backends/          # Storage implementations
│   ├── short_term.py
│   ├── long_term.py
│   ├── episodic.py
│   └── semantic.py
├── agent.py           # LangGraph implementation
├── benchmark.py       # Evaluation suite
├── context_manager.py # Token management
├── memory_manager.py  # Orchestrator
└── router.py          # Intent logic
run_benchmark.py       # Main entry point
report.md              # Detailed benchmark report
BENCHMARK.md           # Rubric-required benchmark data
```

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Set your NVIDIA API Key:
    ```bash
    # Create a .env file or export the variable
    NVIDIA_API_KEY='your-nvda-key-here'
    ```
3.  Run the benchmark:
    ```bash
    python run_benchmark.py
    ```

## Evaluation

The system uses `meta/llama-3.1-8b-instruct` via NVIDIA NIM for both generation and benchmarking (LLM-as-a-judge).
