"""Thin wrapper over the free LLM APIs. Picks Gemini or Groq from your environment."""
import json
import os
import time

import config


class LLM:
    def __init__(self, provider=None):
        self.provider = provider or os.environ.get("AGENTX_PROVIDER") or (
            "gemini" if os.environ.get("GEMINI_API_KEY") else "groq" if os.environ.get("GROQ_API_KEY") else None)
        if self.provider is None:
            raise RuntimeError("No API key found. Set GEMINI_API_KEY or GROQ_API_KEY in .env (both are free).")
        if self.provider == "gemini":
            from google import genai
            self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        else:
            from groq import Groq
            self.client = Groq(api_key=os.environ["GROQ_API_KEY"])

    def generate(self, system, messages):
        """messages: list of {"role": "user"|"assistant", "content": str}. Returns text. Retries on 429."""
        for attempt in range(4):
            try:
                return self._call(system, messages)
            except Exception as e:
                converted = self._native_tool_call_as_json(e)
                if converted:
                    return converted
                # rate limit: back off and retry, otherwise surface the error
                if attempt < 3 and ("429" in str(e) or "rate" in str(e).lower() or "quota" in str(e).lower()):
                    time.sleep(2 * 2 ** attempt)
                    continue
                raise

    @staticmethod
    def _native_tool_call_as_json(e):
        """Groq's gpt-oss sometimes emits a native tool call, which the API rejects (400 tool_use_failed).
        Turn that into our JSON action so the agent loop keeps going (unknown tool names are reported back)."""
        try:
            body = e.response.json()["error"]
            if body.get("code") != "tool_use_failed":
                return None
            call = json.loads(body["failed_generation"])
            return json.dumps({"thought": "(native tool call)", "action": str(call["name"]).split(".")[-1],
                               "args": call.get("arguments") or {}})
        except Exception:
            return None

    def _call(self, system, messages):
        if self.provider == "gemini":
            from google.genai import types
            text = "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
            r = self.client.models.generate_content(
                model=config.GEMINI_MODEL, contents=text,
                config=types.GenerateContentConfig(system_instruction=system, temperature=config.TEMPERATURE))
            return r.text or ""
        r = self.client.chat.completions.create(
            model=config.GROQ_MODEL, temperature=config.TEMPERATURE,
            messages=[{"role": "system", "content": system}] + messages)
        msg = r.choices[0].message
        # some Groq reasoning models (gpt-oss) leave `content` empty and put the reply in `reasoning`
        return msg.content or getattr(msg, "reasoning", None) or ""


class DryRunLLM:
    """Scripted stand-in so you can test your setup with NO API key: python main.py --dry-run "..." """

    def __init__(self):
        self.step = 0

    def generate(self, system, messages):
        self.step += 1
        if self.step == 1:
            return '{"thought": "See which data files exist.", "action": "list_files", "args": {}}'
        if self.step == 2:
            return '{"thought": "Check a calculation.", "action": "calculator", "args": {"expression": "2 + 2 * 10"}}'
        return '{"thought": "I have enough.", "final_answer": "Dry run OK: tools executed (list_files, calculator)."}'
