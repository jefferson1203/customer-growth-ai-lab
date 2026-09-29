# Progression du Projet - Customer & Growth AI Lab

## [Projet 1 : Voix du Client IA] - Étape 1 : Chargement et préparation des données Olist
- Date : 2026-09-28
- Fait : Implémentation de `load_olist()` et `prepare_voc_data()` dans `common/data.py` (chargement des 5 CSV, conversions de dates, jointures `left`, calcul du `retard_jours`, dédoublonnage et filtrage des avis texte).
- Ce que j'ai compris : Gestion des relations 1:N entre commandes et articles (`drop_duplicates`), typage des dates, et distinction entre satisfaction transactionnelle et NPS.
- Points où j'ai été aidé (niveau d'aide) : Niveau 2.
- Résultats obtenus (chiffres réels) : 40 641 avis avec verbatims texte conservés sur 99 224 avis initiaux.
- Questions d'entretien travaillées : Risque de duplication des avis sur commandes multi-articles ; différence entre satisfaction transactionnelle et NPS.

## [Projet 1 : Voix du Client IA] - Étape 2 : Échantillonnage stratifié
- Date : 2026-09-28
- Fait : Implémentation de `get_stratified_sample()` dans `voc/sample.py`.
- Ce que j'ai compris : Utilité de l'échantillonnage stratifié pour maîtriser les coûts de traitement LLM (FinOps AI) et importance du `random_state` pour la reproductibilité.
- Points où j'ai été aidé (niveau d'aide) : Niveau 1.
- Résultats obtenus (chiffres réels) : Échantillon exact de 1 500 avis (300 avis par note de 1 à 5).
- Questions d'entretien travaillées : Redressement des proportions par la pondération réelle des notes.

## [Projet 1 : Voix du Client IA] - Étape 3 : Classification par LLM
- Date : 2026-09-28
- Fait : Implémentation du client `LLMClient` dans `common/llm.py` (avec le SDK `google-genai`, cache disque JSONL, schéma Pydantic `ReviewLabel`) et du processeur de lot `classify_batch()` dans `voc/classify.py`.
- Ce que j'ai compris : Intérêt des sorties structurées (Pydantic), du typage strict (`Literal`) et du cache disque pour éviter la facturation redondante.
- Points où j'ai été aidé (niveau d'aide) : Niveau 2 (migration SDK Gemini et gestion du cache).
- Résultats obtenus (chiffres réels) : Test validé sur 5 avis réels avec génération de résumés FR et classification d'irritants/sentiment/urgence.
- Questions d'entretien travaillées : Pourquoi imposer une sortie JSON Pydantic plutôt qu'un texte libre (robustesse, parsing automatique sans échec).
## [Projet 1 : Voix du Client IA] - Étape 4 : Validation manuelle et évaluation
- Date : 2026-09-28
- Fait : Implémentation de `generate_validation_sample()` et `evaluate_classification()` dans `voc/validation.py`. Annotation manuelle d'un échantillon de 100 avis et calcul des métriques TP, FP, FN, Précision, Rappel et F1-score par irritant.
- Ce que j'ai compris : Différence entre précision (évitement des fausses alertes) et rappel (exhaustivité), impact métier des Faux Positifs sur la crédibilité de l'outil et technique de prompt engineering pour clarifier la frontière de `LIV_RETARD`.
- Points où j'ai été aidé (niveau d'aide) : Niveau 2.
- Résultats obtenus (chiffres réels) : 100 avis annotés. F1 = 0.941 sur `LIV_NONRECU`, F1 = 0.937 sur `POSITIF`, Précision = 0.25 sur `LIV_RETARD` (sur-détection), Rappel = 0.522 sur `SAV`.
- Questions d'entretien travaillées : Interprétation d'une faible précision / haut rappel en prod ; ajustement du prompt pour supprimer le biais sur les délais de livraison.
## [Projet 1 : Voix du Client IA] - Étape 5 : Analyse et priorisation des irritants
- Date : 2026-09-29
- Fait : Implémentation de `calculate_nps_proxy()`, `compute_prioritization_matrix()` et `analyze_delay_impact()` dans `voc/analysis.py`.
- Ce que j'ai compris : Calcul du NPS proxy sur échelle 1-5 vs vrai NPS relationnel (échelle 0-10), identification des irritants majeurs (`LIV_NONRECU` à 39.67% et `SAV` à 21.78%), et mise en évidence du seuil critique des 4 jours de retard de livraison (87.33% de détracteurs).
- Points où j'ai été aidé (niveau d'aide) : Niveau 3 (vectorisation pandas et découpage `pd.cut`).
- Résultats obtenus (chiffres réels) : NPS proxy global de **15.09**. Taux de détracteurs bondissant de 27.14% (à l'heure) à 87.33% (retard 4-10j). Top 3 irritants : `LIV_NONRECU` (39.67%), `SAV` (21.78%), `PROD_NONCONFORME` (19.33%).
- Questions d'entretien travaillées : Différence entre satisfaction transactionnelle (avis commande) et NPS relationnel (recommandation marque) ; préconisation opérationnelle sur le seuil critique des 4 jours.
## [Projet 1 : Voix du Client IA] - Étape 6 : NPS prédictif (Machine Learning)
- Date : 2026-09-29
- Fait : Implémentation de `prepare_ml_dataset()` et `train_eval_nps_model()` dans `voc/predictive.py` (Pipeline Scikit-Learn avec ColumnTransformer, StandardScaler, OneHotEncoder et LogisticRegression).
- Ce que j'ai compris : Importance capitale d'éviter la fuite de données (Data Leakage temporel) en n'utilisant que les informations connues à la livraison, rôle des pipelines Scikit-Learn pour l'encodage propre, et pertinence métier de la métrique de Lift (Top 10% le plus à risque) par rapport à l'AUC-ROC.
- Points où j'ai été aidé (niveau d'aide) : Niveau 3 (construction du Pipeline Scikit-Learn et calcul du Lift).
- Résultats obtenus (chiffres réels) : Logistic Regression (AUC = **0.676**, Lift = **2.33x**) vs **HistGradientBoosting** (AUC = **0.711**, Taux détracteurs Top 10% = **90.02 %**, Lift = **2.56x**).
- Questions d'entretien travaillées : Pourquoi le Lift est plus convaincant qu'un score AUC auprès d'un Directeur Client ; comparaison Régression Logistique vs Gradient Boosting ; prévention du Data Leakage.
## [Projet 1 : Voix du Client IA] - Étape 7 : Restitution & Tableau de bord
- Date : 2026-09-29
- Fait : Création de l'application interactive Streamlit [`voc/app.py`](voc/app.py) (4 onglets : KPIs, Matrice des irritants, Impact des retards, NPS prédictif & courbe ROC comparative) et rédaction des 3 slides de synthèse stratégique ([`slides/Projet1_Voix_du_Client_IA_Slides.md`](slides/Projet1_Voix_du_Client_IA_Slides.md)).
- Ce que j'ai compris : Restitution efficace du signal Data à la décision business, structuration de slides conseil orientées conclusions, et articulation d'une boucle d'action proactive.
- Points où j'ai été aidé (niveau d'aide) : Niveau 2 (structure Streamlit et layout des slides).
- Résultats obtenus (chiffres réels) : Dashboard fonctionnel, 3 slides de recommandations chiffrées basées sur les données Olist.

