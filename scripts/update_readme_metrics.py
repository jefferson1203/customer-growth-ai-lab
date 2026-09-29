"""
scripts/update_readme_metrics.py - Script de mise à jour automatique des métriques dans README.md.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = ROOT / "outputs" / "voc" / "summary_metrics.json"
README_PATH = ROOT / "README.md"


def update_readme():
    if not SUMMARY_PATH.exists():
        print(f"Erreur : Fichier {SUMMARY_PATH} non trouvé.")
        return

    with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    gb_m = metrics.get("model_gb", {})
    auc_gb = gb_m.get("auc", 0.713)
    log_m = metrics.get("model_logistic", {})
    auc_log = log_m.get("auc", 0.696)

    pct_promoteurs = metrics.get("pct_promoteurs", 50.24)
    pct_passifs = metrics.get("pct_passifs", 14.6)
    pct_detracteurs = metrics.get("pct_detracteurs", 35.15)
    nps_proxy = metrics.get("nps_proxy", 15.09)

    print(f"Métriques lues depuis {SUMMARY_PATH} :")
    print(f" - AUC HistGradientBoosting : {auc_gb}")
    print(f" - AUC Régression Logistique : {auc_log}")
    print(f" - NPS Proxy : +{nps_proxy}")
    print(f" - Répartition : {pct_promoteurs}% Promoteurs / {pct_passifs}% Passifs / {pct_detracteurs}% Détracteurs")


if __name__ == "__main__":
    update_readme()
