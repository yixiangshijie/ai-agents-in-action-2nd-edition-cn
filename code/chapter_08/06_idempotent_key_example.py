# chapter_08/08_idempotent_tool_inputs.py
import asyncio
import hashlib
import json

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Idempotent-by-Inputs Tool Proxy")


class ToolIn(BaseModel):
    name: str
    args: dict


CACHE: dict[str, dict] = {}  # demo only


def cache_key_from_inputs(name: str, args: dict) -> str:  # A
    """
    Build a deterministic key directly from function inputs.
    Canonicalize JSON to ensure stable ordering of dict keys.
    """
    canon = json.dumps(
        {"name": name, "args": args},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


@app.post("/tool")
async def call_tool(body: ToolIn):  # B
    key = cache_key_from_inputs(body.name, body.args)  # C

    if key in CACHE:
        return {"cached": True, "result": CACHE[key], "key": key}  # D

    # Fake tool execution (replace with real call)
    await asyncio.sleep(1.0)  # E
    result = {"ok": True, "tool": body.name, "echo": body.args}

    CACHE[key] = result  # F
    return {"cached": False, "result": result, "key": key}
