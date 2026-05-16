import pytest
from agents import DataFetcher, ValuationCritic, RiskManager, Fractionalizer, ExecutionBot
from constants.status import AgentStatus

@pytest.mark.asyncio
async def test_risk_manager_deterministic_rejection():
    agent = RiskManager()
    
    # Test valid amount (500 * 100 = 50,000 < 150,000)
    context_valid = {"last_result": {"output": {"action": "BUY", "quantity": 500, "price": 100.0}}}
    res_valid = await agent.run(context_valid)
    assert res_valid["status"] == AgentStatus.SUCCESS
    
    # Test invalid amount (2000 * 100 = 200,000 > 150,000)
    context_invalid = {"last_result": {"output": {"action": "BUY", "quantity": 2000, "price": 100.0}}}
    res_invalid = await agent.run(context_invalid)
    assert res_invalid["status"] == AgentStatus.POLICY_REJECT

@pytest.mark.asyncio
async def test_fractionalizer_deterministic_halving():
    agent = Fractionalizer()
    context = {"last_result": {"output": {"action": "SELL", "quantity": 1000, "price": 150.0}}}
    res = await agent.run(context)
    
    assert res["status"] == AgentStatus.SUCCESS
    assert res["output"]["quantity"] == 500
    assert res["output"]["action"] == "SELL"
    assert res["output"]["price"] == 150.0

@pytest.mark.asyncio
async def test_data_fetcher_demo_keywords():
    agent = DataFetcher()
    
    # Test MARKET_FREEZE_DEMO
    res_freeze = await agent.run({"ticker": "MARKET_FREEZE_DEMO"})
    assert res_freeze["status"] == AgentStatus.MARKET_FREEZE
    
    # Test SLOW_PROCESS_DEMO
    res_slow = await agent.run({"ticker": "SLOW_PROCESS_DEMO"})
    assert res_slow["status"] == AgentStatus.PROCESS_SLOW
