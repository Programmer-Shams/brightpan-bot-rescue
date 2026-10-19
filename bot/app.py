"""Brightpan support chatbot: FastAPI /chat endpoint backed by a LangChain agent.

Run: .venv/bin/uvicorn bot.app:app --port 8004
Request and response shape match the Demo 1 endpoint, so eval/run_eval.py works against it.
"""
import json
import re
import sys
import threading
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import FastAPI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "bot"))
sys.path.insert(0, str(ROOT / "scripts"))
from envfile import load_env  # noqa: E402
from ingest import ensure_index, open_vectorstore  # noqa: E402

MODEL = load_env().get("OPENAI_MODEL", "gpt-5.5")
SYSTEM_PROMPT = (ROOT / "bot" / "system_prompt.md").read_text()
STORE_TZ = ZoneInfo("America/New_York")
MAX_AGENT_STEPS = 12  # model and tool steps per message; stops runaway tool loops

LOG_FILE = ROOT / "logs" / "chat.log"
HANDOFFS = ROOT / "logs" / "handoffs.jsonl"  # stands in for the support team's queue
ORDERS = {o["order_number"]: o for o in json.loads((ROOT / "data" / "orders.json").read_text())}


# Created on first use, so importing this module (for the unit tests) needs no API key.
@lru_cache(maxsize=1)
def vectorstore():
    return open_vectorstore()


@lru_cache(maxsize=1)
def llm():
    return ChatOpenAI(model=MODEL, reasoning_effort="low", use_responses_api=True, timeout=30, max_retries=1,
                      api_key=load_env()["OPENAI_API_KEY"])


@tool(response_format="content_and_artifact")
def search_help_center(query: str) -> tuple[str, list]:
    """Search the Brightpan help center for shipping, returns, refunds, warranty, care and payment info.
    Returns the 4 closest articles; each starts with its id and exact title, like "[A05] Returns policy"."""
    docs = vectorstore().as_retriever(search_kwargs={"k": 4}).invoke(query)
    if not docs:
        return "No results.", []
    articles = [{"id": d.metadata["article_id"], "title": d.metadata["title"]} for d in docs]
    text = "\n\n---\n\n".join(f"[{d.metadata['article_id']}] {d.page_content}" for d in docs)
    return text, articles


# "(Source: Returns policy)", "(Sources: A; B)" or a closing "Source: A" line; titles may hold one level of
# parentheses.
_CITATION = re.compile(r"\(Sources?:\s*((?:[^()]|\([^()]*\))*)\)|^\s*Sources?:\s*(.+)$", re.I | re.M)
_MIN_PREFIX = 0.6  # a shortened title must keep at least 60% of the real one, and match only one article


def _match_title(name: str, titles: list) -> str | None:
    name = re.sub(r"[*_\"“”‘’]", "", name).strip().rstrip(".").lower()
    if len(name) < 4:
        return None
    exact = [aid for aid, t in titles if t == name]
    if exact:
        return exact[0]
    prefix = [aid for aid, t in titles if t.startswith(name) and len(name) >= _MIN_PREFIX * len(t)]
    return prefix[0] if len(prefix) == 1 else None


def cited_articles(answer: str, retrieved: dict) -> list:
    """Article ids the answer cites by title, among the articles the search returned."""
    titles = [(aid, title.lower()) for aid, title in retrieved.items()]
    cited = []
    for match in _CITATION.finditer(answer):
        for part in (match.group(1) or match.group(2) or "").split(";"):
            hit = _match_title(part, titles)
            # "A, B" or "A and B" in one part: try the pieces, since titles can themselves contain "and" or ",".
            hits = [hit] if hit else [_match_title(p, titles) for p in re.split(r",|\band\b", part)]
            for h in hits:
                if h and h not in cited:
                    cited.append(h)
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
_lookup_lock = threading.Lock()


