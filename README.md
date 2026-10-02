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
| **[Projet 3 : Pricing & Élasticité Prix](./pricing/)** | Modélisation log-log OLS de l'élasticité prix, optimisation sous garde-fous métiers, justifications LLM anti-hallucination par Regex & journalisation Human-in-the-Loop. | ✅ **Complété** |
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
  * **Champions (25.2 % des clients)** : Concentrent **69.3 % du CA des clients identifiés** (£12.08M, CA moyen par client sur la période £8 190.82).
  * **Fidèles (20.6 % des clients)** : Génèrent **14.1 % du CA** (£2.46M).
  * **À risque (14.1 % des clients)** : **£1.64M de CA historique sur deux ans** (récence moyenne de 368 jours).
  * **Top 1% Grossistes (59 clients)** : Génèrent **32.06 % du CA des clients identifiés** (£5.59M).
* **Clustérisation 3D K-Means** :
  * Standardisation `log1p(R, F, M)` + `StandardScaler` (Score de Silhouette = **0.342** pour k=5).
  * Scatter plot 3D interactif Plotly pour l'exploration visuelle des comportements.
* **Génération de Personas LLM (Strictement Conforme RGPD)** :
  * 6 personas générés via Gemini à partir d'agrégats statistiques anonymisés (ex: *L'Élite Ambassadrice*, *Le Grand Habitué Endormi*).
