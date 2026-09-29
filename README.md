# Customer & Growth AI Lab

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![Google GenAI](https://img.shields.io/badge/Google--GenAI-Gemini--3.8--Flash-4285F4.svg)](https://ai.google.dev/)
[![Cloud Run Deployment](https://img.shields.io/badge/GCP-Cloud--Run-2496ED.svg)](https://customer-growth-voc-tgdklsc2vq-ew.a.run.app/)

> 🌐 **Application en ligne (Cloud Run)** : [https://customer-growth-voc-tgdklsc2vq-ew.a.run.app/](https://customer-growth-voc-tgdklsc2vq-ew.a.run.app/)

Laboratoire d'ingénierie et d'analyse de données axé sur l'expérience client (CX), l'IA générative et le Machine Learning appliqués au e-commerce (Dataset Olist & Online Retail II).

---

## 🗺️ Roadmap du Laboratoire (4 Projets)

| Projet | Périmètre & Technologies | Statut |
|---|---|---|
| **[Projet 1 : Voix du Client IA](./voc/)** | Classification LLM Gemini, NPS Proxy, Matrice Irritants, NPS Prédictif ML (Lift 2.56x) & Streamlit. | ✅ **Complété** |
| **[Projet 2 : Segmentation Portefeuille Client](./portfolio/)** | Segmentation RFM, Clustérisation (K-Means/DBSCAN), LTV & Prévention du Churn. | 🚀 **En cours / Prochainement** |
| **[Projet 3 : Pricing & Élasticité Prix](./pricing/)** | Modélisation de l'élasticité prix, optimisation de marge & recommandations de tarification. | 📅 **Prochainement** |
| **[Projet 4 : Copilote Agentique](./copilot/)** | Agent IA décisionnel autonome (AGY SDK / LangGraph) pour requêter les insights du lab. | 📅 **Prochainement** |

---

## 🚀 Projet 1 : Voix du Client Augmentée par l'IA (VoC & NPS Prédictif)

Ce module (`voc/`) transforme des milliers de verbatims clients non structurés en décisions stratégiques et boucles d'action proactives.

### 🌟 Résultats Réels et Métriques d'Impact

<!-- METRICS:START -->
* **Volume Traité** : **1 500 avis classés par LLM parmi 40 641 préparés** sur le dataset Olist.
* **Répartition des Clients (Avis texte)** : **50.2 %** Promoteurs (5★), **14.6 %** Passifs (4★), **35.1 %** Détracteurs (1-3★).
* **NPS Proxy Global** : **+15.09** (% Promoteurs 5★ - % Détracteurs 1-3★).
* **Évaluation Complète de la Classification LLM (V1 vs V2 sur Échantillon de Validation 100 Avis)** :

| Irritant / Classe | V1 (Précision / Rappel / F1) | V2 (Précision / Rappel / F1) |
|---|---|---|
| `LIV_NONRECU` | 0.923 / 0.960 / **0.941** | 0.923 / 0.960 / **0.941** |
| `LIV_RETARD` | 0.250 / 1.000 / **0.400** | 0.500 / 1.000 / **0.667** |
| `PROD_QUALITE` | 0.667 / 1.000 / **0.800** | 0.667 / 1.000 / **0.800** |
| `POSITIF` | 1.000 / 0.881 / **0.937** | 1.000 / 0.881 / **0.937** |
| `PROD_NONCONFORME` | 0.667 / 1.000 / **0.800** | 0.727 / 1.000 / **0.842** |
| `SAV` | 1.000 / 0.522 / **0.686** | 1.000 / 0.304 / **0.467** |
| `PROD_ENDOMMAGE` | 1.000 / 0.667 / **0.800** | 1.000 / 0.667 / **0.800** |
| `AUTRE` | 0.429 / 0.429 / **0.429** | 0.444 / 0.571 / **0.500** |
| `PRIX` | 0.750 / 1.000 / **0.857** | 0.750 / 1.000 / **0.857** |

* **Cartographie des Irritants Négatifs (Pondérée & Redressée par la distribution réelle)** :
  * **47.23 %** `LIV_NONRECU` (Commande non reçue - Irritant majeur #1)
  * **26.82 %** `SAV` (Litiges et support)
  * **20.09 %** `LIV_RETARD` (Retard significatif)
  * **19.95 %** `PROD_NONCONFORME` (Produit décevant)
* **Points de Rupture des Retards & Commandes Non Livrées** :
  * **Commandes Non Livrées (4,5 % des avis avec commentaire)** : **91.38 %** de détracteurs (Note moyenne 1.51/5).
  * **Retards de 4 à 10 jours** : **87.33 %** de détracteurs (Seuil de rupture nécessitant une alerte au 3ème jour).
* **NPS Prédictif (Machine Learning avec Feature `non_livre`)** :
  * Modèle retenu : **HistGradientBoostingClassifier**
  * **AUC-ROC** : **0.713** (vs 0.696 en Régression Logistique baseline)
  * **Taux de détracteurs dans le Top 10% le plus à risque** : **90.15 %**
  * **Lift (Gain d'efficacité)** : **2.56x** par rapport au hasard.
<!-- METRICS:END -->

### 📌 Limites & Prochaines Étapes (Maîtrise du Projet)

1. **Validation du Prompt V3 sur jeu de test indépendant** : Le prompt v3 est rédigé et pré-évalué sur 50 avis inédits, mais nécessite une campagne d'annotation annotée à grande échelle sur un test-set out-of-sample totalement étanche.
2. **Amélioration du Rappel SAV (Axe n°1)** : Le rappel du motif SAV reste le principal défi (0,522 en V1, tombé à 0,304 en V2 en raison de règles trop restrictives). L'enjeu du V3 est d'intercepter les réclamations indirectes (ex: demandes de suivi/remboursement sans mention du mot "support").
3. **Périmètre des Avis Texte** : Les métriques et taux de détracteurs portent spécifiquement sur les 40 641 avis avec commentaire texte, naturellement plus négatifs que la population globale des 99 224 commandes Olist.
4. **Validation Temporelle du Modèle ML (Backtesting Out-of-Time)** : Le découpage entraînement / test actuel est un split stratifié aléatoire. La prochaine étape consiste à valider le modèle par un découpage temporel (entraînement sur 2017, test out-of-time sur 2018).

---

## 🛠️ Architecture du Projet

```text
customer-growth-ai-lab/
├── common/                # Utilitaires partagés (chargement Olist, client LLM SDK)
│   ├── data.py            # Ingestion et nettoyage du dataset Olist
│   └── llm.py             # Client Gemini LLM avec Pydantic & cache JSONL
├── voc/                   # Module Voix du Client
│   ├── sample.py          # Échantillonnage stratifié (1 500 avis)
│   ├── classify.py        # Traitement par lots LLM
│   ├── validation.py      # Annotation manuelle (100 avis) & métriques F1/Précision/Rappel
│   ├── analysis.py        # NPS Proxy, Matrice Fréquence x Impact, Tranches de retard
│   ├── predictive.py      # Pipelines Scikit-Learn (LogisticRegression vs HistGradientBoosting)
│   └── app.py             # Application interactive Streamlit
├── slides/                # Restitution stratégique (3 slides d'action)
│   └── Projet1_Voix_du_Client_IA_Slides.md
├── tests/                 # Scripts d'inspection et de benchmark
│   ├── inspect_data.py    # Inspection EDA des features ML
│   └── run_predictive.py # Benchmark des modèles ML
├── config.py              # Configuration centralisée du projet
├── PROGRESS.md            # Suivi de progression et journal d'apprentissage
├── Dockerfile             # Containerization pour Google Cloud Run
└── requirements.txt       # Dépendances du projet
```

---

## ⚙️ Installation & Exécution Locale

### 1. Prérequis
- Python 3.12+
- Une clé API Gemini (`LLM_API_KEY`) dans un fichier `.env`

### 2. Installation de l'environnement

```bash
# Cloner le dépôt
git clone https://github.com/jefferson1203/customer-growth-ai-lab.git
cd customer-growth-ai-lab

# Créer et activer l'environnement virtuel
python3.12 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Fichier `.env`
Créer un fichier `.env` à la racine :
```env
LLM_API_KEY=votre_cle_api_gemini
LLM_MODEL=gemini-3.8-flash
```

### 4. Lancer le benchmark du modèle ML

```bash
PYTHONPATH=. .venv/bin/python tests/run_predictive.py
```

### 5. Lancer l'application Streamlit

```bash
PYTHONPATH=. .venv/bin/streamlit run voc/app.py
```

L'application s'ouvre localement sur `http://localhost:8501`.

---

## ☁️ Déploiement sur Google Cloud Run

L'application est containerisée et prête pour Cloud Run :

```bash
gcloud run deploy customer-growth-voc \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated
```

---

## 📄 Licence

Ce projet est sous licence MIT. Les données Olist proviennent du dataset public Kaggle [Brazilian E-Commerce Dataset par Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
