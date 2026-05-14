from .base_agent import BaseAgent
from typing import Dict, Any
from constants.status import AgentStatus

class FallbackAgent(BaseAgent):
    def __init__(self):
        system_prompt = """You are a technical fallback agent.
Objective: Handle API failures, data errors, and technical anomalies.
Constraints:
- Initiate secondary data retrieval or wait-and-retry protocols.
- Always return a clear 'output' field explaining the recovery step.

STATUS FIELD RULE: Always use exactly 'SUCCESS'. Never use 'OK', 'ok', 'done', or any other value.
"""
        super().__init__("FallbackAgent", system_prompt, fast_mode=True)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        last_output = context.get("last_result", {}).get("output", "")
        return await self._call_llm(f"Initiate technical fallback for: {last_output}")

    def _mock_response(self, query: str) -> Dict[str, Any]:
        return {
            "status": AgentStatus.SUCCESS,
            "output": "FALLBACK_ACTION: Technical anomaly handled. Rerouting to redundant workflow path.",
            "confidence": 1.0,
            "reasoning": "Standard technical recovery protocol triggered to maintain system uptime."
        }
