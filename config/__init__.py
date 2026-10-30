"""Runtime settings. Change these, not the code."""
import os

MAX_ITERATIONS = 6          # hard cap on reasoning steps (the judges check for a guard like this)
MAX_SAME_TOOL_CALLS = 2     # same tool + same args more than this => force a final answer
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")  # Groq retires models; override via .env
TEMPERATURE = 0.2
DATA_DIR = os.environ.get("AGENTX_DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))