@tool
def lookup_order(order_number: str, email: str) -> str:
    """Look up a Brightpan order. Needs the order number AND the email address used at checkout, both exactly as
    the customer wrote them. If the customer hasn't given both, ask for the missing one instead of calling this."""
    number = order_number.strip().lstrip("#")
    now = time.time()
    with _lookup_lock:
        if len(failed_lookups) > 1000:  # forget numbers whose lockout window has passed
            for key in [k for k, ts in failed_lookups.items() if all(now - t >= LOCKOUT_SECONDS for t in ts)]:
                del failed_lookups[key]
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


_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_handoff_lock = threading.Lock()
session_handoffs: dict[str, dict[str, bool]] = {}  # per session: hand-off id -> has an email to reply to


def make_escalate_tool(session_id: str):
    """escalate_to_human, bound to one chat session so it can only update that session's hand-offs."""

    @tool
    def escalate_to_human(
        summary: str,
        reason: Literal["refund", "damaged_or_wrong_item", "warranty", "order_change", "complaint", "other"],
        email: str = "",
        order_number: str = "",
        handoff_id: str = "",
    ) -> str:
        """Hand the case to the support team, who reply by email within 1 business day. Give a short factual
        summary, plus the customer's email and order number if they gave them. To add an email or order number to
        a hand-off made earlier in this conversation, pass its handoff_id."""
        email, order_number = email.strip()[:200], order_number.strip().lstrip("#")[:20]
        entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "session_id": session_id,
                 "email": email, "order_number": order_number}
        with _handoff_lock:
            if handoff_id:
                if handoff_id not in session_handoffs.get(session_id, {}):
                    return json.dumps({"result": "unknown_handoff", "message": "No hand-off with that id in this "
                                       "conversation. Create a new one without a handoff_id."})
                entry.update(handoff_id=handoff_id, update=True)
            else:
                entry["handoff_id"] = f"H-{uuid.uuid4().hex[:10]}"
            entry.update(reason=reason, summary=summary.strip()[:1000])
            has_email = session_handoffs.setdefault(session_id, {}).get(entry["handoff_id"], False)
            session_handoffs[session_id][entry["handoff_id"]] = has_email or bool(_EMAIL.fullmatch(email))
            HANDOFFS.parent.mkdir(exist_ok=True)
            with HANDOFFS.open("a") as f:
                f.write(json.dumps(entry) + "\n")
        if _EMAIL.fullmatch(email):
            message = "Saved for the support team. They reply by email within 1 business day."
        else:
            message = ("Saved for the support team, but there is no email address to reply to. Ask the customer for "
                       "the email address the team should use; when they give it, call escalate_to_human again with "
                       "this handoff_id and the email. Don't say the team will email them until then.")
        return json.dumps({"result": "saved", "handoff_id": entry["handoff_id"],
                           "contact": "email" if _EMAIL.fullmatch(email) else "missing", "message": message})

    return escalate_to_human


def handoff_note(session_id: str) -> str:
    """Tell the model about this conversation's hand-offs that still have no email to reply to."""
    with _handoff_lock:
        waiting = [h for h, has_email in session_handoffs.get(session_id, {}).items() if not has_email]
    if not waiting:
        return ""
    return (f"\n\nIn this conversation you already handed off {', '.join(waiting)} without an email address. If the "
            "customer now gives the email for that case, call escalate_to_human with that handoff_id and the email. "
            "A different problem is a new hand-off: call escalate_to_human without a handoff_id.")


# Short per-session memory so follow-ups ("my email is …") work. Plain user/assistant text only.
HISTORY_TURNS, HISTORY_TTL, MAX_SESSIONS = 10, 30 * 60, 1000
_history: dict[str, tuple[float, list]] = {}
_history_lock = threading.Lock()


def get_history(session_id: str) -> list:
    now = time.time()
    with _history_lock:
        expired = [s for s, (seen, _) in _history.items() if now - seen > HISTORY_TTL]
        for sid in expired:
            del _history[sid]
        turns = list(_history.get(session_id, (now, []))[1])
    with _handoff_lock:
        for sid in expired:
            session_handoffs.pop(sid, None)
    return turns


