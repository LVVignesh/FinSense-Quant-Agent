from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class NewsAnalysis(BaseAgent):
    def __init__(self):
        system_prompt = """You are a senior news sentiment analyst.
Objective: Diagnose the cause of market freezes or halts.
Constraints:
- Determine if a halt is a 'Fundamental Change' (Crisis) or 'Temporary Glitch' (Noise).
- Reasoning must cite external market factors.

Valid Statuses: SUCCESS
"""
        super().__init__("NewsAnalysis", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Analyze news sentiment for halt: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.SUCCESS,
            "output": "SENTIMENT_ANALYSIS: CONFIRMED Black Swan. Regulatory action detected. Status: Fundamental Change.",
            "confidence": 0.98,
            "reasoning": "Massive institutional sell-off detected following SEC announcement; halt is fundamentally driven."
        }