* **Rationalisation du Catalogue SKUs (Analyse Pareto ABC)** :
  * **Classe A (80 % du CA)** : 1 036 références (21.1 % du catalogue).
  * **Classe C (5 % du CA)** : 2 590 références (52.8 % du catalogue).
  * **Déréférenciation ciblée** : **176 références C** identifiées pour suppression (ventes en baisse + moins de 20 % du volume d'achats réalisé par des clients Champions ou Fidèles, £14.02k de CA cumulé sur deux ans).
* **Évaluation Financière des Business Cases & Seuils de Rentabilité** :
  * **Business Case A (Reconquête Clients À risque)** : Seuil de rentabilité dès **1.58 %** de taux de réponse incrémentale basé sur le panier transactionnel moyen de **£362.01** (Gain Net de **£6 061.53** à 8% de conversion, ROI : **406.8 %**).
  * **Business Case B (Rationalisation SKUs)** : Seuil de rentabilité dès **£13.94 / SKU / an** de coût de complexité logistique (vs £500 retenus dans le scénario central, dégageant **£85 546.35** net) et dès **0 %** de transfert d'achat.

### ⚠️ Limites & Périmètre d'Interprétation (Projet 2)

1. **Données transactionnelles historiques (Online Retail II)** : Ingestion limitée aux enregistrements 2009-2011; absence de données sociodémographiques ou de satisfaction directe des acheteurs.
2. **Hypothèses des Business Cases** : Les taux de réengagement (8 %) et de transfert d'achat (50 %) sont des hypothèses de travail illustratives, à valider par un test avec groupe témoin (A/B testing in vivo).
3. **Coûts logistiques fixes par SKU** : La valeur de £500 / SKU / an constitue une moyenne forfaitaire; l'exécution impose la validation des engagements contractuels fournisseurs (MOQ, remises sur volume) et des coûts de déstockage.
4. **Périmètres temporels des Business Cases** : Le CA à risque des SKUs candidates (£14 020.87) est un chiffre d'affaires cumulé sur deux ans, alors que les économies logistiques (£88 000/an) sont calculées sur une base annuelle.
5. **Présence de références de test / ajustements (TEST, GIFT, etc.)** : Le dataset conserve certaines références de test ou d'ajustement opérationnel (ex: TEST, GIFT) non filtrées par les règles initiales d'exclusion des StockCodes. Un nettoyage complémentaire du master données produits est nécessaire avant l'exécution de la déréférenciation.

---

## 🏷️ Projet 3 : Optimisation du Pricing & Élasticité Prix (Online Retail II)

Ce module (`pricing/`) modélise l'élasticité-prix de la demande par économétrie OLS log-log, calcule les prix optimaux sous garde-fous métier et intègre une couche de contrôle anti-hallucination par Regex avec journalisation *Human-in-the-Loop*.

### 🌟 Synthèse des Résultats & Modèle Économétrique

* **Diagnostic Tarifaire Catalogue** :
  * **1 993 SKUs éligibles** (présence ≥ 40 semaines de ventes et CV ≥ 5%).
  * **Prix Actuel de Référence** : Calculé sur la moyenne des 12 dernières semaines observées.
  * **Dispersion Tarifaire** : Ratio médian Pmax / Pmin = 2.6x. **75,5 %** des SKUs présentent un écart ≥ 2x.
  * **Remise Implicite Grossistes** : Seulement **5,13 %** de remise unitaire pour le Top 1% des grossistes malgré 10x plus de volumes.
* **Modélisation Économétrique Log-Log OLS avec Effets Fixes Mensuels** :
  * Équation : `ln(Q) = alpha + elasticity * ln(P) + effets_mois + e`
  * **SKUs Élastiques (élasticité < -1.0, p < 0.10)** : **37 SKUs (74 %)** (Élasticité moyenne: **-2.78**). Baisse de prix pour booster les volumes.
  * **SKUs Inélastiques (-1.0 <= élasticité < 0, p < 0.10)** : **2 SKUs (4 %)**. Hausse de prix pour capter de la marge.
  * **SKUs Exclus / Non Concluantes (p >= 0.10 ou élasticité >= 0)** : **11 SKUs (22 %)** exclues par sécurité (incertitude statistique p >= 0.10 ou effet Veblen/Giffen). Prix maintenu exact (0.00% de variation).
* **Optimisation sous Garde-fous Métiers (100 % Respectés)** :
  * Garde-fous : Variation maximale plafonnée à **±10.00% max après arrondi** (**0 SKU en dehors des bornes**, écart max 9.88%), markup minimum de **1.2x**, arrondis psychologiques sous contrainte stricte en `,49` ou `,99`.
  * **Gain de Marge Net Cumulé sur 2 Ans (Scénario Central 50% coût)** : **+£102 724,99 (+5,67 %)** (de £1,81M à £1,91M), soit **~£51 362,50 / an**.
  * **Analyse de Sensibilité (2 Ans)** : Gain de **+£160 125,86 (+7,36 %)** à 40% de coût et **+£52 277,71 (+3,61 %)** à 60% de coût.
* **Gouvernance IA & Validation Humaine** :
  * Génération de justifications Gemini structurées via `LLMClient.complete_json` (clé de cache dynamique `stock_code_varhash`).
  * **Contrôle Anti-Hallucination Regex Mesuré** : **20,0 % d'acceptation au 1er essai** (10/50 validés au 1er essai, 40 rejets par contrôle Regex anti-hallucination, 0 erreur API).
  * **Validation Humaine (Human-in-the-Loop)** : Journalisation des arbitrages Category Manager dans `outputs/pricing/decisions.csv` (stockage temporaire sur le disque éphémère du conteneur Cloud Run, à relier à une BDD persistante en production).

---

## 📄 Exportation des Supports de Présentation (PDF Paysage)

Chaque projet intègre un moteur d'exportation PDF customisé (`common/pdf_exporter.py`) basé sur `fpdf2` :
* **Mise en page certifiée** : **Stricte garantie "1 slide = 1 page A4 Paysage"** sans saut de page intempestif ni texte coupé.
* **Design Corporate** : Grilles de tableaux auto-calibrées, en-tête bleu nuit et pied de page dynamique.
* **Supports disponibles au téléchargement** :
  * `Projet1_Voix_du_Client_IA_Slides.pdf` (3 slides)
  * `Projet2_Segmentation_Portefeuille_Slides.pdf` (4 slides)
  * `Projet3_Pricing_Slides.pdf` (3 slides)

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
├── pricing/               # Module Projet 3 : Pricing & Élasticité Prix
│   ├── data_prep.py       # Filtrage SKUs éligibles (40w, CV >= 5%) & prix 12w
│   ├── pricing_analysis.py# Diagnostic dispersion tarifaire & remises grossistes
│   ├── elasticity.py      # Régression log-log OLS avec effets fixes mois (statsmodels)
│   ├── optimization.py    # Optimisation sous garde-fous stricts (+/-10%, markup, rounding)
│   ├── llm_justification.py# Justifications Gemini & contrôle Regex anti-hallucination
│   ├── export_summary.py  # Pipeline unifié & export JSON (38 Ko) / Excel (15 Ko)
│   └── app.py             # Application interactive Streamlit Projet 3
├── slides/                # Supports de restitution Markdown conseil
│   ├── Projet1_Voix_du_Client_IA_Slides.md
│   ├── Projet2_Segmentation_Portefeuille_Slides.md
│   └── Projet3_Pricing_Slides.md
├── tests/                 # Suite de tests unitaires pytest (18/18 passés)
│   ├── test_business_case.py
│   ├── test_llm.py
│   ├── test_pricing.py
│   ├── test_product_analysis.py
│   ├── test_retail_load.py
│   └── test_rfm.py
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

# Tests unitaires Scikit-Learn / Pytest (18 tests)
.venv/bin/pytest tests/
```

### 5. Lancer l'application Streamlit Hub Multi-Projets (Projets 1, 2 & 3)

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
