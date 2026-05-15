from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class NewsAnalysis(BaseAgent):
    def __init__(self):
        system_prompt = """You are a senior news sentiment analyst.
Objective: Diagnose the cause of a market freeze or halt.

STRICT OUTPUT RULE:
Your 'output' field MUST be a JSON object with EXACTLY these keys:
- "crisis_level": string — MUST be exactly "CRISIS" or "NOISE"
- "summary": string — one sentence explanation

Use "CRISIS" if the halt is caused by a fundamental event (bankruptcy, regulatory action, war, systemic failure).
Use "NOISE" if the halt is temporary and technical (glitch, brief volatility, maintenance).

STATUS FIELD RULE: Always use exactly 'SUCCESS'. Never use 'OK', 'ok', 'done', or any other value.

Example 'output': {"crisis_level": "CRISIS", "summary": "SEC regulatory action confirmed."}
"""
        super().__init__("NewsAnalysis", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Diagnose this market halt and classify as CRISIS or NOISE: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.SUCCESS,
            "output": {"crisis_level": "CRISIS", "summary": "SEC regulatory action confirmed. Systematic sell-off detected."},
            "confidence": 0.98,
            "reasoning": "Massive institutional sell-off following regulatory announcement. Fundamental change confirmed."
        }
