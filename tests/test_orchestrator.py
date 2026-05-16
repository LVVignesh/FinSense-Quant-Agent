import pytest
from orchestrator.orchestrator import Orchestrator
from constants.status import AgentStatus

@pytest.mark.asyncio
async def test_orchestrator_happy_path():
    orch = Orchestrator()
    # Mock client to force hardcoded logic for testing deterministic routes
    orch.client = None
    
    assert await orch.decide_next_agent("DataFetcher", {"last_result": {"status": AgentStatus.SUCCESS}}) == "ValuationCritic"
    assert await orch.decide_next_agent("ValuationCritic", {"last_result": {"status": AgentStatus.SUCCESS}}) == "RiskManager"
    assert await orch.decide_next_agent("RiskManager", {"last_result": {"status": AgentStatus.SUCCESS}}) == "ExecutionBot"
    assert await orch.decide_next_agent("ExecutionBot", {"last_result": {"status": AgentStatus.SUCCESS}}) == "FINISH"

@pytest.mark.asyncio
async def test_orchestrator_policy_reject_path():
    orch = Orchestrator()
    orch.client = None
    
    assert await orch.decide_next_agent("RiskManager", {"last_result": {"status": AgentStatus.POLICY_REJECT}}) == "Fractionalizer"
    assert await orch.decide_next_agent("Fractionalizer", {"last_result": {"status": AgentStatus.SUCCESS}}) == "RiskManager"

@pytest.mark.asyncio
async def test_orchestrator_market_freeze_path():
    orch = Orchestrator()
    orch.client = None
    
    assert await orch.decide_next_agent("DataFetcher", {"last_result": {"status": AgentStatus.MARKET_FREEZE}}) == "NewsAnalysis"
    assert await orch.decide_next_agent("NewsAnalysis", {"last_result": {"output": {"crisis_level": "CRISIS"}}}) == "Liquidation"
    assert await orch.decide_next_agent("Liquidation", {"last_result": {"status": AgentStatus.SUCCESS}}) == "FINISH"

@pytest.mark.asyncio
async def test_orchestrator_slow_process_path():
    orch = Orchestrator()
    orch.client = None
    
    assert await orch.decide_next_agent("DataFetcher", {"last_result": {"status": AgentStatus.PROCESS_SLOW}}) == "SimpleValuation"
    assert await orch.decide_next_agent("ValuationCritic", {"last_result": {"status": AgentStatus.PROCESS_SLOW}}) == "SimpleValuation"
    assert await orch.decide_next_agent("SimpleValuation", {"last_result": {"status": AgentStatus.SUCCESS}}) == "RiskManager"
