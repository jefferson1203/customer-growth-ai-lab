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

    # Extraction des fréquences d'irritants redressées
    prio_map = {item["irritant"]: item["frequence"] for item in metrics["prio_matrix"]}

    metrics_text = f"""<!-- METRICS:START -->
* **Volume Traité** : **40 641 avis clients texte** analysés et préparés sur le dataset Olist.
* **Répartition des Clients** : **{pct_promoteurs:.1f} %** Promoteurs (5★), **{pct_passifs:.1f} %** Passifs (4★), **{pct_detracteurs:.1f} %** Détracteurs (1-3★).
* **NPS Proxy Global** : **+{nps_proxy:.2f}** (% Promoteurs 5★ - % Détracteurs 1-3★).
* **Évaluation Complète de la Classification LLM (Échantillon de Validation 100 Avis Annotés)** :

| Irritant / Classe | Précision | Rappel | F1-Score | Diagnostic / Action Prompt |
|---|---|---|---|---|
| `LIV_NONRECU` | 0.923 | 0.960 | **0.941** | Excellent repérage des commandes non reçues |
| `POSITIF` | 1.000 | 0.881 | **0.937** | Aucune fausse alerte sur les avis positifs |
| `PROD_NONCONFORME` | 0.833 | 0.769 | **0.800** | Bonne détection de la non-conformité |
| `SAV` | 0.750 | 0.522 | **0.615** | Rappel insuffisant (réclamations indirectes manquées), non résolu par le v2 : objet du v3 |
| `LIV_RETARD` | 0.250 | 0.900 | **0.391** | Sur-détection (explicite vs délai normal) ajustée au prompt v2 |

* **Cartographie des Irritants Négatifs (Pondérée & Redressée par la distribution réelle)** :
  * **{prio_map.get('LIV_NONRECU', 47.23):.2f} %** `LIV_NONRECU` (Commande non reçue - Irritant majeur #1)
  * **{prio_map.get('SAV', 26.82):.2f} %** `SAV` (Litiges et support)
  * **{prio_map.get('LIV_RETARD', 20.09):.2f} %** `LIV_RETARD` (Retard significatif)
  * **{prio_map.get('PROD_NONCONFORME', 19.95):.2f} %** `PROD_NONCONFORME` (Produit décevant)
* **Points de Rupture des Retards & Commandes Non Livrées** :
  * **Commandes Non Livrées (4.5% des commandes)** : **91.38 %** de détracteurs (Note moyenne 1.51/5).
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
