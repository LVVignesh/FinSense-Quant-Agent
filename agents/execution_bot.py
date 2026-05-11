from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class ExecutionBot(BaseAgent):
    def __init__(self):
        system_prompt = """You are a senior execution trader. 
Objective: Execute authorized trades and update internal portfolio ledgers.
Constraints:
- Only execute if trade status is 'APPROVED' or 'AUTHORIZED'.
- Return detailed order fill statistics.

Valid Statuses: SUCCESS
"""
        super().__init__("ExecutionBot", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Execute order fill for: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.SUCCESS,
            "output": "ORDER_FILL: Market Buy Executed. Route: SMART. Fill Price: $175.52. Latency: 14ms.",
            "confidence": 1.0,
            "reasoning": "Order successfully routed to electronic exchange and confirmed."
        }
