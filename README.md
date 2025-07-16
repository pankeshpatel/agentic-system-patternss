# agentic-system-patterns

### pattern 1

 -  a planner sent the same question to multiple agents, and a judge assessed their responses to evaluate agent intelligence.
 -  It sends a same question to multiple large language models (LLMs), then using a separate “judge” agent to evaluate and rank their responses. 
   This approach is valuable for identifying the single best answer among many, leveraging the strengths of ensemble reasoning and critical evaluation.












### setup



- `uv sync/uv init -n`
-  `uv run python3 pattern1.py `


### Resources

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
