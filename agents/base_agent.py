from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import json
import asyncio
from pydantic import BaseModel, Field, ValidationError
from groq import AsyncGroq
from tenacity import retry, stop_after_attempt, wait_exponential
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GROQ_API_KEY, MOCK_MODE, DEFAULT_MODEL
from constants.status import AgentStatus

class AgentResponse(BaseModel):
    status: str
    output: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str

class BaseAgent(ABC):
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Context now contains: ticker, last_result, history"""
        pass

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _call_llm(self, user_prompt: str) -> Dict[str, Any]:
        if MOCK_MODE or not self.client:
            return self._mock_response(user_prompt)
        
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"}
                ),
                timeout=5.0
            )
            
            content = response.choices[0].message.content
            validated_response = AgentResponse.model_validate_json(content)
            return validated_response.model_dump()

        except asyncio.TimeoutError:
            return {
                "status": AgentStatus.PROCESS_SLOW,
                "output": "LATENCY_CRITICAL: Timeout during inference.",
                "confidence": 0.0,
                "reasoning": "Agent failed to respond within 5000ms SLA."
            }
        except Exception as e:
            # Tenacity will automatically retry this
            raise e

    @abstractmethod
    def _mock_response(self, query: str) -> Dict[str, Any]:
        pass
