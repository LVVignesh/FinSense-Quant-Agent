from typing import List, Dict, Any, Generator
import os
import json
import time
import gradio as gr
import sys
# Note: Google ADK imports are mocked here for external running

# --- Global Status Definitions (Needed for mock logic and Orchestrator) ---
STATUS_POLICY_REJECT = "POLICY_REJECT"
STATUS_MARKET_FREEZE = "MARKET_FREEZE"
STATUS_PROCESS_SLOW = "PROCESS_SLOW"
STATUS_SUCCESS = "SUCCESS"
STATUS_DATA_ERROR = "DATA_ERROR"
STATUS_UNAVAILABLE = "UNAVAILABLE"

# --- SMART MOCK AGENT CLASS ---
class Agent:
    """
    Simulates the Agent Development Kit (ADK) logic for demonstration purposes.
    Returns a structured dictionary indicating the next step or result.
    """
    def __init__(self, name: str, model: str, instructions: str, tools: List[Any] = None, memory: Any = None):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model = model
        
    def run(self, query: str) -> Dict[str, Any]:
        """
        Simulates the agent's LLM call and structured output based on the input query.
        """
        # Default result if no specific mock logic applies
        result = {"status": STATUS_SUCCESS, "output": f"[Mock Output from {self.name}] Processed: {query}"}

        # --- SMART MOCK LOGIC FOR FINANCE (WITH WALL STREET POLISH) ---
        is_policy_reject_demo = "POLICY_REJECT_DEMO" in query
        is_market_freeze_demo = "MARKET_FREEZE_DEMO" in query
        is_slow_process_demo = "SLOW_PROCESS_DEMO" in query

        if self.name == "DataFetcher":
            if "GOOGL" in query: 
                result["output"] = "DATA: Ticker=GOOGL | Price=$175.00 | P/E=24.0 | Sector=Tech"
            elif "TSLA" in query: 
                result["output"] = "DATA: Ticker=TSLA | Price=$180.00 | P/E=60.0 | Sector=Auto"
            elif is_policy_reject_demo:
                # Inject signal for Policy Reject demo
                result["output"] = "DATA: Ticker=HIGH_RISK_ETF | Price=$500.00 | Volatility=High | SIGNAL: POLICY_REJECT_DEMO" 
            elif is_market_freeze_demo:
                result["status"] = STATUS_MARKET_FREEZE
                result["output"] = "MARKET_HALT: LUDP (Limit Up-Limit Down) Pause Triggered. Volatility spike > 10%."
            elif "UNAVAILABLE" in query:
                result["status"] = STATUS_DATA_ERROR
                result["output"] = "API_ERROR: 404 Not Found. Data source unreachable."
            else: 
                result["status"] = STATUS_DATA_ERROR
                result["output"] = "API_ERROR: Ticker symbol invalid."

        elif self.name == "ValuationCritic":
            # Pass signals through
            signal = " | SIGNAL: POLICY_REJECT_DEMO" if is_policy_reject_demo else ""
            
            if "24.0" in query: 
                result["output"] = f"VALUATION_MODEL: UNDERVALUED. Target=$210. REC: BUY.{signal}"
            elif "60.0" in query: 
                result["output"] = f"VALUATION_MODEL: OVERVALUED. Mean Reversion likely. REC: SELL.{signal}"
            elif is_slow_process_demo:
                result["status"] = STATUS_PROCESS_SLOW
                result["output"] = "LATENCY_WARNING: DCF Model computation > 5000ms. Optimization required."
            else:
                result["output"] = f"VALUATION_MODEL: BUY (Strong Conviction).{signal}"

        elif self.name == "RiskManager":
            if "SELL" in query: 
                result["output"] = "COMPLIANCE_CHECK: PASSED. De-risking execution authorized."
            
            elif "POLICY_REJECT_DEMO" in query: 
                 result["status"] = STATUS_POLICY_REJECT
                 result["output"] = "RISK_VIOLATION: Notional Value ($500k) > Daily Alloc Limit ($150k). REJECTED."
            
            elif "ALGO_OPTIMIZATION" in query or "RE-CALCULATED" in query: 
                 result["output"] = "COMPLIANCE_CHECK: PASSED. Modified Notional ($125k) < Daily Alloc Limit ($150k). APPROVED."
            
            elif "BUY" in query:
                result["output"] = "COMPLIANCE_CHECK: PASSED. Fundamentals strong. Exposure within VAR limits."

        elif self.name == "ExecutionBot":
            result["output"] = "ORDER_FILL: Market Buy Executed. Route: SMART. Time: 14ms. Portfolio Updated."

        elif self.name == "FallbackAgent":
            result["output"] = "FALLBACK_PROTOCOL: Secondary data feed activated. Watch order placed."

        elif self.name == "FractionalizerAgent":
            result["output"] = "ALGO_OPTIMIZATION: Input Size: 1,000. Limit Constraint: 25%. Target: 250. Status: RE-CALCULATED."
            result["status"] = STATUS_SUCCESS 

        elif self.name == "NewsAnalysisAgent":
            if "TSLA" in query or is_market_freeze_demo: 
                result["output"] = "SENTIMENT_ANALYSIS: CONFIRMED Black Swan. Regulatory Action detected. ACTION: Fundamental Change."
                result["status"] = STATUS_SUCCESS
            else:
                result["output"] = "SENTIMENT_ANALYSIS: Noise detected. No fundamental shift. ACTION: Temporary Glitch."
                result["status"] = STATUS_SUCCESS

        elif self.name == "LiquidationAgent":
            result["output"] = "EMERGENCY_PROTOCOL: Liquidating positions. Order Type: IOC (Immediate or Cancel)."
            result["status"] = STATUS_SUCCESS
            
        elif self.name == "SimpleValuationAgent":
            result["output"] = "HEURISTIC_CHECK: Quick Ratio > 1.0. Momentum Positive. Proceeding."
            result["status"] = STATUS_SUCCESS
            
        return result

