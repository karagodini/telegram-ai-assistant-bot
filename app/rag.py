import os
from glob import glob

from chromadb import PersistentClient
from fastembed import TextEmbedding

from . import config

SUPPORTED = {".txt", ".pdf", ".md"}

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def _read_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def _chunk(text: str) -> list[str]:
    size, overlap = config.CHUNK_SIZE, config.CHUNK_OVERLAP
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += size - overlap
    return [c.strip() for c in chunks if c.strip()]


class KnowledgeBase:
    """RAG по документам: чанкинг + векторный поиск (всё локально)."""

    def __init__(self) -> None:
        self.client = PersistentClient(path=config.CHROMA_DIR)
        self.col = self.client.get_or_create_collection("docs")
        self.embedder = TextEmbedding(model_name=EMBED_MODEL)

    def rebuild(self) -> int:
        self.client.delete_collection("docs")
        self.col = self.client.get_or_create_collection("docs")
        total = 0
        for path in glob(os.path.join(config.DATA_DIR, "**", "*"), recursive=True):
            if os.path.splitext(path)[1].lower() not in SUPPORTED:
                continue
            text = _read_file(path)
            for i, chunk in enumerate(_chunk(text)):
                vec = next(iter(self.embedder.embed([chunk])))
                self.col.add(
                    ids=[f"{os.path.basename(path)}:{i}"],
                    embeddings=[vec],
                    documents=[chunk],
                    metadatas=[{"source": os.path.basename(path)}],
                )
                total += 1
        return total

    def ask(self, question: str) -> tuple[str, list[str]]:
        if self.col.count() == 0:
            return "", []
        qvec = next(iter(self.embedder.embed([question])))
        result = self.col.query(
            query_embeddings=[qvec], n_results=config.TOP_K
        )
        chunks = result["documents"][0]
        sources = sorted({m["source"] for m in result["metadatas"][0]})
        context = "\n\n".join(f"[{i+1}] {c}" for i, c in enumerate(chunks))
        return context, sources
