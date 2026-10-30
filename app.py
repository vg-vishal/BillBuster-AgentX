import streamlit as st
import subprocess
import json

st.set_page_config(page_title="BillBuster AI", page_icon="🤖", layout="wide")

st.title("🤖 BillBuster: Agentic Expense Auditor")
st.markdown("**Team Innovators | AgentX Challenge 2026**")
st.write("Click the button below to let the autonomous AI agent scan the UPI dataset, detect anomalies, and generate a rebalanced budget plan.")

if st.button("🚀 Run Expense Audit", type="primary"):
    with st.spinner("Agent is thinking, scanning data, and finding anomalies..."):
        result = subprocess.run(
            ["python", "main.py", "--json", "Audit my UPI transactions and find anomalies"],
            capture_output=True,
            text=True
        )
        
        try:
            output = json.loads(result.stdout)
            st.success("✅ Audit Complete!")
            
            st.write("### 🧠 Agent Thought Trace")
            for step in output["trace"]:
                with st.expander(f"Thought: {step['thought']}", expanded=True):
                    st.code(f"Tool: {step['tool']}\nArgs: {json.dumps(step['args'])}\nObservation: {step['observation']}")
            
            st.write("### 📊 Final Financial Report")
            st.info(output["answer"])
            
        except Exception as e:
            st.error(f"Error parsing agent output: {e}")
            st.text(result.stdout)