from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus
import copy

class Fractionalizer(BaseAgent):
    def __init__(self):
        super().__init__("Fractionalizer", "Deterministic Optimization Component")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Pure Python Deterministic Fractionalization. NO LLM INVOLVED."""
        last_output = context.get("last_result", {}).get("output", {})
        
        if not isinstance(last_output, dict) or "quantity" not in last_output:
            return {
                "status": AgentStatus.DATA_ERROR,
                "output": last_output,
                "confidence": 0.0,
                "reasoning": "Fractionalizer requires structured dictionary input with 'quantity'."
            }

        # Create a deep copy to mutate the state
        new_state = copy.deepcopy(last_output)
        
        # Mathematically reduce quantity by 50%
        old_qty = new_state["quantity"]
        new_qty = int(old_qty * 0.5)
        new_state["quantity"] = new_qty
        
        return {
            "status": AgentStatus.SUCCESS,
            "output": new_state,
            "confidence": 1.0,
            "reasoning": f"PYTHON_OPTIMIZATION: Reduced quantity from {old_qty} to {new_qty} to satisfy risk constraints."
        }

    def _mock_response(self, query: str) -> Dict[str, Any]:
        pass # Not used since we don't call the LLM anymore