# --- TOOLS & MEMORY DEFINITIONS ---

# 1. Market Tool (Simulates API)
def get_market_data_tool(ticker: str) -> str:
    """Fetches real-time price and P/E ratio from a mock JSON file."""
    print(f"    📈 [Tool Call] Fetching Data for: {ticker}...")
    try:
        # Assumes market_data.json exists (created in main execution block)
        with open("market_data.json", "r") as f:
            db = json.load(f)
        if ticker in db:
            data = db[ticker]
            return f"DATA: Price ${data['price']} | P/E {data['pe']}"
        return "Error: Ticker not found."
    except:
        return "Error: Database unavailable."

# 2. Memory Bank (Simulates RAG History)
class MemoryBank:
    """Mock memory for historical context retrieval."""
    def recall(self, query: str) -> str:
        return "HISTORY: Similar undervaluation in 2023 led to 15% gain."

memory_bank = MemoryBank()
def recall_history_tool(query: str) -> str: 
    return memory_bank.recall(query)

# --- AGENT MAP DEFINITION ---

AGENT_MAP = {
    # Primary Workflow Agents
    "DataFetcher": Agent(
        name="DataFetcher",
        model="gemini-2.5-flash",
        tools=[get_market_data_tool],
        instructions="Fetch price and P/E data. Pass to Orchestrator."
    ),
    "ValuationCritic": Agent(
        name="ValuationCritic",
        model="gemini-2.5-flash",
        tools=[recall_history_tool],
        instructions="Compare P/E to industry norm. Check Memory. Recommend BUY/SELL. Note: May be slow."
    ),
    "RiskManager": Agent(
        name="RiskManager",
        model="gemini-2.5-flash",
        instructions="Review recommendation against risk policy. Output APPROVED or POLICY_REJECT."
    ),
    "ExecutionBot": Agent(
        name="ExecutionBot",
        model="gemini-2.5-flash",
        instructions="If Approved, execute trade and update Portfolio DB."
    ),

    # LEVEL 5 SELF-CORRECTION AGENTS
    "FractionalizerAgent": Agent(
        name="FractionalizerAgent",
        model="gemini-2.5-flash",
        instructions="Calculate a reduced trade size (e.g., 25% of original) to bypass policy limits."
    ),
    "NewsAnalysisAgent": Agent(
        name="NewsAnalysisAgent",
        model="gemini-2.5-flash",
        instructions="Analyze external news for market halt reason. Output 'Fundamental Change' or 'Temporary Glitch'."
    ),
    "LiquidationAgent": Agent(
        name="LiquidationAgent",
        model="gemini-2.5-flash",
        instructions="Execute urgent sale of high-risk assets upon detecting a black swan fundamental change."
    ),
    "SimpleValuationAgent": Agent(
        name="SimpleValuationAgent",
        model="gemini-2.5-flash",
        instructions="Provide a fast, high-level valuation recommendation when the primary critic is too slow."
    ),
    "FallbackAgent": Agent(
        name="FallbackAgent",
        model="gemini-2.5-flash",
        instructions="Initiate secondary data retrieval, place a watch order, or initiate a wait-and-retry protocol."
    ),
}

