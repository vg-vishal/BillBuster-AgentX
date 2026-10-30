"""Offline tests (no API key). Run: python -m unittest discover tests"""
import json
import subprocess
import sys
import unittest

from agent.core import AgentExecutor, parse_json
from tools import build_tools


class Scripted:
    def __init__(self, replies):
        self.replies = list(replies)

    def generate(self, system, messages):
        return self.replies.pop(0) if self.replies else '{"final_answer": "done"}'


class AgentTests(unittest.TestCase):
    def test_parse_json_handles_fences(self):
        self.assertEqual(parse_json('text ```json\n{"a": 1}\n``` more'), {"a": 1})

    def test_tool_call_then_final(self):
        llm = Scripted(['{"thought":"t","action":"read_file","args":{"filename":"scores.csv"}}',
                        '{"thought":"t","final_answer":"recursion is weak"}'])
        answer, trace = AgentExecutor(llm, build_tools()).run("q")
        self.assertEqual(answer, "recursion is weak")
        self.assertEqual(trace[0]["tool"], "read_file")
        self.assertIn("recursion", trace[0]["observation"])

    def test_tool_error_becomes_observation(self):
        llm = Scripted(['{"action":"read_file","args":{"filename":"nope.csv"}}', '{"final_answer":"x"}'])
        _, trace = AgentExecutor(llm, build_tools()).run("q")
        self.assertTrue(trace[0]["observation"].startswith("ERROR"))

    def test_iteration_cap(self):
        llm = Scripted(['{"action":"list_files","args":{}}'] * 20)
        answer, trace = AgentExecutor(llm, build_tools(), max_iterations=3).run("q")
        self.assertLessEqual(len(trace), 3)

    def test_sql_and_calculator(self):
        t = build_tools()
        self.assertIn("recursion", t["sql_query"].execute(filename="scores.csv", sql="SELECT topic FROM data WHERE score < 40"))
        self.assertEqual(t["calculator"].execute(expression="2+2*10"), 22)

    def test_cli_contract(self):
        out = subprocess.run([sys.executable, "main.py", "--json", "--dry-run", "hi"], capture_output=True, text=True)
        d = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertTrue(d["answer"] and len(d["trace"]) >= 2)


if __name__ == "__main__":
    unittest.main()
