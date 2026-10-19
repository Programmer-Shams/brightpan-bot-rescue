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


# What a verified customer may see about their own order: no name, email or address.
ORDER_FIELDS = ("order_number", "created", "fulfillment_status", "financial_status", "carrier", "tracking_number",
                "shipped_date", "delivered_date", "country", "subtotal", "shipping", "note")
ITEM_FIELDS = ("title", "qty", "status", "final_sale")
NO_MATCH = json.dumps({"result": "no_match", "message": "No order matches that order number and email. Share no "
                       "order details; ask the customer to check both and try again."})
LOCKED = json.dumps({"result": "locked", "message": "Too many failed attempts for this order number. Share no order "
                     "details; ask the customer to contact the support team."})
MAX_FAILED_LOOKUPS, LOCKOUT_SECONDS = 5, 15 * 60
failed_lookups: dict[str, list[float]] = {}


@tool
def lookup_order(order_number: str, email: str) -> str:
    """Look up a Brightpan order. Needs the order number AND the email address used at checkout, both exactly as
    the customer wrote them. If the customer hasn't given both, ask for the missing one instead of calling this."""
    number = order_number.strip().lstrip("#")
    now = time.time()
    recent = [t for t in failed_lookups.get(number, []) if now - t < LOCKOUT_SECONDS]
    if len(recent) >= MAX_FAILED_LOOKUPS:
        return LOCKED
    order = ORDERS.get(number)
    if not order or order["email"].strip().lower() != email.strip().lower():
        # A wrong email and an unknown number get the same reply, so nothing is revealed either way.
        failed_lookups[number] = recent + [now]
        return NO_MATCH
    failed_lookups.pop(number, None)
    view = {k: order[k] for k in ORDER_FIELDS if order.get(k) is not None}
    view["items"] = [{k: i[k] for k in ITEM_FIELDS if k in i} for i in order["items"]]
    return json.dumps({"result": "match", "order": view})


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
            result = json.loads(m.content)
            if result["result"] == "match":
                lookup = "match"
                order = {k: result["order"][k] for k in ("order_number", "fulfillment_status")}
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
        "lookup_verified": lookup == "match",
        "order": order,
        "handoff_id": None,
        "escalated": False,
        "latency_ms": round((time.perf_counter() - started) * 1000),
        "model": MODEL,
        "error": False,
    }
