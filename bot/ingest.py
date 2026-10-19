"""Keep a local Chroma index of the help center in sync with the file.

One document per help-center article (each "## [Axx] Title" section), stored under its article id; the text
before the first article (store name, where it ships from, product lines) is article A00, "About Brightpan".
Run once to build it: python bot/ingest.py. The app also calls ensure_index() before every answer:
when the help-center file's hash differs from the manifest, only the articles whose hash changed are re-indexed.
"""
import hashlib
import json
import re
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from envfile import load_env, require  # noqa: E402

KB_FILE = ROOT / "kb" / "help-center-v2.md"
CHROMA_DIR = ROOT / "chroma"
MANIFEST = CHROMA_DIR / "manifest.json"
COLLECTION = "brightpan"
EMBED_MODEL = "text-embedding-3-small"
CHUNKING = "article+intro"  # index format; a manifest built with another format triggers a full rebuild
_HEADING = re.compile(r"^## \[(A\d+)\] (.+)$", re.M)
INTRO_ID, INTRO_TITLE = "A00", "About Brightpan"
_lock = threading.Lock()


def embeddings():
    env = load_env()
    require(env, "OPENAI_API_KEY")
    return OpenAIEmbeddings(model=EMBED_MODEL, api_key=env["OPENAI_API_KEY"])


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def split_articles(text: str) -> list:
    parts = _HEADING.split(text)
    articles = [{"article_id": parts[i], "title": parts[i + 1].strip(), "content": parts[i + 2].strip()}
                for i in range(1, len(parts), 3)]
    intro = re.sub(r"^# .*$", "", parts[0], count=1, flags=re.M).strip()  # drop the page title line
    if intro:
        articles.insert(0, {"article_id": INTRO_ID, "title": INTRO_TITLE, "content": intro})
    for a in articles:
        a["sha256"] = sha256(a["title"] + "\n" + a["content"])
    return articles


def check_articles(articles: list) -> None:
    """Refuse a help-center file that would empty or break the index."""
    ids = [a["article_id"] for a in articles if a["article_id"] != INTRO_ID]
    if not ids:
        raise ValueError("no '## [Axx] Title' articles found")
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"duplicate article ids: {', '.join(duplicates)}")


def article_hashes(text: str) -> dict:
    return {a["article_id"]: a["sha256"] for a in split_articles(text)}


def read_manifest() -> dict:
    try:
        return json.loads(MANIFEST.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def build(vectorstore: Chroma, text: str) -> dict:
    """Bring the index in line with the help center and write the manifest. Returns the new manifest."""
    previous = read_manifest()
    articles = split_articles(text)
    check_articles(articles)
    new = {a["article_id"]: a["sha256"] for a in articles}
    full = previous.get("chunking") != CHUNKING
    old = {} if full else previous.get("articles", {})
    changed = sorted(a for a in new.keys() | old.keys() if new.get(a) != old.get(a))
    if full:
        vectorstore.reset_collection()
    elif changed:
        vectorstore.delete(ids=[a for a in changed if a in old])
    docs = [Document(page_content=f"{a['title']}\n\n{a['content']}",
                     metadata={"article_id": a["article_id"], "title": a["title"], "source": KB_FILE.name})
            for a in articles if a["article_id"] in changed]
    if docs:
        vectorstore.add_documents(docs, ids=[d.metadata["article_id"] for d in docs])
    manifest = {
        "file": KB_FILE.name,
        "file_sha256": sha256(text),
        "index_version": sha256(text)[:12],
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "chunking": CHUNKING,
        "articles": new,
        "changed_articles": changed,
        "chunks": len(articles),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    return manifest


def ensure_index(vectorstore: Chroma) -> str:
    """Re-index if the help-center file changed since the last build. Returns the index version."""
    text = KB_FILE.read_text()
    manifest = read_manifest()
    if manifest.get("file_sha256") == sha256(text) and manifest.get("chunking") == CHUNKING:
        return manifest["index_version"]
    with _lock:
        manifest = read_manifest()
        if manifest.get("file_sha256") != sha256(text) or manifest.get("chunking") != CHUNKING:
            try:
                manifest = build(vectorstore, text)
            except ValueError as e:
                if not manifest:
                    raise
                print(f"NOT re-indexing {KB_FILE.name}: {e}. Still answering from version "
                      f"{manifest['index_version']}.", file=sys.stderr, flush=True)
                return manifest["index_version"]
            print(f"Re-indexed {KB_FILE.name}: version {manifest['index_version']}, "
                  f"changed articles: {', '.join(manifest['changed_articles']) or 'none'}", flush=True)
        return manifest["index_version"]


def open_vectorstore() -> Chroma:
    return Chroma(collection_name=COLLECTION, embedding_function=embeddings(), persist_directory=str(CHROMA_DIR))


def main():
    m = build(open_vectorstore(), KB_FILE.read_text())
    print(f"Indexed {m['chunks']} articles from {m['file']} (version {m['index_version']}); "
          f"changed articles: {', '.join(m['changed_articles']) or 'none'}")


if __name__ == "__main__":
    main()
