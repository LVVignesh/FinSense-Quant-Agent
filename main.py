import gradio as gr
import asyncio
import json
import pandas as pd
from datetime import datetime
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

    async def run_ticker_cycle(self, ticker: str) -> Generator[Dict[str, Any], None, None]:
        """Main execution loop controlled by the Orchestrator."""
        current_agent_name = "DataFetcher"
        logs = []
        self.history = [] # Reset history for new run
        
        # FIX 6: Fallback loop protection
        fallback_count = 0
        MAX_FALLBACKS = 2
        
        # Safeguard: Limit total iterations
        max_iterations = 15
        iteration_count = 0
        
        while current_agent_name != "FINISH" and iteration_count < max_iterations:
            iteration_count += 1
            agent = self.agents.get(current_agent_name)
            if not agent:
                break
                
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Activating {current_agent_name}...")
            yield {"logs": "\n".join(logs), "status": f"Running: {current_agent_name}"}
            
            # Prepare Structured Context
            context = {
                "ticker": ticker,
                "last_result": self.history[-1] if self.history else None,
                "history": self.history[-3:]
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
                        logs.append("🛑 Max fallback retries reached. Terminating safely to prevent loop.")
                        break

                # Ask Orchestrator what to do next
                workflow_state = {
                    "last_result": result,
                    "history": self.history
                }
                current_agent_name = await self.orchestrator.decide_next_agent(current_agent_name, workflow_state)
                
            except Exception as e:
                logs.append(f"⚠️ Critical Error in {current_agent_name}: {str(e)}")
                current_agent_name = "FallbackAgent"
                yield {"logs": "\n".join(logs), "status": "Error - Routing to Fallback"}

        if iteration_count >= max_iterations:
             logs.append("⚠️ Safety Break: Maximum workflow depth reached.")
             
        logs.append("✅ Workflow Cycle Complete.")
        yield {"logs": "\n".join(logs), "status": "Idle"}

app_instance = FinSenseApp()

def run_ui():
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate")) as demo:
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

    demo.queue().launch(share=False)

if __name__ == "__main__":
    run_ui()
