"""
voc/run_v3_eval.py - Évaluation empirique du Prompt V3 sur 50 avis inédits.
"""

import os
import sys
import pandas as pd
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import DATA_RAW, OUTPUTS
from common.data import load_olist, prepare_voc_data
from common.llm import LLMClient
from voc.schema import ReviewLabel

PROMPT_V3_PATH = "prompts/voc_classification_v3.txt"
CACHE_V3_PATH = OUTPUTS / "voc" / "cache" / "classifications_v3_eval50.json"


def evaluate_v3_on_fresh_sample():
    print("--- ÉVALUATION empirique PROMPT V3 SUR 50 AVIS INÉDITS ---")
    data = load_olist(DATA_RAW)
    full_df = prepare_voc_data(data)

    # Chargement de l'échantillon de validation historique (100 avis) pour l'exclure
    val_100_path = OUTPUTS / "voc" / "validation_sample_100.csv"
    excluded_ids = set()
    if val_100_path.exists():
        excluded_ids = set(pd.read_csv(val_100_path)["review_id"].astype(str))

    # Filtrage des avis non vus lors de l'ajustement du prompt
    fresh_reviews = full_df[~full_df["review_id"].astype(str).isin(excluded_ids)].dropna(subset=["review_comment_message"])
    
    # Échantillon de 50 avis inédits avec seed fixe
    sample_50 = fresh_reviews.sample(n=50, random_state=123).copy()

    client = LLMClient(prompt_path=PROMPT_V3_PATH, cache_path=CACHE_V3_PATH)

    results = []
    print(f"Lancement de la classification pour {len(sample_50)} avis inédits...")

    for idx, row in sample_50.reset_index(drop=True).iterrows():
        review_id = str(row["review_id"])
        review_text = row["review_comment_message"]

        label = client.complete_json(
            variables={"review_text": review_text},
            cache_key=review_id,
            schema=ReviewLabel
        )

        results.append({
            "review_id": review_id,
            "review_score": row["review_score"],
            "comment": review_text,
            "irritants": label.irritants,
            "sentiment": label.sentiment,
            "urgence": label.urgence,
            "resume_fr": label.resume_fr
        })

    eval_df = pd.DataFrame(results)

    print(f"\nTotal d'appels API effectués : {client.call_count}")
    print("\n--- DISTRIBUTION DES IRRITANTS PRÉDITS PAR PROMPT V3 (50 AVIS) ---")
    all_irritants = eval_df["irritants"].explode().value_counts()
    print(all_irritants.to_string())

    sav_count = (eval_df["irritants"].apply(lambda x: "SAV" in x if isinstance(x, list) else False)).sum()
    print(f"\nNombre d'avis identifiés avec le motif 'SAV' : {sav_count} / 50 ({sav_count/50*100:.1f}%)")

    return eval_df


if __name__ == "__main__":
    evaluate_v3_on_fresh_sample()
