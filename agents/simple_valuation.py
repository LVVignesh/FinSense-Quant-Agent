from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class SimpleValuation(BaseAgent):
    def __init__(self):
        system_prompt = """You are a high-speed heuristic valuation agent.
Objective: Provide a fast, secondary valuation recommendation when the primary agent is too slow.
Constraints:
- Use simplified P/E heuristics.
- Output 'FAST_VALUATION' and BUY/SELL recommendation.

Valid Statuses: SUCCESS
"""
        super().__init__("SimpleValuation", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Perform high-speed valuation for: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.SUCCESS,
            "output": "FAST_VALUATION: Heuristic check passed. REC: BUY.",
            "confidence": 0.75,
            "reasoning": "Fallback valuation confirms undervalued status using simplified sector heuristics."
        }
