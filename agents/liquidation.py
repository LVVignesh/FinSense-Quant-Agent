from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class Liquidation(BaseAgent):
    def __init__(self):
        system_prompt = """You are an emergency liquidation bot.
Objective: Rapidly exit high-risk positions during confirmed market crises.
Constraints:
- Execute market sell orders for all affected assets.
- Output 'EMERGENCY_LIQUIDATION' and status.

Valid Statuses: SUCCESS
"""
        super().__init__("Liquidation", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Liquidate high-risk positions: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.SUCCESS,
            "output": "EMERGENCY_LIQUIDATION: All positions closed at market. Portfolio de-risked.",
            "confidence": 1.0,
            "reasoning": "Urgent liquidation triggered by fundamental crisis confirmation from News Agent."
        }
