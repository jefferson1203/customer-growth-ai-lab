"""
voc/dry_run_v3.py - Test à blanc sur 5 avis avec le prompt v3, item_id et un cache séparé.
"""

import json
import os
import sys
from pathlib import Path
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import DATA_RAW
from common.data import load_olist
from common.llm import LLMClient
from voc.schema import ReviewLabel

PROMPT_V3_PATH = "prompts/voc_classification_v3.txt"
DRY_RUN_CACHE_PATH = Path("outputs/voc/cache/dry_run_v3_test.json")


def dry_run():
    print("--- DÉBUT TEST À BLANC PROMPT V3 (5 AVIS) ---")
    data = load_olist(DATA_RAW)
    df_reviews = data["reviews"].dropna(subset=["review_comment_message"]).copy()
    
    sample_5 = df_reviews.head(5)

    client = LLMClient(prompt_path=PROMPT_V3_PATH, cache_path=DRY_RUN_CACHE_PATH)

    results = []
    for idx, row in sample_5.iterrows():
        review_text = row["review_comment_message"]
        review_id = row["review_id"]

        print(f"\n[Avis {review_id}] Texte: {review_text[:100]}...")
        label = client.complete_json(
            variables={"review_text": review_text},
            cache_key=review_id,
            schema=ReviewLabel
        )
        print(f" -> Classification : Irritants={label.irritants} | Sentiment={label.sentiment} | Urgence={label.urgence}")
        print(f" -> Résumé : {label.resume_fr}")

        results.append({
            "item_id": review_id,
            "review_id": review_id,
            "comment": review_text,
            "irritants": label.irritants,
            "sentiment": label.sentiment,
            "urgence": label.urgence,
            "resume_fr": label.resume_fr
        })

    print(f"\nTotal d'appels réels à l'API Gemini : {client.call_count}")
    print("--- FIN DU TEST À BLANC ---")


if __name__ == "__main__":
    dry_run()
