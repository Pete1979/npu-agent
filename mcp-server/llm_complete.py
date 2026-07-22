#!/usr/bin/env python3
"""Read a prompt from stdin, print one completion from the local NPU LLM (Lemonade).

Usage: printf '%s' "$PROMPT" | python3 llm_complete.py [model]
Env: LEMONADE_BASE_URL, LEMONADE_API_KEY, LOCAL_LLM_MODEL
"""
import os
import re
import sys

import requests

BASE = os.environ.get("LEMONADE_BASE_URL", "http://localhost:13305/api/v1")
KEY = os.environ.get("LEMONADE_API_KEY", "lemonade")
MODEL = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("LOCAL_LLM_MODEL", "qwen3.6-moe-35b-a3b-FLM")

prompt = sys.stdin.read()
try:
    r = requests.post(
        f"{BASE}/chat/completions",
        headers={"Authorization": f"Bearer {KEY}"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "stream": False,
        },
        timeout=600,
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"].get("content") or ""
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    print(content)
except Exception as e:  # noqa: BLE001
    print(f"[local LLM error contacting {BASE}: {e}]", file=sys.stderr)
    sys.exit(1)
