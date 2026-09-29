"""
voc/migrate_cache.py - Migration stricte du cache v1 avec validation Pydantic et item_id générique.
"""

import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.llm import get_prompt_hash
from voc.schema import ReviewLabel

OLD_CACHE_PATH = "outputs/voc/cache_classifications_v1.json"
NEW_CACHE_PATH = "outputs/voc/cache/classifications_v1.json"
ORIGINAL_PROMPT_PATH = "prompts/archive/voc_classification_v1_original.txt"

# MODÈLE DES CLASSIFICATIONS V1 :
# Valeur de LLM["model"] dans config.py au moment de la classification (28/09/2026) : "gemini-3.8-flash"
MODEL_NAME = "gemini-3.8-flash"
PROMPT_NAME = "voc_classification"


def migrate():
    # Si le cache originel a été déplacé dans outputs/voc/cache_classifications_v1.json
    if not os.path.exists(OLD_CACHE_PATH) and os.path.exists(NEW_CACHE_PATH):
        print(f"Information : {NEW_CACHE_PATH} existe déjà.")
        source_path = NEW_CACHE_PATH
    else:
        source_path = OLD_CACHE_PATH

    if not os.path.exists(source_path):
        print(f"Erreur : Aucun fichier source de cache trouvé à {source_path}.")
        sys.exit(1)

    if not os.path.exists(ORIGINAL_PROMPT_PATH):
        print(f"Erreur : Fichier prompt original introuvable : {ORIGINAL_PROMPT_PATH}")
        sys.exit(1)

    with open(ORIGINAL_PROMPT_PATH, "r", encoding="utf-8") as f:
        prompt_raw = f.read()

    prompt_hash = get_prompt_hash(prompt_raw)

    with open(source_path, "r", encoding="utf-8") as f:
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
            print(f"Avertissement : Entrée invalide ignorée pour {item_id} ({e})")
            invalid_count += 1
            continue

        new_cache[composite_key] = {
            "item_id": item_id,
            "prompt": PROMPT_NAME,
            "prompt_hash": prompt_hash,
            "model": MODEL_NAME,
            "data": clean_data
        }

    os.makedirs(os.path.dirname(NEW_CACHE_PATH), exist_ok=True)
    tmp_path = Path(NEW_CACHE_PATH).with_name(Path(NEW_CACHE_PATH).name + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(new_cache, f, ensure_ascii=False, indent=2)
    tmp_path.replace(NEW_CACHE_PATH)

    print(f"Migration terminée : {len(new_cache)} entrées valides migré(es) vers {NEW_CACHE_PATH} ({invalid_count} invalides).")


if __name__ == "__main__":
    migrate()
