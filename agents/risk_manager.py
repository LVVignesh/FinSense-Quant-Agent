from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus
from config import MAX_NOTIONAL_VALUE

class RiskManager(BaseAgent):
    def __init__(self):
        super().__init__("RiskManager", "Deterministic Governance Component")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Pure Python Deterministic Governance. NO LLM INVOLVED."""
        last_output = context.get("last_result", {}).get("output", {})
        
        if not isinstance(last_output, dict) or "quantity" not in last_output or "price" not in last_output:
            return {
                "status": AgentStatus.DATA_ERROR,
                "output": last_output,
                "confidence": 0.0,
                "reasoning": "RiskManager requires structured dictionary input with 'quantity' and 'price'."
            }

        qty = float(last_output["quantity"])
        price = float(last_output["price"])
        total_value = qty * price
        
        if total_value > MAX_NOTIONAL_VALUE:
            return {
                "status": AgentStatus.POLICY_REJECT,
                "output": last_output,  # Pass the structured state perfectly untouched
                "confidence": 1.0,
                "reasoning": f"REJECTED: {qty} * ${price:.2f} = ${total_value:,.2f} > Limit (${MAX_NOTIONAL_VALUE:,.2f})"
            }
        else:
            return {
                "status": AgentStatus.SUCCESS,
                "output": last_output,  # Pass the structured state perfectly untouched
                "confidence": 1.0,
                "reasoning": f"APPROVED: {qty} * ${price:.2f} = ${total_value:,.2f} <= Limit (${MAX_NOTIONAL_VALUE:,.2f})"
            }

    def _mock_response(self, query: str) -> Dict[str, Any]:
        pass # Not used since we don't call the LLM anymore
