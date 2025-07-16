# agentic-system-patternss

### pattern 1 - Orchestrator–Worker pattern
 -  a planner sent the same question to multiple agents, and a judge assessed their responses to evaluate agent intelligence.
 -  It sends a same question to multiple large language models (LLMs), then using a separate “judge” agent to evaluate and rank their responses. 
   This approach is valuable for identifying the single best answer among many, leveraging the strengths of ensemble reasoning and critical evaluation.










### setup



- `uv sync`
-  `uv run python3 pattern1.py `