## [Projet 1 : Voix du Client IA] - Étape 8 : Déploiement Cloud Run & CI/CD initial
- Date : 2026-09-29
- Fait : 
  - Déploiement conteneurisé Docker sur Google Cloud Run (`customer-growth-voc`).
  - Automatisation du pipeline CI/CD GitHub Actions ([`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)) déclenché sur la branche `master`.
  - Implémentation du hub d'entrée multi-pages [`main.py`](main.py) via `st.navigation`.
- Ce que j'ai compris : Gestion des contraintes de déploiement serveur (`STREAMLIT_SERVER_HEADLESS`, casse des noms de fichiers Linux).
- Statut : **Déploiement opérationnel, corrections suite à revue en cours.**

## [Projet 1 : Voix du Client IA] - Étape 9 : Corrections suite à la revue senior & Rigueur méthodologique
- Date : 2026-09-29
- Fait :
  - **Retrait des données brutes & Sécurité** : Retrait des fichiers CSV/JSONL bruts du dépôt (`git rm --cached`), remplacement par un fichier JSON d'agrégats analytiques anonymisés (`outputs/voc/summary_metrics.json`).
  - **Redressement de la Matrice des Irritants** : Application des poids de redressement selon la distribution réelle Olist (60.5% 1★, 14.8% 2★, 24.7% 3★). Le motif `LIV_NONRECU` passe de 39.7% (brut) à **47.23% (redressé)**.
  - **Commandes Non Livrées & Feature ML** : Prise en compte explicite de la tranche *"0. Non livrée"* (1 845 commandes, 91.38% détracteurs) et ajout de la feature `non_livre` (AUC du Gradient Boosting qui passe de 0.711 à **0.751**).
  - **Expérimentation LLM réelle (Prompt V1 vs Prompt V2)** : Création de `prompts/voc_classification_v2.txt` avec des consignes de désambiguïsation strictes et ré-exécution réelle des 100 avis via l'API Gemini 3.8 Flash (`voc/run_v2_eval.py`). Constat : La précision sur `LIV_RETARD` a **doublé (passant de 0.25 à 0.50)** et le rappel sur `PROD_NONCONFORME` a atteint **100 %**.
  - **Benchmark intégré dans l'Application** : Ajout du tableau comparatif mesuré V1 vs V2 dans l'onglet *Cadrage & Recommandations* de l'application Streamlit [`voc/app.py`](voc/app.py).
  - **Transparence du README** : Rectification des chiffres du README (Promoteurs 50.2 %, Passifs 14.6 %, Détracteurs 35.2 %) et publication du tableau complet des métriques par irritant.
  - **Design Corporate & Homogénéisation** : Retrait des émojis des titres d'onglets pour une restitution sobre.
- Ce que j'ai compris : Rigueur de l'évaluation méthodologique en conseil (redressement d'échantillons stratifiés, analyse empirique de l'arbitrage Précision vs Rappel en prompt engineering, protection de la propriété intellectuelle des jeux de données).
- Statut : **Projet 1 Validé avec Révision Méthodologique & Expérimentation Réelle !**




