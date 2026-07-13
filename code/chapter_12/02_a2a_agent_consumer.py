import json

import requests

# 1) discover
card = requests.get("http://localhost:8080/.well-known/ai-agent.json")
endpoint = card["url"]  # e.g. "http://localhost:8080"

# 2) send a task (A2A message in JSON-RPC form)
payload = {
    "jsonrpc": "2.0",
    "id": "task-1",
    "method": "tasks/send",
    "params": {"task": {"input": "Explain RAG in one sentence"}},
}
print(requests.post(endpoint, json=payload).json())
