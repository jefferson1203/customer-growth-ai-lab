# Customer & Growth AI Lab

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![Google GenAI](https://img.shields.io/badge/Google--GenAI-Gemini--3.8--Flash-4285F4.svg)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Cloud--Run-2496ED.svg)](https://cloud.google.com/run)

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

* **Volume Traité** : **40 641 avis clients texte** analysés et préparés sur le dataset Olist.
* **NPS Proxy Global** : **+15.09** (*64.8 %* Promoteurs 5★ | *35.2 %* Détracteurs 1-3★).
* **Évaluation de la Classification LLM (Gemini 3.8 Flash via Pydantic JSON)** :
  * `LIV_NONRECU` : **F1-score 0.941** (Précision 0.923 | Rappel 0.960)
  * `POSITIF` : **F1-score 0.937** (Précision 1.000 | Rappel 0.881)
* **Cartographie des Irritants Négatifs** :
  * **39.67 %** `LIV_NONRECU` (Commande non reçue)
  * **21.78 %** `SAV` (Litiges et support)
  * **19.33 %** `PROD_NONCONFORME` (Produit décevant)
* **Seuil Critique de Retard** : À partir de **4 jours de retard**, le taux de détracteurs passe à **87.33 %** (contre 27.14 % à l'heure).
* **NPS Prédictif (Machine Learning)** :
  * Modèle retenu : **HistGradientBoostingClassifier**
  * **AUC-ROC** : **0.711** (vs 0.676 en Régression Logistique baseline)
  * **Taux de détracteurs dans le Top 10% le plus à risque** : **90.02 %**
  * **Lift (Gain d'efficacité)** : **2.56x** par rapport au hasard.

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
git clone https://github.com/votre-user/customer-growth-ai-lab.git
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
