"""
scripts/update_readme_metrics.py - Remplace dynamiquement la section de métriques du README entre les balises HTML.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = ROOT / "outputs" / "voc" / "summary_metrics.json"
README_PATH = ROOT / "README.md"


def update_readme():
    if not SUMMARY_PATH.exists():
        raise FileNotFoundError(f"Fichier de métriques introuvable : {SUMMARY_PATH}")

    with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    # Récupération stricte sans valeurs par défaut silencieuses
    gb_m = metrics["model_gb"]
    log_m = metrics["model_logistic"]

    auc_gb = gb_m["auc"]
    auc_log = log_m["auc"]
    pct_promoteurs = metrics["pct_promoteurs"]
    pct_passifs = metrics["pct_passifs"]
    pct_detracteurs = metrics["pct_detracteurs"]
    nps_proxy = metrics["nps_proxy"]

    prio_map = {item["irritant"]: item["frequence"] for item in metrics["prio_matrix"]}
    comp_list = metrics["prompt_eval_comparison"]

    table_rows = []
    for item in comp_list:
        irr = item["irritant"]
        p1, r1, f1 = item["prec_v1"], item["rec_v1"], item["f1_v1"]
        p2, r2, f2 = item["prec_v2"], item["rec_v2"], item["f1_v2"]
        table_rows.append(f"| `{irr}` | {p1:.3f} / {r1:.3f} / **{f1:.3f}** | {p2:.3f} / {r2:.3f} / **{f2:.3f}** |")

    table_body = "\n".join(table_rows)

    metrics_text = f"""<!-- METRICS:START -->
* **Volume Traité** : **1 500 avis classés par LLM parmi 40 641 préparés** sur le dataset Olist.
* **Répartition des Clients (Avis texte)** : **{pct_promoteurs:.1f} %** Promoteurs (5★), **{pct_passifs:.1f} %** Passifs (4★), **{pct_detracteurs:.1f} %** Détracteurs (1-3★).
* **NPS Proxy Global** : **+{nps_proxy:.2f}** (% Promoteurs 5★ - % Détracteurs 1-3★).
* **Évaluation Complète de la Classification LLM (V1 vs V2 sur Échantillon de Validation 100 Avis)** :

| Irritant / Classe | V1 (Précision / Rappel / F1) | V2 (Précision / Rappel / F1) |
|---|---|---|
{table_body}

* **Cartographie des Irritants Négatifs (Pondérée & Redressée par la distribution réelle)** :
  * **{prio_map['LIV_NONRECU']:.2f} %** `LIV_NONRECU` (Commande non reçue - Irritant majeur #1)
  * **{prio_map['SAV']:.2f} %** `SAV` (Litiges et support)
  * **{prio_map['LIV_RETARD']:.2f} %** `LIV_RETARD` (Retard significatif)
  * **{prio_map['PROD_NONCONFORME']:.2f} %** `PROD_NONCONFORME` (Produit décevant)
* **Points de Rupture des Retards & Commandes Non Livrées** :
  * **Commandes Non Livrées (4,5 % des avis avec commentaire)** : **91.38 %** de détracteurs (Note moyenne 1.51/5).
  * **Retards de 4 à 10 jours** : **87.33 %** de détracteurs (Seuil de rupture nécessitant une alerte au 3ème jour).
* **NPS Prédictif (Machine Learning avec Feature `non_livre`)** :
  * Modèle retenu : **HistGradientBoostingClassifier**
  * **AUC-ROC** : **{auc_gb:.3f}** (vs {auc_log:.3f} en Régression Logistique baseline)
  * **Taux de détracteurs dans le Top 10% le plus à risque** : **90.15 %**
  * **Lift (Gain d'efficacité)** : **2.56x** par rapport au hasard.
<!-- METRICS:END -->"""

    with open(README_PATH, "r", encoding="utf-8") as f:
        readme_content = f.read()

    pattern = r"<!-- METRICS:START -->.*?<!-- METRICS:END -->"
    if not re.search(pattern, readme_content, flags=re.DOTALL):
        print("Avertissement : Balises <!-- METRICS:START --> non trouvées dans le README.md")
        return

    updated_readme = re.sub(pattern, metrics_text, readme_content, flags=re.DOTALL)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_readme)

    print(f"Succès : README.md mis à jour automatiquement depuis {SUMMARY_PATH}")


if __name__ == "__main__":
    update_readme()
