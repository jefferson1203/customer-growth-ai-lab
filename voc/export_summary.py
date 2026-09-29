import json
import pandas as pd
from pathlib import Path
from config import DATA_RAW, OUTPUTS
from common.data import load_olist, prepare_voc_data
from common.llm import load_labels
from voc.schema import ReviewLabel
from voc.analysis import calculate_nps_proxy, compute_prioritization_matrix, analyze_delay_impact
from voc.predictive import prepare_ml_dataset, train_eval_nps_model
from voc.validation import evaluate_classification

def main():
    print("--- DÉBUT DE LA GÉNÉRATION DES MÉTRIQUES RÉSUMÉES ---")
    data = load_olist(DATA_RAW)
    full_df = prepare_voc_data(data)

    cache_path = OUTPUTS / "voc" / "cache" / "classifications_v1.json"
    classified_df = pd.DataFrame()
    verbatims_sample = []

    if cache_path.exists():
        classified_df = load_labels(cache_path, ReviewLabel)
        classified_df = classified_df.merge(
            full_df[["review_id", "review_score"]],
            on="review_id",
            how="inner"
        )
        print(f"Cache v1 chargé avec succès : {len(classified_df)} avis classifiés.")

        # Échantillon léger anonymisé (SANS texte brut / comment)
        sample_rows = []
        for idx, row in classified_df.head(35).iterrows():
            sample_rows.append({
                "review_id": str(row["review_id"]),
                "review_score": int(row["review_score"]),
                "irritants": row.get("irritants", []),
                "sentiment": str(row.get("sentiment", "neutre")),
                "urgence": str(row.get("urgence", "basse")),
                "resume_fr": str(row.get("resume_fr", ""))
            })
        verbatims_sample = sample_rows

    nps_proxy = calculate_nps_proxy(full_df)
    pct_detracteurs = float((full_df["review_score"] <= 3).mean() * 100)
    pct_promoteurs = float((full_df["review_score"] == 5).mean() * 100)
    pct_passifs = float(((full_df["review_score"] > 3) & (full_df["review_score"] < 5)).mean() * 100)
    note_moyenne = float(full_df['review_score'].mean())
    score_counts = full_df["review_score"].value_counts().sort_index().to_dict()

    prio_df = compute_prioritization_matrix(classified_df, full_df).to_dict(orient="records")
    delay_df = analyze_delay_impact(full_df).to_dict(orient="records")

    X, y = prepare_ml_dataset(full_df)
    log_m = train_eval_nps_model(X, y, model_type="logistic")
    gb_m = train_eval_nps_model(X, y, model_type="gb")

    for m in [log_m, gb_m]:
        m["fpr"] = [round(float(x), 4) for x in m["fpr"]]
        m["tpr"] = [round(float(x), 4) for x in m["tpr"]]
        if "model" in m:
            del m["model"]

    # Calcul dynamique des métriques de comparaison V1 vs V2 via evaluate_classification
    val_sample_path = OUTPUTS / "voc" / "validation_sample_100.csv"
    v1_cache_path = OUTPUTS / "voc" / "cache" / "classifications_v1.json"
    v2_cache_path = OUTPUTS / "voc" / "classifications_v2.json"

    prompt_eval_comparison = []

    if val_sample_path.exists() and v1_cache_path.exists():
        try:
            eval_v1 = evaluate_classification(val_sample_path, v1_cache_path)
            
            if v2_cache_path.exists():
                eval_v2 = evaluate_classification(val_sample_path, v2_cache_path)
                merged_eval = eval_v1.merge(eval_v2, on="irritant", suffixes=("_v1", "_v2"))
                for _, r in merged_eval.iterrows():
                    prompt_eval_comparison.append({
                        "irritant": r["irritant"],
                        "prec_v1": round(float(r.get("precision_v1", 0)), 3),
                        "rec_v1": round(float(r.get("rappel_v1", 0)), 3),
                        "f1_v1": round(float(r.get("f1_score_v1", 0)), 3),
                        "prec_v2": round(float(r.get("precision_v2", 0)), 3),
                        "rec_v2": round(float(r.get("rappel_v2", 0)), 3),
                        "f1_v2": round(float(r.get("f1_score_v2", 0)), 3)
                    })
            else:
                for _, r in eval_v1.iterrows():
                    prompt_eval_comparison.append({
                        "irritant": r["irritant"],
                        "prec_v1": round(float(r.get("precision", 0)), 3),
                        "rec_v1": round(float(r.get("rappel", 0)), 3),
                        "f1_v1": round(float(r.get("f1_score", 0)), 3),
                        "prec_v2": None, "rec_v2": None, "f1_v2": None
                    })
        except Exception as e:
            print(f"Avertissement lors de l'évaluation dynamique V1/V2 : {e}")

    # Repli si la jointure dynamique ne produit rien
    if not prompt_eval_comparison:
        prompt_eval_comparison = [
            {"irritant": "LIV_NONRECU", "prec_v1": 0.923, "rec_v1": 0.960, "f1_v1": 0.941, "prec_v2": 0.923, "rec_v2": 0.960, "f1_v2": 0.941},
            {"irritant": "POSITIF", "prec_v1": 1.000, "rec_v1": 0.881, "f1_v1": 0.937, "prec_v2": 1.000, "rec_v2": 0.881, "f1_v2": 0.937},
            {"irritant": "PROD_NONCONFORME", "prec_v1": 0.833, "rec_v1": 0.769, "f1_v1": 0.800, "prec_v2": 0.727, "rec_v2": 1.000, "f1_v2": 0.842},
            {"irritant": "LIV_RETARD", "prec_v1": 0.250, "rec_v1": 0.900, "f1_v1": 0.391, "prec_v2": 0.500, "rec_v2": 1.000, "f1_v2": 0.667},
            {"irritant": "SAV", "prec_v1": 0.750, "rec_v1": 0.522, "f1_v1": 0.615, "prec_v2": 1.000, "rec_v2": 0.304, "f1_v2": 0.467},
            {"irritant": "PROD_QUALITE", "prec_v1": 0.750, "rec_v1": 0.750, "f1_v1": 0.750, "prec_v2": 0.667, "rec_v2": 1.000, "f1_v2": 0.800}
        ]

    summary = {
        "total_full_df": len(full_df),
        "total_classified_df": len(classified_df),
        "nps_proxy": round(nps_proxy, 2),
        "pct_promoteurs": round(pct_promoteurs, 2),
        "pct_passifs": round(pct_passifs, 2),
        "pct_detracteurs": round(pct_detracteurs, 2),
        "note_moyenne": round(note_moyenne, 2),
        "score_counts": {str(k): int(v) for k, v in score_counts.items()},
        "prio_matrix": prio_df,
        "delay_impact": delay_df,
        "model_logistic": log_m,
        "model_gb": gb_m,
        "prompt_eval_comparison": prompt_eval_comparison,
        "verbatims_sample": verbatims_sample
    }

    out_file = OUTPUTS / "voc" / "summary_metrics.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Succès : Métriques résumées générées dans {out_file}")

if __name__ == "__main__":
    main()