# --- LEVEL 5 ORCHESTRATION LOGIC (Mocks the Orchestrator Agent's Decision) ---

def orchestrate_step(previous_agent: str, previous_output: Dict[str, Any]) -> str:
    """Mocks the Orchestrator's dynamic decision making with Level 5 self-correction."""
    status = previous_output.get("status", STATUS_SUCCESS)
    output = previous_output.get("output", "")

    # 1. General/Technical Failure: Reroute to Fallback
    if status == STATUS_DATA_ERROR or status == STATUS_UNAVAILABLE:
        print(f"[Orchestrator] Data Error ({status}) detected. Routing to FallbackAgent.")
        return "FallbackAgent"

    # 2. Strategic Failure (Policy Reject) -> Reroute to Fractionalizer
    if status == STATUS_POLICY_REJECT:
        print("[Orchestrator] Policy Rejection detected. Routing to FractionalizerAgent to reduce trade size.")
        return "FractionalizerAgent"

    # 3. Market Failure (Market Freeze) -> Reroute to News Analysis
    if status == STATUS_MARKET_FREEZE:
        print("[Orchestrator] Market Freeze detected. Routing to NewsAnalysisAgent for crisis assessment.")
        return "NewsAnalysisAgent"
    
    # 4. Process Failure (Agent Too Slow) -> Reroute to Simple Valuation
    if status == STATUS_PROCESS_SLOW and previous_agent == "ValuationCritic":
        print("[Orchestrator] ValuationCritic was too slow. Routing to SimpleValuationAgent for speed.")
        return "SimpleValuationAgent"

    # --- PRIMARY WORKFLOW LOGIC ---

    if previous_agent == "DataFetcher":
        return "ValuationCritic"
    
    # Decision logic is same for both valuation agents
    if previous_agent == "ValuationCritic" or previous_agent == "SimpleValuationAgent":
        if "BUY" in output or "SELL" in output:
            return "RiskManager"
        return "END" 

    if previous_agent == "RiskManager" and "APPROVED" in output:
        return "ExecutionBot"
    
    # --- SELF-CORRECTION REROUTING LOGIC (After corrective agents run) ---
    
    if previous_agent == "FractionalizerAgent":
        # After reducing size, re-submit the smaller trade to the RiskManager
        return "RiskManager"

    if previous_agent == "NewsAnalysisAgent":
        if "Fundamental Change" in output:
            # If crisis is fundamental, liquidate immediately
            return "LiquidationAgent"
        else:
            # If glitch, stop and go to fallback for wait-and-retry protocol
            return "FallbackAgent"

    # If all else fails or execution is complete
    return "END"


# --- FINSENSE DASHBOARD (UI) ---

