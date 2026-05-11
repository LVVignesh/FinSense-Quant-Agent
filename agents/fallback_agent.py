from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class FallbackAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a technical fallback agent.
Objective: Handle API failures, data errors, and technical anomalies.
Constraints:
- Initiate secondary data retrieval or wait-and-retry protocols.
- Output 'FALLBACK_ACTION' and details.

Valid Statuses: SUCCESS
"""
        super().__init__("FallbackAgent", system_prompt)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Initiate technical fallback for: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.SUCCESS,
            "output": "FALLBACK_ACTION: Secondary data feed activated. Watch order placed.",
            "confidence": 1.0,
            "reasoning": "Technical anomaly detected; switching to redundant infrastructure for data integrity."
        }
