from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class ValuationCritic(BaseAgent):
    def __init__(self):
        system_prompt = """You are a senior quantitative analyst. 
Objective: Compare stock P/E to sector norms (Tech: 25, Auto: 15). 
Constraints: 
- If P/E < Norm: Recommend BUY. 
- If P/E > Norm: Recommend SELL.
- Output must contain the words 'BUY' or 'SELL'.
- Reasoning must justify the recommendation based on the valuation gap.

Valid Statuses: SUCCESS, PROCESS_SLOW
"""
        super().__init__("ValuationCritic", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Evaluate compliance for this recommendation: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.SUCCESS,
            "output": "VALUATION_MODEL: UNDERVALUED. Target=$210. REC: BUY.",
            "confidence": 0.95,
            "reasoning": "P/E of 24.5 is below tech sector norm of 25.0, suggesting 5% upside."
        }