def finsense_ui_runner(ticker_input: str) -> Generator[str, None, None]:
    """Runs the dynamic Level 5 agent pipeline using Gradio's generator yield."""
    logs = []
    def log(message):
        timestamp = time.strftime("%H:%M:%S")
        logs.append(f"[{timestamp}] {message}")
        return "\n".join(logs)

    ticker = ticker_input.strip().upper()
    current_agent_name = "DataFetcher"
    
    yield log(f"🔵 [System] Starting Analysis for: {ticker}")
    yield log(f"🧠 [Orchestrator] Initial Plan: Start with data gathering.")
    time.sleep(1)

    # State variables for the loop
    current_input = ticker
    
    # Run the dynamic pipeline until the Orchestrator signals END
    while current_agent_name != "END":
        
        # 0. Get the current agent object
        current_agent = AGENT_MAP.get(current_agent_name)
        if not current_agent:
            yield log(f"❌ ERROR: Unknown agent '{current_agent_name}'. Halting.")
            break
        
        # 1. Announce step
        yield log(f"\n⚙️ [{current_agent_name}] Running with input: {current_input}")
        
        # 2. Simulate Tool/Memory use for visual fidelity
        if current_agent_name == "DataFetcher":
              yield log(f"    > 📈 Tool Call: get_market_data('{ticker}')")
        elif current_agent_name == "ValuationCritic":
              yield log(f"    > 🧠 Memory Recall: {memory_bank.recall(ticker).split(': ')[1]}")
        elif current_agent_name == "NewsAnalysisAgent":
              yield log(f"    > 📰 Checking external news sources...")

        time.sleep(1)
        
        # 3. Agent Execution (Mocked)
        current_output = current_agent.run(current_input)
        
        # 4. Process Output and Log
        yield log(f"📝 [{current_agent_name} Output Status]: {current_output['status']}")
        yield log(f"📝 [{current_agent_name} Output]: {current_output['output']}")
        
        # 5. ORCHESTRATION (The Level 5 Core)
        next_agent_name = orchestrate_step(current_agent_name, current_output)
        
        yield log(f"\n🧠 [Orchestrator Decision]: Next Agent is {next_agent_name}")
        
        # 6. Update for next iteration
        current_agent_name = next_agent_name
        current_input = current_output['output'] # Next input is the previous output
        
        # Handle Immediate Execution for terminal agents like Fallback or Liquidation
        if current_agent_name == "FallbackAgent" or current_agent_name == "LiquidationAgent":
            final_agent = AGENT_MAP[current_agent_name]
            # Must run the final agent to generate its output, as the Orchestrator only decided the name
            yield log(f"\n⚙️ [{final_agent.name}] Running Final Corrective Action...")
            final_output = final_agent.run(ticker)
            yield log(f"📝 [{final_agent.name} Output]: {final_output['output']}")
            current_agent_name = "END" # Force loop to exit after final action
            
    yield log(f"\n🎉 SEQUENCE COMPLETE.")


def main():
    # --- MOCK DATA GENERATION (Simulates Financial Data API) ---
    market_data = {
        "GOOGL": {"price": 175.50, "pe": 24.5, "sector": "Tech"},
        "TSLA": {"price": 180.00, "pe": 60.0, "sector": "Auto"},
    }
    with open("market_data.json", "w") as f:
        json.dump(market_data, f, indent=4)
    print("✅ Mock Market Database 'market_data.json' created.")
    
    # --- API CONFIGURATION (Mocked for public repository) ---
    # In a real ADK project, this would load the API Key.
    os.environ["GOOGLE_API_KEY"] = "MOCK_KEY"
    print("⚠️ Using Mock Mode. Replace 'MOCK_KEY' with your actual API key for real ADK execution.")

    # --- GRADIO UI DEFINITION ---
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🚀 FinSense: Level 5 Autonomous Quant Analyst")
        gr.Markdown("The **Orchestrator Agent** dynamically controls the workflow, including self-correction (Level 5).")
        
        gr.Markdown("### Demo Scenarios (Enter one of these inputs):")
        gr.Markdown("- **GOOGL/TSLA:** Standard success path.")
        gr.Markdown("- **POLICY_REJECT_DEMO:** Strategic Correction (Risk Rejects -> Fractionalizer -> Re-submit).")
        gr.Markdown("- **SLOW_PROCESS_DEMO:** Process Correction (Valuation Slow -> SimpleValuationAgent).")
        gr.Markdown("- **MARKET_FREEZE_DEMO:** Market Correction (Freeze -> NewsAnalysis -> Liquidation/Fallback).")
        
        with gr.Row():
            with gr.Column(scale=1):
                ticker_in = gr.Textbox(label="Stock Ticker / Demo Scenario Input", placeholder="e.g. GOOGL or POLICY_REJECT_DEMO")
                btn = gr.Button("Run Dynamic Analysis", variant="primary")
                gr.Examples([
                    "GOOGL", 
                    "POLICY_REJECT_DEMO",
                    "SLOW_PROCESS_DEMO",
                    "MARKET_FREEZE_DEMO",
                    "UNAVAILABLE"
                ], inputs=ticker_in)
            with gr.Column(scale=2):
                out = gr.Code(label="Agent Trace Logs (Dynamic Workflow)", language="shell", lines=30)
                
        btn.click(fn=finsense_ui_runner, inputs=ticker_in, outputs=out)

    print("🚀 Launching Level 5 UI...")
    demo.queue().launch(share=False, inline=True, height=600)

if __name__ == "__main__":
    main()
