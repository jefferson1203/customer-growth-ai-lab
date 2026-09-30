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
| **[Projet 1 : Voix du Client IA](./voc/)** | Classification LLM Gemini, NPS Proxy, Matrice Irritants, NPS Prédictif ML (Lift 2.56x) & Exporter PDF. | ✅ **Complété** |
| **[Projet 2 : Segmentation & Portefeuille](./portfolio/)** | Segmentation RFM, Clustérisation 3D K-Means, Personas LLM (RGPD), Rationalisation SKUs Pareto & Business Cases A/B. | ✅ **Complété** |
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

---

## 📈 Projet 2 : Segmentation Clients & Rationalisation de Portefeuille (Online Retail II)

Ce module (`portfolio/`) analyse **5 852 clients uniques** et **4 907 références produits** (£20.12M de CA) pour optimiser la rétention et assainir la rentabilité du catalogue.

### 🌟 Synthèse des Résultats & Business Cases

* **Segmentation Métier RFM** :
  * **Champions (25.2 % des clients)** : Concentrent **69.3 % du CA** (£12.08M, panier moyen £8 190.82).
  * **Fidèles (20.6 % des clients)** : Generent **14.1 % du CA** (£2.46M).
  * **À risque (14.1 % des clients)** : **£1.64M de CA menacé** (récence moyenne de 368 jours).
  * **Top 1% Grossistes (59 clients)** : Génèrent **32.06 % du CA global** (£5.59M).
* **Clustérisation 3D K-Means** :
  * Standardisation `log1p(R, F, M)` + `StandardScaler` (Score de Silhouette = **0.342** pour k=5).
  * Scatter plot 3D interactif Plotly pour l'exploration visuelle des comportements.
* **Génération de Personas LLM (Strictement Conforme RGPD)** :
  * 6 personas générés via Gemini à partir d'agrégats statistiques anonymisés (ex: *L'Élite Ambassadrice*, *Le Grand Habitué Endormi*).
* **Rationalisation du Catalogue SKUs (Analyse Pareto ABC)** :
  * **Classe A (80 % du CA)** : 1 036 références (21.1 % du catalogue).
  * **Classe C (5 % du CA)** : 2 590 références (52.8 % du catalogue).
  * **Déréférenciation ciblée** : **1 737 références C** identifiées pour suppression (ventes en baisse + absentes des paniers Champions).
* **Évaluation Financière des Business Cases** :
  * **Business Case A (Reconquête Clients À risque)** : Gain Net annuel de **£39 779.84** (ROI : **2 669.8 %**, Seuil de rentabilité : **0.29 %** de taux de réponse).
  * **Business Case B (Rationalisation SKUs)** : Économies logistiques de **£868 500/an** (£500/SKU) pour un Gain Net de **£756 669.64** (avec 50 % de transfert d'achat sur les références A/B).

---

## 📄 Exportation des Supports de Présentation (PDF Paysage)

Chaque projet intègre un moteur d'exportation PDF customisé (`common/pdf_exporter.py`) basé sur `fpdf2` :
* **Mise en page certifiée** : **Stricte garantie "1 slide = 1 page A4 Paysage"** sans saut de page intempestif ni texte coupé.
* **Design Corporate** : Grilles de tableaux auto-calibrées, en-tête bleu nuit et pied de page dynamique.
* **Supports disponibles au téléchargement** :
  * `Projet1_Voix_du_Client_IA_Slides.pdf` (3 slides)
  * `Projet2_Segmentation_Portefeuille_Slides.pdf` (4 slides)

---

## 🛠️ Architecture du Projet

```text
customer-growth-ai-lab/
├── common/                # Utilitaires partagés (loaders, client LLM, exportateur PDF)
│   ├── data.py            # Ingestion datasets Olist et Online Retail II (Parquet)
│   ├── llm.py             # Client Gemini LLM avec Pydantic & cache JSONL unifié
│   └── pdf_exporter.py    # Exporter PDF Landscape A4 (1 slide / page)
├── voc/                   # Module Projet 1 : Voix du Client IA
│   ├── sample.py          # Échantillonnage stratifié (1 500 avis)
│   ├── classify.py        # Classification LLM structurée
│   ├── validation.py      # Benchmark et métriques de validation Prompt V1 vs V2
│   ├── analysis.py        # NPS Proxy & Matrice des irritants
│   ├── predictive.py      # NPS Prédictif (Logistic vs HistGradientBoosting)
│   └── app.py             # Application interactive Streamlit Projet 1
├── portfolio/             # Module Projet 2 : Segmentation & Portefeuille
│   ├── overview.py        # Cadrage et métriques globales Online Retail II
│   ├── rfm.py             # Segmentation déterministe RFM & Analyse Grossistes
│   ├── clustering.py      # Clustering non-supervisé 3D K-Means
│   ├── personas.py        # Génération de Personas LLM (RGPD) & Next Best Actions
│   ├── product_analysis.py# Analyse Pareto ABC & Candidats à la déréférenciation
│   ├── business_case.py   # Modélisation financière des Business Cases A & B
│   └── app.py             # Application interactive Streamlit Projet 2
├── slides/                # Supports de restitution Markdown conseil
│   ├── Projet1_Voix_du_Client_IA_Slides.md
│   └── Projet2_Segmentation_Portefeuille_Slides.md
├── main.py                # Hub d'entrée Streamlit multi-pages (`st.navigation`)
├── config.py              # Configuration centralisée des chemins et constantes
├── PROGRESS.md            # Suivi de progression et journal d'apprentissage
├── Dockerfile             # Containerization pour Google Cloud Run
└── requirements.txt       # Dépendances du projet (fpdf2, streamlit, scikit-learn, etc.)
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

### 4. Lancer les benchmarks & tests unitaires

```bash
# Test du NPS prédictif (Projet 1)
PYTHONPATH=. .venv/bin/python tests/run_predictive.py

# Tests unitaires Scikit-Learn / Pytest
.venv/bin/pytest tests/
```

### 5. Lancer l'application Streamlit Hub (Projet 1 & Projet 2)

```bash
PYTHONPATH=. .venv/bin/streamlit run main.py
```

L'application s'ouvre localement sur `http://localhost:8501` avec la navigation multi-pages.

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

Ce projet est sous licence MIT. Les jeux de données proviennent de Kaggle : [Brazilian E-Commerce par Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) et [Online Retail II](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci).
