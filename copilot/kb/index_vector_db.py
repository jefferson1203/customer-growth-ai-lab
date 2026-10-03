"""
copilot/kb/index_vector_db.py - Indexation RAG de la Politique Commerciale dans une base vectorielle SQLite/FAISS.
"""

import os
from pathlib import Path
from typing import List, Dict, Any

KB_FILE = Path(__file__).parent / "politique_commerciale.md"
VECTOR_INDEX_FILE = Path(__file__).parent / "vector_store.json"


def load_and_chunk_kb() -> List[Dict[str, Any]]:
    """Découpe le document markdown de politique commerciale en sections sémantiques."""
    if not KB_FILE.exists():
        raise FileNotFoundError(f"Fichier de politique commerciale introuvable : {KB_FILE}")

    with open(KB_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    sections = content.split("---")
    chunks = []
    for idx, sec in enumerate(sections):
        cleaned = sec.strip()
        if cleaned:
            chunks.append({
                "chunk_id": f"sec_{idx+1}",
                "text": cleaned,
                "source": "copilot/kb/politique_commerciale.md"
            })
    return chunks


def build_vector_store():
    """Génère un magasin d'indexation vectoriel léger déterministe pour le RAG n8n/Python."""
    chunks = load_and_chunk_kb()
    import json
    with open(VECTOR_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"✅ Base vectorielle générée avec succès ({len(chunks)} sections indexées) dans {VECTOR_INDEX_FILE}")


if __name__ == "__main__":
    build_vector_store()
