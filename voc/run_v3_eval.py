import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from config import OUTPUTS
from common.llm import LLMClient, ReviewLabel
from voc.validation import evaluate_classification

load_dotenv()

def run_v3_evaluation():
    val_sample_path = Path("outputs/voc/validation_sample_100.csv")
    if not val_sample_path.exists():
        print("Fichier outputs/voc/validation_sample_100.csv non trouvé.")
        return

    val_df = pd.read_csv(val_sample_path)
    print(f"Chargement de {len(val_df)} avis pour évaluation empirique avec Prompt V3...")

    # Fichier de cache dédié v3
    cache_v3_path = OUTPUTS / "voc" / "cache" / "classifications_v3.json"
    llm_client = LLMClient(cache_path=cache_v3_path)

    count = 0
    for idx, row in val_df.iterrows():
        review_id = str(row["review_id"])
        review_text = row["review_comment_message"]

        cache_key_check = f"voc_classification_v3:{llm_client.cache_path}:{review_id}"
        if cache_key_check not in llm_client.cache:
            try:
                print(f"[{idx+1}/100] Traitement avis {review_id} via Gemini (v3)...")
                res = llm_client.complete_json(
                    prompt_name="voc_classification_v3",
                    variables={"review_text": review_text},
                    schema=ReviewLabel,
                    cache_key=review_id
                )
                count += 1
            except Exception as e:
                print(f"Erreur sur {review_id}: {e}")

    print(f"\n{count} nouveaux avis classifiés avec le Prompt V3.")
    print("\n--- RÉSULTATS RÉELS DU PROMPT V3 ---")
    
    metrics_v3_df = evaluate_classification(val_sample_path, cache_v3_path)
    print(metrics_v3_df.to_string(index=False))

if __name__ == "__main__":
    run_v3_evaluation()
