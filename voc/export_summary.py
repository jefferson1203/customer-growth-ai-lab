import json
import pandas as pd
from pathlib import Path
from config import DATA_RAW, OUTPUTS
from common.data import load_olist, prepare_voc_data
from voc.analysis import calculate_nps_proxy, compute_prioritization_matrix, analyze_delay_impact
from voc.predictive import prepare_ml_dataset, train_eval_nps_model

def main():
    data = load_olist(DATA_RAW)
    full_df = prepare_voc_data(data)

    cache_path = OUTPUTS / "voc" / "classifications.jsonl"
    classified_df = pd.DataFrame()
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
        classified_df = pd.DataFrame([{"review_id": k, **v} for k, v in cache_data.items()])
        classified_df = classified_df.merge(full_df[["review_id", "review_score"]], on="review_id", how="inner")

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

    prompt_eval_comparison = [
        {"irritant": "LIV_NONRECU", "prec_v1": 0.923, "rec_v1": 0.960, "f1_v1": 0.941, "prec_v2": 0.923, "rec_v2": 0.960, "f1_v2": 0.941, "impact": "Excellente stabilité sur l'irritant majeur #1"},
        {"irritant": "POSITIF", "prec_v1": 1.000, "rec_v1": 0.881, "f1_v1": 0.937, "prec_v2": 1.000, "rec_v2": 0.881, "f1_v2": 0.937, "impact": "Zéro fausse alerte sur les avis positifs"},
        {"irritant": "PROD_NONCONFORME", "prec_v1": 0.833, "rec_v1": 0.769, "f1_v1": 0.800, "prec_v2": 0.727, "rec_v2": 1.000, "f1_v2": 0.842, "impact": "Rappel parfait (1.00) sur la non-conformité"},
        {"irritant": "LIV_RETARD", "prec_v1": 0.250, "rec_v1": 0.900, "f1_v1": 0.391, "prec_v2": 0.500, "rec_v2": 1.000, "f1_v2": 0.667, "impact": "Précision doublée (0.25 -> 0.50) via désambiguïsation"},
        {"irritant": "SAV", "prec_v1": 0.750, "rec_v1": 0.522, "f1_v1": 0.615, "prec_v2": 1.000, "rec_v2": 0.304, "f1_v2": 0.467, "impact": "Précision 100% mais arbitrage conservateur sur le rappel"},
        {"irritant": "PROD_QUALITE", "prec_v1": 0.750, "rec_v1": 0.750, "f1_v1": 0.750, "prec_v2": 0.667, "rec_v2": 1.000, "f1_v2": 0.800, "impact": "Gain de +5 points de F1-score"}
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
        "prompt_eval_comparison": prompt_eval_comparison,
        "ml_results": {
            "logistic": log_m,
            "gb": gb_m
        },
        "verbatims_sample": classified_df[["review_id", "review_score", "irritants", "resume_fr", "sentiment", "urgence"]].head(20).to_dict(orient="records")
    }

    summary_path = OUTPUTS / "voc" / "summary_metrics.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("summary_metrics.json généré avec succès!")

if __name__ == "__main__":
    main()
