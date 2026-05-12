from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import json
import asyncio
import re
from pydantic import BaseModel, Field, ValidationError
from groq import AsyncGroq
from tenacity import retry, stop_after_attempt, wait_exponential
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GROQ_API_KEY, MOCK_MODE, DEFAULT_MODEL
from constants.status import AgentStatus

# Phase 3 Upgrade: Flexible Schema
class AgentResponse(BaseModel):
    status: str = "DATA_ERROR"
    output: str = "No output provided."
    confidence: float = 0.0
    reasoning: str = "No reasoning provided."

class BaseAgent(ABC):
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def _extract_json(self, raw_text: str) -> Dict[str, Any]:
        """Safely extracts JSON from LLM response."""
        try:
            cleaned = raw_text.strip()
            # Handle markdown code blocks
            if "```" in cleaned:
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            
            return json.loads(cleaned.strip())
        except Exception:
            # Fallback to regex if simple cleaning fails
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            return {}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _call_llm(self, user_prompt: str) -> Dict[str, Any]:
        if MOCK_MODE or not self.client:
            return self._mock_response(user_prompt)
        
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": self.system_prompt + "\n\nCRITICAL: Return ONLY a raw JSON object. Use this exact keys: 'status', 'output', 'confidence', 'reasoning'."},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1
                ),
                timeout=10.0 # Increased timeout for reliability
            )
            
            content = response.choices[0].message.content
            print(f"DEBUG [{self.name}] Raw Response: {content[:200]}...") # Log raw response for debugging
            
            extracted_data = self._extract_json(content)
            
            # Use model_validate with default values for missing fields
            try:
                validated_response = AgentResponse.model_validate(extracted_data)
                return validated_response.model_dump()
            except ValidationError as ve:
                print(f"DEBUG [{self.name}] Validation failed on: {extracted_data}")
                # Create a semi-valid response manually if Pydantic fails
                return {
                    "status": str(extracted_data.get("status", AgentStatus.DATA_ERROR)),
                    "output": str(extracted_data.get("output", "Output parsing failed.")),
                    "confidence": float(extracted_data.get("confidence", 0.0)),
                    "reasoning": str(extracted_data.get("reasoning", "Reasoning parsing failed."))
                }

        except Exception as e:
            error_type = type(e).__name__
            print(f"[{self.name}] API Error: {error_type} - {str(e)}")
            raise e

    @abstractmethod
    def _mock_response(self, query: str) -> Dict[str, Any]:
        pass
