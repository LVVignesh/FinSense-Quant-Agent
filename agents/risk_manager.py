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
- Portfolio VAR limit: 5%.
- If limits exceeded: status must be POLICY_REJECT.
- If approved: output must contain 'APPROVED'.

Valid Statuses: SUCCESS, POLICY_REJECT
"""
        super().__init__("RiskManager", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Evaluate compliance for this recommendation: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        # Realistic mock for demo purposes
        if "POLICY_REJECT_DEMO" in query:
            return {
                "status": AgentStatus.POLICY_REJECT,
                "output": f"RISK_VIOLATION: Trade Value ($500k) > Limit (${MAX_NOTIONAL_VALUE}).",
                "confidence": 1.0,
                "reasoning": "Trade exceeds maximum allowable notional value per single ticker."
            }
        return {
            "status": AgentStatus.SUCCESS,
            "output": "COMPLIANCE_CHECK: PASSED. Trade is within VAR limits. APPROVED.",
            "confidence": 1.0,
            "reasoning": "Trade is compliant with portfolio risk management policy."
        }
