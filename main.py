"""Entry point.
  python main.py "your question"            human-readable run (shows Thought/Action/Observation)
  python main.py --json "your question"     machine output: ONE JSON line (the judges' harness uses this)
  python main.py --dry-run "anything"       test your setup without an API key
Contract: stdout = {"answer": str, "trace": [{"thought","tool","args","observation"}]}; logs go to stderr.
"""
import argparse
import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from agent.core import AgentExecutor  # noqa: E402
from agent.llm import LLM, DryRunLLM  # noqa: E402
from tools import build_tools  # noqa: E402


def run_agent(query, dry_run=False, verbose=False):
    llm = DryRunLLM() if dry_run else LLM()
    return AgentExecutor(llm, build_tools()).run(query, verbose=verbose)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--json", action="store_true", help="print the judges' JSON contract to stdout")
    ap.add_argument("--dry-run", action="store_true", help="scripted LLM, no API key needed")
    a = ap.parse_args()
    try:
        answer, trace = run_agent(a.query, a.dry_run or bool(os.environ.get("AGENTX_DRY_RUN")), verbose=not a.json)
    except Exception as e:  # never crash silently: always return a valid answer object
        answer, trace = f"Agent error: {type(e).__name__}: {e}", []
        print(answer, file=sys.stderr)
    if a.json:
        print(json.dumps({"answer": answer, "trace": trace}))
    else:
        print(f"\nANSWER: {answer}")


if __name__ == "__main__":
    main()
