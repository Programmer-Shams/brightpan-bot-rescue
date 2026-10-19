"""Keep a local Chroma index of the help center in sync with the file.

Run once to build it: python bot/ingest.py. The app also calls ensure_index() before every answer:
when the help-center file's hash differs from the manifest, it re-indexes and records which articles changed.
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
from langchain_text_splitters import CharacterTextSplitter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from envfile import load_env, require  # noqa: E402

KB_FILE = ROOT / "kb" / "help-center-v2.md"
CHROMA_DIR = ROOT / "chroma"
MANIFEST = CHROMA_DIR / "manifest.json"
COLLECTION = "brightpan"
EMBED_MODEL = "text-embedding-3-small"
_HEADING = re.compile(r"^## \[(A\d+)\] (.+)$", re.M)
_lock = threading.Lock()


def embeddings():
    env = load_env()
    require(env, "OPENAI_API_KEY")
    return OpenAIEmbeddings(model=EMBED_MODEL, api_key=env["OPENAI_API_KEY"])


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def article_hashes(text: str) -> dict:
    parts = _HEADING.split(text)
    return {parts[i]: sha256(parts[i + 1] + parts[i + 2]) for i in range(1, len(parts), 3)}


def read_manifest() -> dict:
    try:
        return json.loads(MANIFEST.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def build(vectorstore: Chroma, text: str) -> dict:
    """Re-index the whole help center and write the manifest. Returns the new manifest."""
    old = read_manifest().get("articles", {})
    new = article_hashes(text)
    docs = [Document(page_content=text, metadata={"source": KB_FILE.name})]
    chunks = CharacterTextSplitter(separator="", chunk_size=250, chunk_overlap=0).split_documents(docs)
    vectorstore.reset_collection()
    vectorstore.add_documents(chunks)
    manifest = {
        "file": KB_FILE.name,
        "file_sha256": sha256(text),
        "index_version": sha256(text)[:12],
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "articles": new,
        "changed_articles": sorted(a for a in new.keys() | old.keys() if new.get(a) != old.get(a)),
        "chunks": len(chunks),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    return manifest


def ensure_index(vectorstore: Chroma) -> str:
    """Re-index if the help-center file changed since the last build. Returns the index version."""
    text = KB_FILE.read_text()
    manifest = read_manifest()
    if manifest.get("file_sha256") == sha256(text):
        return manifest["index_version"]
    with _lock:
        manifest = read_manifest()
        if manifest.get("file_sha256") != sha256(text):
            manifest = build(vectorstore, text)
            print(f"Re-indexed {KB_FILE.name}: version {manifest['index_version']}, "
                  f"changed articles: {', '.join(manifest['changed_articles']) or 'none'}", flush=True)
        return manifest["index_version"]


def open_vectorstore() -> Chroma:
    return Chroma(collection_name=COLLECTION, embedding_function=embeddings(), persist_directory=str(CHROMA_DIR))


def main():
    m = build(open_vectorstore(), KB_FILE.read_text())
    print(f"Indexed {m['chunks']} chunks from {m['file']} (version {m['index_version']}); "
          f"changed articles: {', '.join(m['changed_articles']) or 'none'}")


if __name__ == "__main__":
    main()
