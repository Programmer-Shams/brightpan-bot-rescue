"""Load the help center into a local Chroma index. Run once: python bot/ingest.py"""
import sys
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from envfile import load_env, require  # noqa: E402

KB_FILE = ROOT / "kb" / "help-center-v1.md"
CHROMA_DIR = ROOT / "chroma"
COLLECTION = "brightpan"
EMBED_MODEL = "text-embedding-3-small"


def embeddings():
    env = load_env()
    require(env, "OPENAI_API_KEY")
    return OpenAIEmbeddings(model=EMBED_MODEL, api_key=env["OPENAI_API_KEY"])


def main():
    docs = [Document(page_content=KB_FILE.read_text(), metadata={"source": KB_FILE.name})]
    chunks = CharacterTextSplitter(separator="", chunk_size=250, chunk_overlap=0).split_documents(docs)
    Chroma.from_documents(chunks, embeddings(), collection_name=COLLECTION, persist_directory=str(CHROMA_DIR))
    print(f"Indexed {len(chunks)} chunks from {KB_FILE.name} into {CHROMA_DIR.name}/")


if __name__ == "__main__":
    main()
