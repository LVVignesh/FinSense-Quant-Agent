from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class Fractionalizer(BaseAgent):
    def __init__(self):
        system_prompt = """You are a trade optimization agent (Fractionalizer).
Objective: Optimize rejected trade sizes to bypass risk policy violations.
Constraints:
- Mathematically reduce the quantity of the trade (e.g., from 1000 units to 500 units).
- You MUST maintain the Price in your output (e.g., "BUY 500 units at $175.50").
- Status must be SUCCESS.

Valid Statuses: SUCCESS
"""
        super().__init__("Fractionalizer", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Optimize this rejected trade size: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.SUCCESS,
            "output": "ALGO_OPTIMIZATION: Size reduced. NEW REC: BUY 500 units at $175.50.",
            "confidence": 1.0,
            "reasoning": "Downsizing position by 50% to fit within institutional notional value limits."
        }
