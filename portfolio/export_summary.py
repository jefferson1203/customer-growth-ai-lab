import json
from pathlib import Path
import pandas as pd

from config import DATA_RAW, OUTPUTS
from common.data import load_retail
from portfolio.rfm import compute_rfm, compute_rfm_summary, analyse_wholesalers
from portfolio.clustering import train_kmeans, compare_rfm_vs_kmeans
from portfolio.personas import generate_all_personas
from portfolio.product_analysis import compute_abc_analysis, identify_deletion_candidates
from portfolio.business_case import compute_business_case_a, compute_business_case_b, compute_sensitivity_tables, generate_business_case_excel


def export_portfolio_summary():
    print("Chargement et traitement des données Online Retail II...")
    df_clean, audit_df = load_retail(DATA_RAW)

    print("Calcul de la segmentation RFM...")
    df_rfm = compute_rfm(df_clean)
    rfm_summary = compute_rfm_summary(df_rfm)
    wholesalers_stats = analyse_wholesalers(df_rfm)

    print("Clustérisation K-Means...")
    df_kmeans, silhouette_score_val = train_kmeans(df_rfm, n_clusters=5)
    rfm_vs_kmeans = compare_rfm_vs_kmeans(df_kmeans)

    print("Analyse Pareto ABC et déréférenciation SKUs...")
    df_abc, abc_summary = compute_abc_analysis(df_clean)
    df_candidates = identify_deletion_candidates(df_clean, df_rfm, df_abc)

    print("Génération du modèle financier Excel...")
    excel_path = generate_business_case_excel(df_rfm, df_candidates)

    print("Génération des personas LLM...")
    cache_path = OUTPUTS / "portfolio" / "personas_cache.json"
    personas_cache = generate_all_personas(rfm_summary, cache_path)
    personas_json = {k: v.model_dump() for k, v in personas_cache.items()}

    print("Calcul des Business Cases & Tables de sensibilité...")
    bc_a = compute_business_case_a(df_rfm)
    bc_b = compute_business_case_b(df_candidates)
    sens_a, sens_b = compute_sensitivity_tables(df_rfm, df_candidates)

    # Préparation du top 20 des candidates SKUs pour affichage léger
    top20_cols = ["StockCode", "Description", "ca_total", "quantity_total"]
    available_cols = [c for c in top20_cols if c in df_candidates.columns]
    candidates_top20 = df_candidates.sort_values("ca_total", ascending=False).head(20)[available_cols].to_dict(orient="records")

    summary_data = {
        "overview_metrics": {
            "nb_transactions": int(len(df_clean)),
            "nb_clients": int(len(df_rfm)),
            "total_ca": float(round(df_clean["Revenue"].sum(), 2)),
            "total_skus": int(df_clean["StockCode"].nunique()),
        },
        "rfm_summary": rfm_summary.to_dict(orient="records"),
        "stats_wholesalers": wholesalers_stats,
        "silhouette_score": float(silhouette_score_val),
        "rfm_vs_kmeans": rfm_vs_kmeans.to_dict(orient="records"),
        "abc_summary": abc_summary,
        "candidates_summary": {
            "nb_candidates": int(len(df_candidates)),
            "ca_at_risk": float(round(df_candidates["ca_total"].sum(), 2)),
        },
        "candidates_top20": candidates_top20,
        "bc_a": bc_a,
        "bc_b": bc_b,
        "sens_a": sens_a.to_dict(),
        "sens_b": sens_b.to_dict(),
        "personas_cache": personas_json,
        "excel_path": str(excel_path),
    }

    out_json = OUTPUTS / "portfolio" / "summary_metrics.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Résumé léger exporté avec succès dans {out_json}")
    print(f"  - Business Case A Net Margin: £{bc_a['net_margin']:,.2f} (Break-even: {bc_a['break_event_rate']*100:.2f}%, ROI: {bc_a['roi_pct']:.1f}%)")
    print(f"  - Business Case B Net Margin: £{bc_b['net_gain']:,.2f} (Break-even SKU Cost: £{bc_b['break_even_sku_cost']:.2f}/SKU/an)")
    return summary_data


if __name__ == "__main__":
    export_portfolio_summary()
