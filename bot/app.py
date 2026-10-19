"""Brightpan support chatbot: FastAPI /chat endpoint backed by a LangChain agent.

Run: .venv/bin/uvicorn bot.app:app --port 8003
Request and response shape match the Demo 1 endpoint, so eval/run_eval.py works against it.
"""
import json
import sys
import time
import traceback
from pathlib import Path

from fastapi import FastAPI
from langchain.agents import create_agent
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "bot"))
sys.path.insert(0, str(ROOT / "scripts"))
from envfile import load_env  # noqa: E402
from ingest import CHROMA_DIR, COLLECTION, embeddings  # noqa: E402

MODEL = load_env().get("OPENAI_MODEL", "gpt-5.5")
SYSTEM_PROMPT = "You are a helpful assistant for Brightpan. Answer the customer's question."

ORDERS = {o["order_number"]: o for o in json.loads((ROOT / "data" / "orders.json").read_text())}
vectorstore = Chroma(collection_name=COLLECTION, embedding_function=embeddings(), persist_directory=str(CHROMA_DIR))
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
llm = ChatOpenAI(model=MODEL, reasoning_effort="low", use_responses_api=True, api_key=load_env()["OPENAI_API_KEY"])


@tool
def search_help_center(query: str) -> str:
    """Search the Brightpan help center for shipping, returns, refunds, warranty, care and payment info."""
    docs = retriever.invoke(query)
    return docs[0].page_content if docs else "No results."


@tool
def lookup_order(order_number: str) -> str:
    """Look up a Brightpan order by its order number."""
    order = ORDERS.get(order_number.strip().lstrip("#"))
    return json.dumps(order) if order else "Order not found."


TOOLS = [search_help_center, lookup_order]
app = FastAPI()


class ChatRequest(BaseModel):
    session_id: str
    message: str
    today: str | None = None


@app.post("/chat")
def chat(req: ChatRequest):
    started = time.perf_counter()
    try:
        prompt = SYSTEM_PROMPT + (f"\nToday's date: {req.today}." if req.today else "")
        agent = create_agent(llm, TOOLS, system_prompt=prompt)
        result = agent.invoke({"messages": [{"role": "user", "content": req.message}]})
    except Exception:
        traceback.print_exc()
        return {"answer": "Sorry, something went wrong. Please try again.", "session_id": req.session_id,
                "error": True, "latency_ms": round((time.perf_counter() - started) * 1000)}

    messages = result["messages"]
    tools_called, lookup, order = [], None, None
    for m in messages:
        for call in getattr(m, "tool_calls", None) or []:
            tools_called.append(call["name"])
        if m.type == "tool" and m.name == "lookup_order":
            if m.content.startswith("{"):
                lookup, found = "match", json.loads(m.content)
                order = {"order_number": found["order_number"], "fulfillment_status": found["fulfillment_status"]}
            elif lookup != "match":
                lookup = "no_match"

    return {
        "answer": messages[-1].text.strip(),
        "session_id": req.session_id,
        "tools_called": tools_called,
        "article_ids_used": [],
        "article_ids_retrieved": [],
        "sources": [],
        "lookup": lookup,
        "order": order,
        "handoff_id": None,
        "escalated": False,
        "latency_ms": round((time.perf_counter() - started) * 1000),
        "model": MODEL,
        "error": False,
    }
