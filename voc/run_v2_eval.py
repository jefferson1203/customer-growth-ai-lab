import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from config import OUTPUTS, PROMPTS, LLM
from common.llm import LLMClient, ReviewLabel
from voc.validation import evaluate_classification

load_dotenv()

def run_v2_evaluation():
    val_sample_path = Path("outputs/voc/validation_sample_100.csv")
    if not val_sample_path.exists():
        print("Fichier outputs/voc/validation_sample_100.csv non trouvé.")
        return

    val_df = pd.read_csv(val_sample_path)
    print(f"Chargement de {len(val_df)} avis pour ré-évaluation avec Prompt V2...")

    # Initialisation du client LLM avec un cache v2 séparé
    cache_v2_path = OUTPUTS / "voc" / "classifications_v2.json"
    cache_v2 = {}
    if cache_v2_path.exists():
        with open(cache_v2_path, "r", encoding="utf-8") as f:
            cache_v2 = json.load(f)

    llm_client = LLMClient(OUTPUTS)
    
    # Remplacer temporairement le cache avec cache_v2
    llm_client.cache = cache_v2

    count = 0
    for idx, row in val_df.iterrows():
        review_id = str(row["review_id"])
        review_text = row["review_comment_message"]

        if review_id not in llm_client.cache:
            try:
                print(f"[{idx+1}/100] Traitement avis {review_id} via Gemini (v2)...")
                res = llm_client.complete_json(
                    prompt_name="voc_classification_v2",
                    variables={"review_text": review_text},
                    schema=ReviewLabel,
                    cache_key=review_id
                )
                count += 1
            except Exception as e:
                print(f"Erreur sur {review_id}: {e}")

    # Sauvegarder cache v2
    cache_v2_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_v2_path, "w", encoding="utf-8") as f:
        json.dump(llm_client.cache, f, indent=2, ensure_ascii=False)

    print(f"\n{count} nouveaux avis classifiés avec le Prompt V2.")
    print("\n--- RÉSULTATS RÉELS DU PROMPT V2 (COMPARAISON EMBIRIQUE) ---")
    
    metrics_v2_df = evaluate_classification(val_sample_path, cache_v2_path)
    print(metrics_v2_df.to_string(index=False))

if __name__ == "__main__":
    run_v2_evaluation()
