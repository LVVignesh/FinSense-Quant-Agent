from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus
from config import MAX_NOTIONAL_VALUE

class RiskManager(BaseAgent):
    def __init__(self):
        system_prompt = f"""You are a risk compliance officer.
Objective: Review trade recommendations against institutional risk limits.
Constraints:
- Max Notional per trade: ${MAX_NOTIONAL_VALUE}.
- Calculate Total Value = Quantity * Price.
- If Total Value > ${MAX_NOTIONAL_VALUE}, status MUST be POLICY_REJECT.
- If Total Value <= ${MAX_NOTIONAL_VALUE}, status MUST be SUCCESS and output contains 'APPROVED'.

Valid Statuses: SUCCESS, POLICY_REJECT
"""
        super().__init__("RiskManager", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Evaluate compliance for this trade: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        # Improved mock logic for the demo loop
        try:
            # Simple parsing for "1000 units at $175.50"
            if "1000 units" in query and "$175.50" in query:
                return {
                    "status": AgentStatus.POLICY_REJECT,
                    "output": f"REJECTED: EXCEEDS LIMIT. Value ($175,500) > Limit (${MAX_NOTIONAL_VALUE}).",
                    "confidence": 1.0,
                    "reasoning": "Trade size exceeds the $150k notional limit per ticker."
                }
            if "500 units" in query:
                return {
                    "status": AgentStatus.SUCCESS,
                    "output": "COMPLIANCE_CHECK: PASSED. Value (~$87,750) is within limits. APPROVED.",
                    "confidence": 1.0,
                    "reasoning": "Downsized trade is now compliant with institutional risk policy."
                }
        except:
            pass
            
        return {
            "status": AgentStatus.SUCCESS,
            "output": "APPROVED",
            "confidence": 1.0,
            "reasoning": "Trade appears within generic safety limits."
        }
