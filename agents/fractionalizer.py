from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class Fractionalizer(BaseAgent):
    def __init__(self):
        system_prompt = """You are a trade optimization agent (Fractionalizer).
Objective: Optimize rejected trade sizes by reducing the quantity while keeping the action (BUY/SELL).

Constraints:
- Mathematically reduce the quantity (e.g., divide by 2).
- You MUST maintain the original action (If original was SELL, keep it SELL).
- You MUST maintain the Price in your output.
- Status must be SUCCESS.

Valid Statuses: SUCCESS
"""
        super().__init__("Fractionalizer", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Optimize this rejected trade size. Keep the same action (BUY/SELL) but reduce quantity: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        # Handle SELL or BUY in mock
        action = "SELL" if "SELL" in query else "BUY"
        return {
            "status": AgentStatus.SUCCESS,
            "output": f"ALGO_OPTIMIZATION: Size reduced. NEW REC: {action} 500 units at $175.50.",
            "confidence": 1.0,
            "reasoning": f"Reducing {action} size by 50% to satisfy institutional risk constraints while maintaining direction."
        }
