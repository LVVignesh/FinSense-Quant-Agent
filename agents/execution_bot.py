from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus
import uuid

class ExecutionBot(BaseAgent):
    def __init__(self):
        super().__init__("ExecutionBot", "Deterministic Execution Component")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Pure Python Execution Logic. NO LLM INVOLVED."""
        # Get the approved state from the RiskManager (which is the last history entry)
        history = context.get("history", [])
        if not history:
            return self._error_response("No history provided.")
            
        last_result = history[-1]
        
        # Verify it was approved by RiskManager
        if last_result.get("status") != AgentStatus.SUCCESS:
            return self._error_response("Trade was not approved by RiskManager.")
            
        trade_details = last_result.get("output", {})
        if not isinstance(trade_details, dict):
            return self._error_response("Invalid trade details format.")
            
        # Execute the trade
        action = trade_details.get("action", "UNKNOWN")
        quantity = trade_details.get("quantity", 0)
        price = trade_details.get("price", 0.0)
        ticker = context.get("ticker", "UNKNOWN")
        
        order_id = str(uuid.uuid4())[:8]
        
        return {
            "status": AgentStatus.SUCCESS,
            "output": {
                "order_fill": {
                    "status": "FILLED",
                    "order_id": order_id,
                    "symbol": ticker,
                    "action": action,
                    "quantity": quantity,
                    "price": price,
                    "total_value": quantity * price
                }
            },
            "confidence": 1.0,
            "reasoning": f"PYTHON_EXECUTION: Order {order_id} routed to SMART exchange. Filled {quantity} shares of {ticker} at ${price:.2f}."
        }
        
    def _error_response(self, reason: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.DATA_ERROR,
            "output": "EXECUTION_FAILED",
            "confidence": 0.0,
            "reasoning": reason
        }

    def _mock_response(self, query: str) -> Dict[str, Any]:
        pass
