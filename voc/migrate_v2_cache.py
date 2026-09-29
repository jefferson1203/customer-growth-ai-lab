"""
voc/migrate_v2_cache.py - Migration stricte du cache v2 vers le format unifié.
"""

import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.llm import get_prompt_hash
from voc.schema import ReviewLabel

OLD_V2_CACHE_PATH = "outputs/voc/classifications_v2.json"
NEW_V2_CACHE_PATH = "outputs/voc/cache/classifications_v2.json"
PROMPT_V2_PATH = "prompts/voc_classification_v2.txt"

MODEL_NAME = "gemini-3.8-flash"
PROMPT_NAME = "voc_classification_v2"


def migrate_v2():
    if not os.path.exists(OLD_V2_CACHE_PATH):
        print(f"Erreur : Fichier {OLD_V2_CACHE_PATH} introuvable.")
        sys.exit(1)

    with open(PROMPT_V2_PATH, "r", encoding="utf-8") as f:
        prompt_raw = f.read()

    prompt_hash = get_prompt_hash(prompt_raw)

    with open(OLD_V2_CACHE_PATH, "r", encoding="utf-8") as f:
        old_cache = json.load(f)

    new_cache = {}
    invalid_count = 0

    for raw_key, val in old_cache.items():
        item_id = val.get("item_id") or val.get("review_id") or (raw_key.split(":")[-1] if ":" in raw_key else raw_key)
        composite_key = f"{PROMPT_NAME}:{prompt_hash}:{MODEL_NAME}:{item_id}"

        data_payload = val.get("data", val) if isinstance(val, dict) else val

        try:
            validated_obj = ReviewLabel(**data_payload)
            clean_data = validated_obj.model_dump()
        except Exception as e:
            print(f"Avertissement : Entrée v2 invalide pour {item_id} ({e})")
            invalid_count += 1
            continue

        new_cache[composite_key] = {
            "item_id": item_id,
            "prompt": PROMPT_NAME,
            "prompt_hash": prompt_hash,
            "model": MODEL_NAME,
            "data": clean_data
        }

    os.makedirs(os.path.dirname(NEW_V2_CACHE_PATH), exist_ok=True)
    tmp_path = Path(NEW_V2_CACHE_PATH).with_name(Path(NEW_V2_CACHE_PATH).name + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(new_cache, f, ensure_ascii=False, indent=2)
    tmp_path.replace(NEW_V2_CACHE_PATH)

    print(f"Migration V2 terminée : {len(new_cache)} entrées valides migré(es) vers {NEW_V2_CACHE_PATH} ({invalid_count} invalides).")


if __name__ == "__main__":
    migrate_v2()
