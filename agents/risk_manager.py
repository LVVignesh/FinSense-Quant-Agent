from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus
from config import MAX_NOTIONAL_VALUE
import re

class RiskManager(BaseAgent):
    def __init__(self):
        system_prompt = f"""You are a senior risk compliance officer.
Objective: Review trade recommendations against institutional risk limits.

STRICT RULES:
1. MAX NOTIONAL: ${MAX_NOTIONAL_VALUE}.
2. CALCULATION: total_value = quantity * price.
3. If total_value > ${MAX_NOTIONAL_VALUE}, you MUST return POLICY_REJECT.
4. You must explicitly show your math in the reasoning field.

Valid Statuses: SUCCESS, POLICY_REJECT
"""
        super().__init__("RiskManager", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = str(context.get("last_result", {}).get("output", ""))
        
        # DETERMINISTIC PYTHON GUARDRAIL
        # Try to extract numbers to double check the AI
        try:
            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", last_output.replace(',', ''))
            if len(numbers) >= 2:
                qty = float(numbers[0])
                price = float(numbers[1])
                total_value = qty * price
                
                if total_value > MAX_NOTIONAL_VALUE:
                    return {
                        "status": AgentStatus.POLICY_REJECT,
                        "output": f"REJECTED: EXCEEDS LIMIT. Value (${total_value:,.2f}) > Limit (${MAX_NOTIONAL_VALUE:,.2f})",
                        "confidence": 1.0,
                        "reasoning": f"PYTHON_GUARDRAIL: Deterministic calculation confirmed violation. {qty} * {price} = {total_value:,.2f}."
                    }
        except Exception as e:
            print(f"DEBUG [RiskManager] Guardrail error: {str(e)}")

        return await self._call_llm(f"Evaluate compliance for this trade. Show your math explicitly: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        # Fallback mock logic
        if "1000 units" in query:
            return {
                "status": AgentStatus.POLICY_REJECT,
                "output": "REJECTED: EXCEEDS LIMIT",
                "confidence": 1.0,
                "reasoning": f"Value exceeds the ${MAX_NOTIONAL_VALUE} limit."
            }
        return {
            "status": AgentStatus.SUCCESS,
            "output": "COMPLIANCE_CHECK: PASSED. APPROVED.",
            "confidence": 1.0,
            "reasoning": "Trade size is within limits."
        }
