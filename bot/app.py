"""Brightpan support chatbot: FastAPI /chat endpoint backed by a LangChain agent.

Run: .venv/bin/uvicorn bot.app:app --port 8003
Request and response shape match the Demo 1 endpoint, so eval/run_eval.py works against it.
"""
import json
import re
import sys
import threading
import time
import traceback
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "bot"))
sys.path.insert(0, str(ROOT / "scripts"))
from envfile import load_env  # noqa: E402
from ingest import ensure_index, open_vectorstore  # noqa: E402

MODEL = load_env().get("OPENAI_MODEL", "gpt-5.5")
SYSTEM_PROMPT = (ROOT / "bot" / "system_prompt.md").read_text()

LOG_FILE = ROOT / "logs" / "chat.log"
HANDOFFS = ROOT / "logs" / "handoffs.jsonl"  # stands in for the support team's queue
ORDERS = {o["order_number"]: o for o in json.loads((ROOT / "data" / "orders.json").read_text())}
vectorstore = open_vectorstore()
ensure_index(vectorstore)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model=MODEL, reasoning_effort="low", use_responses_api=True, api_key=load_env()["OPENAI_API_KEY"])


@tool(response_format="content_and_artifact")
def search_help_center(query: str) -> tuple[str, list]:
    """Search the Brightpan help center for shipping, returns, refunds, warranty, care and payment info.
    Returns the 4 closest articles; each starts with its id and exact title, like "[A05] Returns policy"."""
    docs = retriever.invoke(query)
    if not docs:
        return "No results.", []
    articles = [{"id": d.metadata["article_id"], "title": d.metadata["title"]} for d in docs]
    text = "\n\n---\n\n".join(f"[{d.metadata['article_id']}] {d.page_content}" for d in docs)
    return text, articles


# "(Source: Returns policy)" or "(Sources: A; B)"; titles may hold one level of parentheses.
_CITATION = re.compile(r"\(Sources?:\s*((?:[^()]|\([^()]*\))*)\)", re.I)


def cited_articles(answer: str, retrieved: dict) -> list:
    """Article ids the answer cites by title, among the articles the search returned."""
    titles = [(aid, title.lower()) for aid, title in retrieved.items()]
    cited = []
    for match in _CITATION.finditer(answer):
        for part in match.group(1).split(";"):
            name = part.strip().rstrip(".").lower()
            if len(name) < 4:
                continue
            hit = next((t for t in titles if t[1] == name), None) or next(
                (t for t in titles if t[1].startswith(name) or name.startswith(t[1])), None)
            if hit and hit[0] not in cited:
                cited.append(hit[0])
    return cited


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


_handoff_lock = threading.Lock()


@tool
def escalate_to_human(
    summary: str,
    reason: Literal["refund", "damaged_or_wrong_item", "warranty", "order_change", "complaint", "other"],
    email: str = "",
    order_number: str = "",
) -> str:
    """Hand the case to the support team, who reply by email within 1 business day. Give a short factual summary,
    plus the customer's email and order number if they gave them."""
    handoff = {
        "handoff_id": f"H-{uuid.uuid4().hex[:10]}",
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "reason": reason,
        "summary": summary.strip()[:1000],
        "email": email.strip()[:200],
        "order_number": order_number.strip().lstrip("#")[:20],
    }
    with _handoff_lock:
        HANDOFFS.parent.mkdir(exist_ok=True)
        with HANDOFFS.open("a") as f:
            f.write(json.dumps(handoff) + "\n")
    return json.dumps({"result": "saved", "handoff_id": handoff["handoff_id"],
                       "message": "Saved for the support team. They reply by email within 1 business day."})


TOOLS = [search_help_center, lookup_order, escalate_to_human]
app = FastAPI()


class ChatRequest(BaseModel):
    session_id: str
    message: str
    today: str | None = None


def log_turn(reply: dict) -> None:
    """One JSON line per answer: which help-center version it used, never the message text."""
    keys = ("session_id", "index_version", "tools_called", "article_ids_used", "lookup", "escalated", "latency_ms",
            "error")
    entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **{k: reply.get(k) for k in keys}}
    LOG_FILE.parent.mkdir(exist_ok=True)
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(entry) + "\n")


@app.post("/chat")
def chat(req: ChatRequest):
    started = time.perf_counter()
    index_version = None
    try:
        index_version = ensure_index(vectorstore)
        today = req.today if req.today and re.fullmatch(r"\d{4}-\d{2}-\d{2}", req.today) else date.today().isoformat()
        prompt = SYSTEM_PROMPT.replace("{{TODAY}}", today)
        agent = create_agent(llm, TOOLS, system_prompt=prompt)
        result = agent.invoke({"messages": [{"role": "user", "content": req.message}]})
    except Exception:
        traceback.print_exc()
        reply = {"answer": "Sorry, something went wrong. Please try again.", "session_id": req.session_id,
                 "index_version": index_version, "error": True,
                 "latency_ms": round((time.perf_counter() - started) * 1000)}
        log_turn(reply)
        return reply

    messages = result["messages"]
    tools_called, lookup, order, handoff_id, retrieved = [], None, None, None, {}
    for m in messages:
        for call in getattr(m, "tool_calls", None) or []:
            tools_called.append(call["name"])
        if m.type == "tool" and m.name == "lookup_order":
            try:
                found = json.loads(m.content)
            except json.JSONDecodeError:
                found = {"result": "error"}
            if found.get("result") == "match":
                lookup = "match"
                order = {k: found["order"][k] for k in ("order_number", "fulfillment_status")}
            elif lookup != "match":
                lookup = "no_match"
        if m.type == "tool" and m.name == "search_help_center":
            for a in getattr(m, "artifact", None) or []:
                retrieved.setdefault(a["id"], a["title"])
        if m.type == "tool" and m.name == "escalate_to_human":
            try:
                handoff_id = json.loads(m.content).get("handoff_id") or handoff_id
            except json.JSONDecodeError:
                pass

    answer = messages[-1].text.strip()
    cited = cited_articles(answer, retrieved)
    reply = {
        "answer": answer,
        "session_id": req.session_id,
        "tools_called": tools_called,
        "article_ids_used": cited,
        "article_ids_retrieved": list(retrieved),
        "sources": [{"id": a, "title": retrieved[a]} for a in cited],
        "lookup": lookup,
        "lookup_verified": lookup == "match",
        "order": order,
        "handoff_id": handoff_id,
        "escalated": handoff_id is not None,
        "latency_ms": round((time.perf_counter() - started) * 1000),
        "model": MODEL,
        "index_version": index_version,
        "error": False,
    }
    log_turn(reply)
    return reply
