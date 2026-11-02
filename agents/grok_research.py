
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

API_KEY = os.environ.get("XAI_API_KEY")
PROMPT = os.environ.get("GROK_PROMPT")
MODEL = "grok-4.7"

if not API_KEY:
    raise SystemExit("Missing XAI_API_KEY secret.")

if not PROMPT:
    raise SystemExit("Missing GROK_PROMPT research instructions.")

payload = {
    "model": MODEL,
    "input": PROMPT,
    "store": False,
    "max_output_tokens": 1200
}

request = urllib.request.Request(
    "https://api.x.ai/v1/responses",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(request, timeout=90) as response:
        result = json.loads(response.read().decode("utf-8"))

    answer = result.get("output_text", "")

    if not answer:
        parts = []
        for item in result.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    parts.append(content.get("text", ""))
        answer = "\n".join(parts)

    if not answer:
        raise SystemExit("Grok returned no readable research text.")

    Path("grok-research-result.md").write_text(
        "# Grok Research Results\n\n" + answer + "\n",
        encoding="utf-8"
    )

    print("Research completed. Result saved securely as an artifact.")
    print(answer)

 except urllib.error.HTTPError as error:
    print("Grok API returned HTTP status:", error.code)
    details = error.read().decode("utf-8", errors="replace")
    print("API error details:", details[:3000])
    raise SystemExit("Research request failed.")