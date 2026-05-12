from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class ValuationCritic(BaseAgent):
    def __init__(self):
        system_prompt = """You are a senior quantitative analyst. 
Objective: Compare stock P/E to sector norms and recommend a trade. 
Constraints: 
- If P/E < Norm: Recommend BUY. 
- If P/E > Norm: Recommend SELL.
- You MUST output the full trade details: Recommendation, Price, and Quantity.
- Format: "REC: BUY 1000 units of {ticker} at ${price} (P/E: {pe})"

Valid Statuses: SUCCESS, PROCESS_SLOW
"""
        super().__init__("ValuationCritic", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Get market data from history (first element is DataFetcher)
        history = context.get("history", [])
        data_fetcher_output = history[0].get("output", "") if history else "No data"
        
        return await self._call_llm(f"Analyze this market data and provide a specific quantity to buy/sell: {data_fetcher_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        # Extract ticker from query if possible
        return {
            "status": AgentStatus.SUCCESS,
            "output": "VALUATION_MODEL: UNDERVALUED. REC: BUY 1000 units at $175.50 (P/E: 24.5).",
            "confidence": 0.95,
            "reasoning": "P/E is below sector norm. Recommending a standard institutional block of 1000 units."
        }
