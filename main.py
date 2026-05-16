import gradio as gr
import asyncio
import json
import pandas as pd
from datetime import datetime
import uuid
import time
import os
from typing import Dict, Any, List, Generator

# Import our new architecture
from agents import (
    DataFetcher, ValuationCritic, RiskManager, ExecutionBot,
    Fractionalizer, NewsAnalysis, Liquidation, SimpleValuation, FallbackAgent
)
from orchestrator.orchestrator import Orchestrator
from constants.status import AgentStatus

class FinSenseApp:
    def __init__(self):
        self.agents = {
            "DataFetcher": DataFetcher(),
            "ValuationCritic": ValuationCritic(),
            "RiskManager": RiskManager(),
            "ExecutionBot": ExecutionBot(),
            "Fractionalizer": Fractionalizer(),
            "NewsAnalysis": NewsAnalysis(),
            "Liquidation": Liquidation(),
            "SimpleValuation": SimpleValuation(),
            "FallbackAgent": FallbackAgent()
        }
        self.orchestrator = Orchestrator()
        self.history = []
        os.makedirs("logs", exist_ok=True)

    def write_structured_log(self, ticker: str, start_time: float, agents_activated: List[str]):
        """Phase C: Write structured JSON log per cycle."""
        session_id = str(uuid.uuid4())
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Determine final status and order ID from history
        final_status = "UNKNOWN"
        order_id = None
        for result in reversed(self.history):
            if "FILLED" in str(result.get("output", "")):
                final_status = "FILLED"
                try:
                    order_id = result.get("output", {}).get("order_fill", {}).get("order_id")
                except:
                    pass
                break
            if "EMERGENCY_LIQUIDATION" in str(result.get("output", "")):
                final_status = "LIQUIDATED"
                break
            if result.get("status") in [AgentStatus.DATA_ERROR, "Error - Routing to Fallback"]:
                final_status = "ERROR"
        
        log_data = {
            "session_id": session_id,
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "agents_activated": agents_activated,
            "total_duration_ms": duration_ms,
            "final_status": final_status,
            "order_id": order_id
        }
        
        with open(f"logs/run_{session_id}.json", "w") as f:
            json.dump(log_data, f, indent=2)

    async def run_ticker_cycle(self, ticker: str) -> Generator[Dict[str, Any], None, None]:
        """Main execution loop controlled by the Orchestrator."""
        current_agent_name = "DataFetcher"
        logs = []
        self.history = [] # Reset history for new run
        
        # Fallback loop protection
        fallback_count = 0
        MAX_FALLBACKS = 2
        
        # Safeguard: Limit total iterations
        max_iterations = 15
        iteration_count = 0
        agents_activated = []
        start_time = time.time()
        
        while current_agent_name != "FINISH" and iteration_count < max_iterations:
            iteration_count += 1
            agents_activated.append(current_agent_name)
            agent = self.agents.get(current_agent_name)
            if not agent:
                break
                
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Activating {current_agent_name}...")
            yield {"logs": "\n".join(logs), "status": f"Running: {current_agent_name}"}
            
            # Build structured context for each agent
            context = {
                "ticker": ticker,
                "last_result": self.history[-1] if self.history else None,
                "history": self.history
            }
            
            # Execute Agent
            try:
                result = await agent.run(context)
                self.history.append(result)
                
                logs.append(f"[{current_agent_name}] Status: {result['status']}")
                logs.append(f"[{current_agent_name}] Output: {result['output']}")
                logs.append(f"[{current_agent_name}] Confidence: {result.get('confidence', 0.0)}")
                logs.append("-" * 30)
                
                yield {"logs": "\n".join(logs), "status": f"Agent {current_agent_name} Completed"}
                
                # Check for infinite fallback loops
                if current_agent_name == "FallbackAgent":
                    fallback_count += 1
                    if fallback_count >= MAX_FALLBACKS:
                        logs.append("🛑 Max fallback retries reached. Terminating safely.")
                        break

                # Ask Orchestrator what to do next
                workflow_state = {
                    "last_result": result,
                    "history": self.history
                }
                current_agent_name = await self.orchestrator.decide_next_agent(current_agent_name, workflow_state)
                
            except Exception as e:
                error_msg = str(e)
                logs.append(f"⚠️ Error in {current_agent_name}: {type(e).__name__}")
                
                # If ValuationCritic times out, use fast backup
                if current_agent_name == "ValuationCritic" and "Timeout" in type(e).__name__:
                    logs.append("⚡ Timeout detected - switching to SimpleValuation")
                    current_agent_name = "SimpleValuation"
                else:
                    current_agent_name = "FallbackAgent"
                    
                yield {"logs": "\n".join(logs), "status": "Error - Routing to Fallback"}

        if iteration_count >= max_iterations:
             logs.append("⚠️ Safety Break: Maximum workflow depth reached.")
             
        # Write structured JSON log (Phase C)
        self.write_structured_log(ticker, start_time, agents_activated)
             
        logs.append("✅ Workflow Cycle Complete.")
        yield {"logs": "\n".join(logs), "status": "Idle"}

app_instance = FinSenseApp()

def run_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# 💰 FinSense: Level 5 Autonomous Quant Analyst")
        gr.Markdown("### Advanced Multi-Agent System (LLM Orchestrated)")
        
        with gr.Row():
            with gr.Column(scale=1):
                ticker_input = gr.Textbox(label="Stock Ticker / Demo Keyword", placeholder="e.g., GOOGL, POLICY_REJECT_DEMO")
                run_btn = gr.Button("🚀 Start Autonomous Cycle", variant="primary")
                status_box = gr.Textbox(label="Current System State", interactive=False)
                
            with gr.Column(scale=2):
                log_output = gr.Textbox(label="Agent Thought Process & Execution Logs", lines=25, interactive=False)

        async def start_process(ticker):
            async for update in app_instance.run_ticker_cycle(ticker):
                yield update["logs"], update["status"]

        run_btn.click(
            start_process, 
            inputs=[ticker_input], 
            outputs=[log_output, status_box]
        )

        gr.Markdown("---")
        gr.Markdown("#### 💡 Demo Scenarios:")
        gr.Markdown("- **AAPL / GOOGL**: Standard Success Path (Real Market Data).")
        gr.Markdown("- **POLICY_REJECT_DEMO**: Strategic Failure -> Reroute to Fractionalizer.")
        gr.Markdown("- **MARKET_FREEZE_DEMO**: Market Failure -> Reroute to News Analysis.")
        gr.Markdown("- **SLOW_PROCESS_DEMO**: Latency Failure -> Reroute to Simple Valuation.")

    demo.queue().launch(share=False, theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate"))

if __name__ == "__main__":
    run_ui()
