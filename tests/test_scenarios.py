import pytest
from main import FinSenseApp
from constants.status import AgentStatus
import json
import os

@pytest.mark.asyncio
async def test_end_to_end_scenarios():
    app = FinSenseApp()
    
    # We will just verify that the generator yields the correct status messages
    # Test MARKET_FREEZE_DEMO
    freeze_events = []
    async for event in app.run_ticker_cycle("MARKET_FREEZE_DEMO"):
        freeze_events.append(event["status"])
    
    assert "Running: DataFetcher" in freeze_events
    assert "Running: NewsAnalysis" in freeze_events
    assert "Idle" in freeze_events[-1]
    
    # Clean up the logs created by the test
    for f in os.listdir("logs"):
        if f.startswith("run_") and f.endswith(".json"):
            os.remove(os.path.join("logs", f))
