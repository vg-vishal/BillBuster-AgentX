# 🤖 BillBuster: The Agentic Expense Auditor & Anomaly Hunter

**AgentX Challenge 2026 | Track: Finance & Risk**
**Team:** Innovators (AGX-16)

## 💡 The Problem
Traditional finance apps only show you a static pie chart of your spending. They don't take action. People waste thousands on duplicate charges and silent price hikes.

## 🚀 The Solution: BillBuster
BillBuster is an **autonomous AI agent** that reads UPI transaction data, detects anomalies (duplicates, spend surges), explains its reasoning, and proposes a personalized, rebalanced budget plan.

### 🧠 Key Agentic Capabilities
1. **Perception:** Reads the Kaggle UPI dataset (`data/upi_transactions_2024.csv`).
2. **Reasoning & Tool Use:** Uses a custom Python tool (`expense_auditor`) to scan the data for anomalies.
3. **Action:** Outputs a step-by-step trace of its thoughts and a final JSON budget plan.

## 🛠️ Tech Stack
* **Backend:** Python, Pandas, Groq API (LLM)
* **Frontend:** Streamlit
* **Template:** Official AgentX Starter (ReAct Loop)

## 💻 How to Run (For Judges)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt