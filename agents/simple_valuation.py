from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class SimpleValuation(BaseAgent):
    def __init__(self):
        system_prompt = """You are a fast heuristic valuation agent.
Objective: Quickly analyze market data and provide a trade recommendation.

STRICT OUTPUT RULE:
Your 'output' field MUST be a JSON object with EXACTLY these keys:
- "action": string (either "BUY" or "SELL")
- "quantity": integer (default to 500 as a conservative size)
- "price": float (extracted from the market data)

STATUS FIELD RULE: Always use exactly 'SUCCESS'. Never use 'OK', 'ok', 'done', or any other value.
"""
        super().__init__("SimpleValuation", system_prompt, fast_mode=True)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_result = context.get("last_result", {})
        last_output = last_result.get("output", "") if last_result else ""
        history = context.get("history", [])
        data = history[0].get("output", last_output) if history else last_output
        return await self._call_llm(f"Quickly analyze this data and return a structured trade recommendation: {data}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.SUCCESS,
            "output": {"action": "BUY", "quantity": 500, "price": 175.50},
            "confidence": 0.7,
            "reasoning": "Fast heuristic: P/E within acceptable range. Conservative 500-unit position."
        }
