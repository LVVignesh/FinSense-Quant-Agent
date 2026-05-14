from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class ValuationCritic(BaseAgent):
    def __init__(self):
        system_prompt = """You are a senior quantitative analyst. 
Objective: Compare stock P/E to sector norms and recommend a trade. 

STRICT OUTPUT RULE:
Your 'output' field MUST be a JSON object containing EXACTLY these keys:
- "action": string (either "BUY" or "SELL")
- "quantity": integer (default to 1000)
- "price": float (extracted from market data)

STATUS FIELD RULE: Always use exactly 'SUCCESS' or 'PROCESS_SLOW'. Never use 'OK', 'ok', 'done', or any other value.

Example 'output': {"action": "SELL", "quantity": 1000, "price": 175.50}
"""
        super().__init__("ValuationCritic", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        history = context.get("history", [])
        data_fetcher_output = history[0].get("output", "") if history else "No data"
        
        return await self._call_llm(f"Analyze this market data and provide a structured trade recommendation: {data_fetcher_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.SUCCESS,
            "output": {"action": "SELL", "quantity": 1000, "price": 175.50},
            "confidence": 0.95,
            "reasoning": "P/E is below sector norm. Recommending a standard institutional block of 1000 units."
        }
