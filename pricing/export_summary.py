import json
import datetime
from pathlib import Path
import pandas as pd
import numpy as np

from config import DATA_RAW, OUTPUTS, PRICING
from common.data import load_retail
from pricing.pricing_analysis import run_pricing_diagnostic
from pricing.data_prep import prepare_weekly_pricing_data
from pricing.elasticity import compute_sku_elasticity
from pricing.optimization import optimize_sku_prices, run_sensitivity_analysis
from pricing.llm_justification import generate_pricing_justifications


def export_pricing_summary() -> tuple[dict, Path, Path]:
    """Exécute le pipeline unifié du Projet 3 et génère le fichier JSON et le modèle Excel.

    Returns:
        tuple[dict, Path, Path]: (summary_metrics, json_path, excel_path)
    """
    print("⏳ [PRICING EXPORT] 1/6. Chargement des données brutes Online Retail II...")
    df_clean, _ = load_retail(DATA_RAW)

    print("⏳ [PRICING EXPORT] 2/6. Audit du diagnostic de la politique tarifaire...")
    diagnostic = run_pricing_diagnostic(df_clean)

    print("⏳ [PRICING EXPORT] 3/6. Agrégation hebdomadaire & filtrage des SKUs...")
    df_weekly, sku_stats = prepare_weekly_pricing_data(df_clean, config=PRICING)

    print("⏳ [PRICING EXPORT] 4/6. Modélisation Log-Log des élasticités-prix...")
    df_elasticity = compute_sku_elasticity(df_weekly, sku_stats)

    print("⏳ [PRICING EXPORT] 5/6. Optimisation sous garde-fous & analyse de sensibilité...")
    df_opt = optimize_sku_prices(df_elasticity, config=PRICING, cost_ratio=0.50)
    sensitivity = run_sensitivity_analysis(df_elasticity, config=PRICING)

    print("⏳ [PRICING EXPORT] 6/6. Génération des justifications LLM et contrôle anti-hallucination...")
    df_justified, control_metrics = generate_pricing_justifications(df_opt)

    # Métriques globales
    cat_counts = df_elasticity["category"].value_counts().to_dict()
    elastic_skus = df_elasticity[df_elasticity["category"] == "Élastique"]
    mean_elasticity_elastic = float(elastic_skus["elasticity"].mean()) if len(elastic_skus) > 0 else 0.0

    tot_curr_rev = float(df_justified["current_revenue"].sum())
    tot_curr_margin = float(df_justified["current_margin"].sum())
    tot_rec_rev = float(df_justified["rec_revenue"].sum())
    tot_rec_margin = float(df_justified["rec_margin"].sum())
    tot_margin_gain = float(df_justified["margin_gain_gbp"].sum())
    tot_margin_gain_pct = (tot_margin_gain / tot_curr_margin) if tot_curr_margin > 0 else 0.0

    skus_increased = int((df_justified["price_change_pct"] > 0.001).sum())
    skus_decreased = int((df_justified["price_change_pct"] < -0.001).sum())
    skus_unchanged = int((df_justified["price_change_pct"].abs() <= 0.001).sum())

    # Top opportunités de marge
    top_opportunities = df_justified.sort_values(by="margin_gain_gbp", ascending=False).head(15)[[
        "StockCode", "Description", "category", "elasticity", "r2", "p_value",
        "current_price", "rec_price", "price_change_pct",
        "current_margin", "rec_margin", "margin_gain_gbp", "opt_reason",
        "llm_justification", "control_status"
    ]].to_dict(orient="records")

    summary_metrics = {
        "project": "Projet 3 - Optimisation du Pricing & Élasticité-Prix",
        "generated_at": datetime.datetime.now().isoformat(),
        "global_metrics": {
            "total_skus_raw": len(sku_stats),
            "eligible_skus": int(sku_stats["is_eligible"].sum()),
            "modeled_skus": len(df_elasticity),
            "category_breakdown": cat_counts,
            "mean_elasticity_elastic": round(mean_elasticity_elastic, 4),
            "baseline_revenue_gbp": round(tot_curr_rev, 2),
            "baseline_margin_gbp": round(tot_curr_margin, 2),
            "optimized_revenue_gbp": round(tot_rec_rev, 2),
            "optimized_margin_gbp": round(tot_rec_margin, 2),
            "margin_gain_gbp": round(tot_margin_gain, 2),
            "margin_gain_pct": round(tot_margin_gain_pct, 4),
            "skus_price_increased": skus_increased,
            "skus_price_decreased": skus_decreased,
            "skus_price_unchanged": skus_unchanged
        },
        "diagnostic_summary": diagnostic,
        "sensitivity_analysis": sensitivity,
        "llm_control_metrics": control_metrics,
        "top_opportunities": top_opportunities,
        "skus_summary": df_justified[[
            "StockCode", "Description", "category", "elasticity", "r2", "p_value",
            "current_price", "rec_price", "price_change_pct",
            "current_revenue", "current_margin", "rec_margin", "margin_gain_gbp", "opt_reason",
            "llm_justification", "control_status"
        ]].to_dict(orient="records")
    }


    # 1. Export JSON
    pricing_dir = OUTPUTS / "pricing"
    pricing_dir.mkdir(parents=True, exist_ok=True)
    json_path = pricing_dir / "summary_metrics.json"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary_metrics, f, ensure_ascii=False, indent=2)

    print(f"✅ [PRICING EXPORT] Métriques JSON enregistrées dans : {json_path}")

    # 2. Export Modèle Financier Excel
    excel_path = pricing_dir / "pricing_optimization.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        # Onglet 1: Synthèse
        df_overview = pd.DataFrame([
            {"Indicateur": "Total SKUs analysés", "Valeur": len(sku_stats)},
            {"Indicateur": "SKUs éligibles modélisés", "Valeur": len(df_elasticity)},
            {"Indicateur": "Marge Baseline Total (£)", "Valeur": round(tot_curr_margin, 2)},
            {"Indicateur": "Marge Optimisée Total (£)", "Valeur": round(tot_rec_margin, 2)},
            {"Indicateur": "Gain de Marge Potentiel (£)", "Valeur": round(tot_margin_gain, 2)},
            {"Indicateur": "Gain de Marge (%)", "Valeur": f"{round(tot_margin_gain_pct * 100, 2)} %"},
            {"Indicateur": "SKUs en Hausse de Prix", "Valeur": skus_increased},
            {"Indicateur": "SKUs en Baisse de Prix", "Valeur": skus_decreased},
            {"Indicateur": "SKUs Inchangés", "Valeur": skus_unchanged}
        ])
        df_overview.to_excel(writer, sheet_name="Vue_Synthetique", index=False)

        # Onglet 2: Optimisation SKUs
        df_opt_export = df_opt[[
            "StockCode", "Description", "nb_weeks", "mean_price", "cv_price",
            "elasticity", "r2", "p_value", "category",
            "unit_cost", "current_price", "rec_price", "price_change_pct",
            "current_quantity", "rec_quantity",
            "current_revenue", "rec_revenue", "current_margin", "rec_margin",
            "margin_gain_gbp", "opt_reason"
        ]]
        df_opt_export.to_excel(writer, sheet_name="Optimisation_SKU", index=False)

        # Onglet 3: Sensibilité
        df_sens = pd.DataFrame(sensitivity).T
        df_sens.to_excel(writer, sheet_name="Analyse_Sensibilite", index=False)

    print(f"✅ [PRICING EXPORT] Modèle Excel enregistré dans : {excel_path}")

    return summary_metrics, json_path, excel_path


if __name__ == "__main__":
    export_pricing_summary()