def save_turn(session_id: str, message: str, answer: str) -> None:
    with _history_lock:
        turns = _history.get(session_id, (0, []))[1] + [{"role": "user", "content": message},
                                                         {"role": "assistant", "content": answer}]
        _history[session_id] = (time.time(), turns[-2 * HISTORY_TURNS:])
        if len(_history) > MAX_SESSIONS:
            del _history[min(_history, key=lambda s: _history[s][0])]


def store_today(requested: str | None) -> str:
    """The request's date if it is a real YYYY-MM-DD date, else today in the store's time zone."""
    if requested and re.fullmatch(r"\d{4}-\d{2}-\d{2}", requested):
        try:
            return date.fromisoformat(requested).isoformat()
        except ValueError:  # e.g. 2026-99-99
            pass
    return datetime.now(STORE_TZ).date().isoformat()


@asynccontextmanager
async def lifespan(_app):
    ensure_index(vectorstore())
    yield


app = FastAPI(lifespan=lifespan)


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


def summarize(messages: list) -> dict:
    """Tools used, order lookup outcome, hand-off and retrieved articles, from this turn's messages."""
    out = {"tools_called": [], "lookup": None, "order": None, "handoff_id": None, "retrieved": {}}
    for m in messages:
        for call in getattr(m, "tool_calls", None) or []:
            out["tools_called"].append(call["name"])
        if m.type != "tool":
            continue
        try:
            result = json.loads(m.content) if m.name != "search_help_center" else {}
        except json.JSONDecodeError:
            result = {}
        if m.name == "lookup_order":
            if result.get("result") == "match":
                out["lookup"] = "match"
                out["order"] = {k: result["order"][k] for k in ("order_number", "fulfillment_status")}
            elif out["lookup"] != "match":
                out["lookup"] = "no_match"
        elif m.name == "search_help_center":
            for a in getattr(m, "artifact", None) or []:
                out["retrieved"].setdefault(a["id"], a["title"])
        elif m.name == "escalate_to_human" and result.get("result") == "saved":
            out["handoff_id"] = result["handoff_id"]
    return out


@app.post("/chat")
def chat(req: ChatRequest):
    started = time.perf_counter()
    index_version = None
    try:
        index_version = ensure_index(vectorstore())
        prompt = SYSTEM_PROMPT.replace("{{TODAY}}", store_today(req.today)) + handoff_note(req.session_id)
        tools = [search_help_center, lookup_order, make_escalate_tool(req.session_id)]
        history = get_history(req.session_id)
        agent = create_agent(llm(), tools, system_prompt=prompt)
        result = agent.invoke({"messages": history + [{"role": "user", "content": req.message}]},
                              config={"recursion_limit": MAX_AGENT_STEPS})
        turn = result["messages"][len(history):]
        answer = turn[-1].text.strip()
        s = summarize(turn)
        cited = cited_articles(answer, s["retrieved"])
        save_turn(req.session_id, req.message, answer)
        reply = {
            "answer": answer,
            "session_id": req.session_id,
            "tools_called": s["tools_called"],
            "article_ids_used": cited,
            "article_ids_retrieved": list(s["retrieved"]),
            "sources": [{"id": a, "title": s["retrieved"][a]} for a in cited],
            "lookup": s["lookup"],
            "lookup_verified": s["lookup"] == "match",
            "order": s["order"],
            "handoff_id": s["handoff_id"],
            "escalated": s["handoff_id"] is not None,
            "latency_ms": round((time.perf_counter() - started) * 1000),
            "model": MODEL,
            "index_version": index_version,
            "error": False,
        }
    except GraphRecursionError:
        reply = {"answer": "I couldn't finish looking that up. Could you rephrase the question? I can also connect you "
                           "with the support team.", "session_id": req.session_id, "index_version": index_version,
                 "error": True, "latency_ms": round((time.perf_counter() - started) * 1000)}
    except Exception:
        traceback.print_exc()
        reply = {"answer": "Sorry, something went wrong. Please try again.", "session_id": req.session_id,
                 "index_version": index_version, "error": True,
                 "latency_ms": round((time.perf_counter() - started) * 1000)}
    log_turn(reply)
    return reply
