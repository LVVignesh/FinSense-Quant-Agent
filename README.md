💰 FinSense: Level 5 Autonomous Quant Analyst System

🎯 Project Overview

FinSense is a state-of-the-art Multi-Agent System (MAS) designed to simulate Level 5 Autonomy in high-frequency quantitative finance.

Unlike traditional trading bots that follow linear scripts and crash upon failure, FinSense features a dynamic Orchestrator Agent. This central intelligence continuously monitors the execution pipeline and autonomously self-corrects when it encounters data errors, policy violations, or market anomalies—without requiring human intervention.

🧠 Key Autonomous Features: Self-Healing Workflow

The system demonstrates three specific "Self-Correction Loops" that define its Level 5 capabilities:

1. Strategic Failure Correction (Policy Violation)

Scenario: The RiskManager rejects a trade because the volume is too high (STATUS_POLICY_REJECT).

Autonomous Fix: The Orchestrator reroutes to the Fractionalizer Agent, which mathematically optimizes the trade size to fit within risk limits and automatically resubmits it for approval.

2. Market Failure Correction (Black Swan Event)

Scenario: The DataFetcher detects a trading halt or market freeze (STATUS_MARKET_FREEZE).

Autonomous Fix: The system triggers the News Analysis Agent to diagnose the cause. If a fundamental crisis is confirmed, it activates the Liquidation Agent to dump assets immediately. If it's a glitch, it routes to the Fallback Agent.

3. Process Failure Correction (Latency Optimization)

Scenario: The primary ValuationCritic model takes too long to compute (STATUS_PROCESS_SLOW).

Autonomous Fix: The Orchestrator detects the latency violation and instantly swaps in the Simple Valuation Agent (heuristic-based) to ensure the trade decision is made within the required time window.

📐 System Architecture

The architecture relies on a Hub-and-Spoke model where the Orchestrator manages state and routing between specialized agents.

The Agent Team

Agent Name

Role

Status Codes Monitored

Orchestrator

Controller: Manages dynamic routing and error handling.

All

DataFetcher

Sensor: Retrieves market data via simulated APIs.

STATUS_MARKET_FREEZE

ValuationCritic

Planner: Deep fundamental analysis (DCF).

STATUS_PROCESS_SLOW

RiskManager

Governance: Enforces portfolio risk limits.

STATUS_POLICY_REJECT

ExecutionBot

Actor: Simulates exchange order placement.

STATUS_SUCCESS

Fractionalizer

Corrector: Optimizes trade size for compliance.

(Strategic Fix)

NewsAnalysis

Corrector: Diagnoses external market shocks.

(Market Fix)

SimpleValuation

Corrector: Low-latency backup analysis.

(Process Fix)

⚙️ Setup and Usage

The project is encapsulated in a single Python script using Gradio for a real-time "War Room" dashboard.

1. Prerequisites

Python 3.8 or higher

pip

2. Installation

Clone the repository and install the required UI library:

git clone [https://github.com/yourusername/FinSense.git](https://github.com/yourusername/FinSense.git)
cd FinSense
pip install gradio


3. Running the Simulation

Launch the interactive dashboard:

python main.py


4. Demo Scenarios

Once the UI is running, enter these specific keywords into the "Stock Ticker" box to trigger the different autonomous paths:

GOOGL -> Standard Success Path (Buy)

POLICY_REJECT_DEMO -> Strategic Correction (Risk Reject -> Resize -> Approve)

MARKET_FREEZE_DEMO -> Market Correction (Freeze -> News Analysis -> Liquidation)

SLOW_PROCESS_DEMO -> Process Correction (Slow Val -> Fast Val -> Execution)

🔮 Future Scope

Real API Integration: Replace mock logic with live Bloomberg/Alpaca APIs.

Vector Memory: Implement Pinecone/ChromaDB for long-term strategy recall.

Reinforcement Learning: Allow the Orchestrator to "learn" which correction paths yield the highest profit over time.

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
