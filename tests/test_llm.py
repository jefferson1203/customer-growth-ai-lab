"""
tests/test_llm.py - Tests unitaires pour le client LLM et load_labels
"""

import json
from pathlib import Path
import pytest
from unittest.mock import MagicMock
from pydantic import BaseModel, Field

from common.llm import LLMClient, load_labels, get_prompt_hash


class DummySchema(BaseModel):
    label: str = Field(..., description="Label de test")
    score: int = Field(..., description="Score de test")


@pytest.fixture
def tmp_prompt_path(tmp_path):
    prompt_file = tmp_path / "test_prompt.txt"
    prompt_file.write_text("Analyse : $review_text", encoding="utf-8")
    return prompt_file


@pytest.fixture
def tmp_cache_path(tmp_path):
    return tmp_path / "test_cache.json"


def test_cache_hit_with_path_object(tmp_prompt_path, tmp_cache_path):
    with open(tmp_prompt_path, "r", encoding="utf-8") as f:
        prompt_raw = f.read()
    p_hash = get_prompt_hash(prompt_raw)

    comp_key = f"test_prompt:{p_hash}:gemini-3.8-flash:item_123"
    existing_cache = {
        comp_key: {
            "item_id": "item_123",
            "prompt": "test_prompt",
            "prompt_hash": p_hash,
            "model": "gemini-3.8-flash",
            "data": {"label": "LIV_RETARD", "score": 5}
        }
    }
    with open(tmp_cache_path, "w", encoding="utf-8") as f:
        json.dump(existing_cache, f)

    # Test avec des objets pathlib.Path
    client = LLMClient(prompt_path=tmp_prompt_path, cache_path=tmp_cache_path)
    client.client = MagicMock()

    res = client.complete_json(
        variables={"review_text": "Retard 3 jours"},
        cache_key="item_123",
        schema=DummySchema
    )

    assert res.label == "LIV_RETARD"
    assert res.score == 5
    client.client.models.generate_content.assert_not_called()


def test_corrupted_cache_raises_error(tmp_prompt_path, tmp_path):
    corrupted_cache = tmp_path / "corrupted_cache.json"
    corrupted_cache.write_text("{ ce json est invalide", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        LLMClient(prompt_path=tmp_prompt_path, cache_path=corrupted_cache)


def test_load_labels_valid_and_duplicates(tmp_path):
    cache_file = tmp_path / "cache_valid.json"
    data = {
        "k1": {
            "item_id": "r1",
            "prompt": "p1",
            "model": "m1",
            "data": {"label": "PRIX", "score": 1}
        }
    }
    cache_file.write_text(json.dumps(data), encoding="utf-8")

    df = load_labels(cache_file, DummySchema)
    assert len(df) == 1
    assert df.iloc[0]["item_id"] == "r1"

    # Test de détection de doublon
    data_dup = {
        "k1": {
            "item_id": "r1",
            "data": {"label": "PRIX", "score": 1}
        },
        "k2": {
            "item_id": "r1",
            "data": {"label": "SAV", "score": 2}
        }
    }
    cache_dup_file = tmp_path / "cache_dup.json"
    cache_dup_file.write_text(json.dumps(data_dup), encoding="utf-8")

    with pytest.raises(ValueError, match="Doublon d'identifiant"):
        load_labels(cache_dup_file, DummySchema)
