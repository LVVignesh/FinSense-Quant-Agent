from typing import List, Dict, Any, Optional
import os
import sys
import json
from pydantic import BaseModel, Field, ValidationError
from groq import AsyncGroq

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GROQ_API_KEY, DEFAULT_MODEL
from constants.status import AgentStatus

# Phase 3 Upgrade: Strict Orchestration Schema
class OrchestratorDecision(BaseModel):
    next_agent: str
    reasoning: str
    priority: str = Field(pattern="^(LOW|MEDIUM|HIGH|URGENT)$")

class Orchestrator:
    def __init__(self):
        self.client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        self.system_prompt = """You are the Institutional Investment Orchestrator. 
Your role is to autonomously control the quantitative workflow state machine.

CORE RESPONSIBILITIES:
1. Routing: Decide the optimal next agent based on previous outputs, confidence scores, and workflow history.
2. Safety: Detect potential failures, loops, or low-confidence decisions and route to fallback workflows.
3. Efficiency: Prioritize execution safety over speed, but handle latency by swapping to heuristic agents.

WORKFLOW CONTEXT:
- DataFetcher -> ValuationCritic -> RiskManager -> ExecutionBot (Standard)
- RiskManager POLICY_REJECT -> Fractionalizer -> RiskManager (Self-Correction)
- DataFetcher MARKET_FREEZE -> NewsAnalysis -> Liquidation (Crisis Handling)
- ValuationCritic PROCESS_SLOW -> SimpleValuation (Latency Handling)
- Any DATA_ERROR/UNAVAILABLE -> FallbackAgent (Recovery)

ROUTING CRITERIA:
- If Confidence < 0.4: Route to secondary validation or Fallback.
- If status is POLICY_REJECT: You MUST route to Fractionalizer to optimize size.
- If status is MARKET_FREEZE: You MUST route to NewsAnalysis for crisis diagnosis.

Return JSON ONLY matching the OrchestratorDecision schema.
"""

    async def decide_next_agent(self, current_agent: str, workflow_state: Dict[str, Any]) -> str:
        """Uses LLM to reason dynamically about the next step."""
        if not self.client:
            return self._hardcoded_logic(current_agent, workflow_state.get("last_result", {}))

        prompt = f"Current Agent: {current_agent}\nWorkflow State: {json.dumps(workflow_state)}"
        
        try:
            response = await self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            decision = OrchestratorDecision.model_validate_json(content)
            return decision.next_agent
        except Exception:
            return self._hardcoded_logic(current_agent, workflow_state.get("last_result", {}))

    def _hardcoded_logic(self, current_agent: str, last_output: Dict[str, Any]) -> str:
        status = last_output.get("status")
        output_text = str(last_output.get("output", ""))
        
        if current_agent == "DataFetcher":
            if status == AgentStatus.SUCCESS: return "ValuationCritic"
            if status == AgentStatus.MARKET_FREEZE: return "NewsAnalysis"
            return "FallbackAgent"
        
        if current_agent == "ValuationCritic":
            if status == AgentStatus.SUCCESS: return "RiskManager"
            if status == AgentStatus.PROCESS_SLOW: return "SimpleValuation"
            return "FallbackAgent"
            
        if current_agent == "RiskManager":
            if "APPROVED" in output_text: return "ExecutionBot"
            if status == AgentStatus.POLICY_REJECT: return "Fractionalizer"
            
        if current_agent == "Fractionalizer":
            return "RiskManager"
            
        if current_agent == "NewsAnalysis":
            if "Fundamental Change" in output_text: return "Liquidation"
            return "FallbackAgent"
            
        return "FINISH"
