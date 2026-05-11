from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class Fractionalizer(BaseAgent):
    def __init__(self):
        system_prompt = """You are a trade optimization agent (Fractionalizer).
Objective: Optimize rejected trade sizes to bypass risk policy violations.
Constraints:
- Mathematically reduce notional size until compliant.
- Output 'RE-CALCULATED' and the new target size.

Valid Statuses: SUCCESS
"""
        super().__init__("Fractionalizer", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Optimize trade size for: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.SUCCESS,
            "output": "ALGO_OPTIMIZATION: Input size $500k reduced to $125k (25%). Status: RE-CALCULATED.",
            "confidence": 1.0,
            "reasoning": "Downsizing position to fit within daily allocation limits while maintaining exposure."
        }
