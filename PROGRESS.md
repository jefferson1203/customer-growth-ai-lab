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
  - **Commandes Non Livrées & Feature ML** : Prise en compte explicite de la tranche *"0. Non livrée"* (1 845 commandes, 91.38% détracteurs) et ajout de la feature `non_livre` (AUC du Gradient Boosting qui passe de 0.696 à **0.713**).
  - **Expérimentation LLM réelle (Prompt V1 vs Prompt V2)** : Création de `prompts/voc_classification_v2.txt` avec des consignes de désambiguïsation strictes et ré-exécution réelle des 100 avis via l'API Gemini 3.8 Flash (`voc/run_v2_eval.py`). Constat : La précision sur `LIV_RETARD` a **doublé (passant de 0.25 à 0.50)** et le rappel sur `PROD_NONCONFORME` a atteint **100 %**.
  - **Benchmark intégré dans l'Application** : Ajout du tableau comparatif mesuré V1 vs V2 dans l'onglet *Cadrage & Recommandations* de l'application Streamlit [`voc/app.py`](voc/app.py).
  - **Transparence du README** : Rectification des chiffres du README (Promoteurs 50.2 %, Passifs 14.6 %, Détracteurs 35.2 %) et publication du tableau complet des métriques par irritant.
  - **Design Corporate & Homogénéisation** : Retrait des émojis des titres d'onglets pour une restitution sobre.
- Ce que j'ai compris : Rigueur de l'évaluation méthodologique en conseil (redressement d'échantillons stratifiés, analyse empirique de l'arbitrage Précision vs Rappel en prompt engineering, protection de la propriété intellectuelle des jeux de données).
- Statut : **Projet 1 Validé avec Révision Méthodologique & Expérimentation Réelle !**

## [Projet 1 : Voix du Client IA] - Étape 10 : Refactoring LLMClient, migration du cache v1 et test à blanc Prompt V3
- Date : 2026-09-29
- Fait :
  - Restructuration de `common/llm.py` (cache unifié avec empreinte MD5 du prompt, `response_schema` strict, retry typé sur `ValidationError`, `JSONDecodeError` et `APIError` 429/5xx avec backoff exponentiel).
  - Création du schéma centralisé Pydantic `voc/schema.py` (`ReviewLabel`).
  - Archivage du prompt original v1 sous `prompts/archive/voc_classification_v1_original.txt` et confirmation du modèle `gemini-3.8-flash`.
  - Script de migration `voc/migrate_cache.py` exécuté avec validation Pydantic strict à la volée.
  - Test à blanc v3 réussi sur 5 avis réels (`voc/dry_run_v3.py`).
- Résultats obtenus :
  - `pytest tests/test_llm.py` : 4 tests au vert (100%).
  - Migration : **1 500 entrées valides migré(es)** (0 invalides).
  - Test à blanc Prompt V3 : 5 avis classés avec succès.

## [Projet 2 : Segmentation & Portefeuille] - Étape 1 : Chargement et cadrage Online Retail II
- Date : 2026-09-29
- Fait : Implémentation du loader optimisé Parquet (`common/data.py`) et calcul des métriques de cadrage (`portfolio/overview.py`).
- Ce que j'ai compris : Optimisation du temps de chargement (< 2s via Parquet) et importance de conserver les transactions sans CustomerID pour le calcul du CA global.
- Résultats obtenus (chiffres réels) : CA total £20.12M (85.7% UK), 5 852 clients uniques identifiés, 4 907 références produits, 1 037 098 lignes nettoyées sur 1 067 371 brutes.
- Prochaine étape : Étape 2 (Segmentation RFM & K-Means).

## [Projet 2 : Segmentation & Portefeuille] - Étape 2 : Segmentation clients RFM & K-Means
- Date : 2026-09-29
- Fait : Implémentation du modèle RFM par quintiles (`portfolio/rfm.py`), 6 règles métier de segmentation, analyse d'impact des grossistes (Top 1% CA), et comparaison avec K-Means sur log(R,F,M) standardisés (`portfolio/clustering.py`). Création des tests unitaires (`tests/test_rfm.py`).
- Ce que j'ai compris : Différence entre segmentation métier déterministe (RFM) et clustering non supervisé (K-Means), transformation log1p pour réduire l'asymétrie, et justification de la primauté des règles métiers pour l'adhésion client.
- Points où j'ai été aidé (niveau d'aide) : Niveau 2 (utilisation du Pipeline Scikit-Learn pour log1p + StandardScaler + K-Means).
- Résultats obtenus (chiffres réels) :
  - **Champions** : 25.2% des clients, **69.3% du CA des clients identifiés** (£12.08M, CA moyen par client sur la période 8 190.82 £).
  - **Fidèles** : 20.6% des clients, 14.1% du CA (£2.46M).
  - **À risque** : 14.1% des clients, 9.4% du CA (£1.64M de CA historique sur 2 ans, récence moy. 368 jours).
  - **En sommeil** : 25.8% des clients, 3.6% du CA (£633k, récence moy. 457 jours).
  - **Top 1% Grossistes** : 59 clients génèrent **32.06% du CA des clients identifiés** (£5.59M).
  - **K-Means** : Silhouette score = **0.3423** (pour k=5).
- Questions d'entretien travaillées : Pourquoi privilégier les règles RFM au clustering en conseil ; interprétation d'un score de Silhouette (bornes [-1, +1]) ; gestion de la corrélation R/F/M.
- Prochaine étape : Étape 3 (Personas LLM & Next Best Action).

## [Projet 2 : Segmentation & Portefeuille] - Étape 3 : Personas LLM & Next Best Actions
- Date : 2026-09-30
- Fait : Implémentation du prompt template `prompts/portfolio_persona.txt`, du schéma Pydantic `SegmentPersona`, de la génération structurée via `LLMClient` avec cache unifié (`portfolio/personas.py`), et de la table synthétique de Next Best Action (`build_next_best_action_table`).
- Ce que j'ai compris : Respect strict de la confidentialité RGPD (aucune donnée individuelle transmise au LLM, uniquement des agrégats), rôle d'expert retail senior dans le prompt, et construction de la table des Next Best Actions pour alimenter le copilote (Projet 4).
- Points où j'ai été aidé (niveau d'aide) : Niveau 2 (passations des variables `$var` dans le template string de `common/llm.py`).
- Résultats obtenus (chiffres réels) : 6 personas générés et mis en cache (`outputs/portfolio/personas_cache.json`).
  - **Champions** : *L'Élite Ambassadrice* (Programme VIP, Conciergerie)
  - **À risque** : *Le Grand Habitué Endormi* (Reconquête ciblée, Appel direct pour réactiver le segment à risque)
  - **Nouveaux** : *L'Explorateur à Fort Potentiel* (Parcours de bienvenue post-achat)
- Questions d'entretien travaillées : Complémentarité entre statistiques RFM et récit LLM ; protection des données clients (RGPD) avec l'IA.
- Prochaine étape : Étape 4 (Segmentation produits ABC & Longue traîne).

## [Projet 2 : Segmentation & Portefeuille] - Étape 4 : Segmentation produits ABC & Longue traîne
- Date : 2026-09-30
- Fait : Implémentation de l'analyse Pareto ABC (`compute_abc_analysis`), identification des 176 candidats à la déréférenciation (`identify_deletion_candidates` dans `portfolio/product_analysis.py`), et création de la suite de tests unitaires (`tests/test_product_analysis.py`).
- Ce que j'ai compris : Loi de Pareto appliquée au retail (80/15/5), arbitrage stratégique entre rationalisation de catalogue et préservation de la complétude du panier des clients VIP (Champions/Fidèles), et évaluation des coûts de complexité logistique.
- Points où j'ai été aidé (niveau d'aide) : Niveau 2 (jointure multi-périodes P1/P2 et harmonisation des types `CustomerID` float vs str).
- Résultats obtenus (chiffres réels) :
  - **Classe A (80% CA)** : 1 036 références (21.1% du catalogue, £16.10M).
  - **Classe B (15% CA)** : 1 281 références (26.1% du catalogue, £3.02M).
  - **Classe C (5% CA)** : 2 590 références (52.8% du catalogue, £1.01M).
  - **Candidats à la suppression** : 176 références C en baisse et avec moins de 20 % du volume d'achats réalisé par des clients Champions ou Fidèles (CA cumulé 2 ans à risque : £14.02k).
- Questions d'entretien travaillées : Pourquoi ne pas supprimer toute la Classe C ; impact logistique et coût de complexité de la longue traîne.
- Prochaine étape : Étape 5 (Business Cases Chiffrés A & B).

## [Projet 2 : Segmentation & Portefeuille] - Étape 5 : Business Cases Chiffrés A & B
- Date : 2026-09-30
- Fait : Implémentation des modèles financiers `compute_business_case_a`, `compute_business_case_b` et `compute_sensitivity_tables` dans `portfolio/business_case.py`. Création des tests unitaires validés dans `tests/test_business_case.py`.
- Ce que j'ai compris : Utilisation du panier transactionnel moyen (£362.01) plutôt que du CA cumulé 2 ans, rôle clé du groupe de contrôle AB testing pour mesurer la conversion additionnelle (incrementality), et sensibilité du Business Case B au coût logistique par SKU.
- Points où j'ai été aidé (niveau d'aide) : Niveau 1.
- Résultats obtenus (chiffres réels) :
  - **Business Case A (Reconquête Clients À risque)** : 745 clients ciblés (83 en groupe contrôle), Coût £1 490.00, Panier transactionnel moyen **£362.01**, Gain Net **£6 061.53** (à 8% de réengagement), ROI **406.8 %**, Seuil de Rentabilité (Break-even) **1.58 %**.
  - **Business Case B (Rationalisation Catalogue SKUs)** : 176 références C déréférencées, Économies logistiques £88 000/an (£500/SKU), Marge perdue £2 453.65 (avec 50% de transfert), Gain Net **£85 546.35**, Seuil logistique **£13.94 / SKU / an**.
- Questions d'entretien travaillées : Utilité du groupe de contrôle AB testing (incrémentalité vs achats spontanés) ; sensibilité du Business Case B au transfert d'achat.
- Prochaine étape : Étape 6 (Restitution & Application Interactive Streamlit).

## [Projet 2 : Segmentation & Portefeuille] - Étape 6 : Restitution & Application Interactive Streamlit
- Date : 2026-09-30
- Fait : Création de l'application interactive Streamlit [`portfolio/app.py`](portfolio/app.py) à 4 onglets (`Tab 0: Cadrage & Recommandations`, `Tab 1: Segmentation RFM & Cohortes`, `Tab 2: Clusters K-Means vs Règles`, `Tab 3: Portefeuille Produits & Business Cases`). Agrandissement du scatter plot 3D K-Means (hauteur 750px) et intégration du bouton de téléchargement du support PDF.
- Ce que j'ai compris : Présentation multi-onglets structurée pour faciliter la prise de décision par la Direction, mise en valeur de l'arbitrage entre segmentation déterministe RFM et clustering non-supervisé K-Means.
- Résultats obtenus : Dashboard complet et fonctionnel pour explorer les 5 852 clients et 4 907 références produits.

## [Projets 1 & 2] - Étape 7 : Exporter PDF Stratégique & Rendu Standardisé (1 slide par page A4 Paysage)
- Date : 2026-09-30
- Fait : Implémentation du moteur d'exportation PDF customisé `PresentationPDF` dans [`common/pdf_exporter.py`](common/pdf_exporter.py) :
  - Découpage étanche des slides via regex (`re.split(r'\n\s*---\s*\n', content)`) évitant toute confusion avec les séparateurs de tableaux Markdown (`|---|`).
  - Fusion propre du titre principal (# H1) sur la première slide sous forme de bandeau d'en-tête.
  - Calcul dynamique de la hauteur des cellules et des espacements pour garantir une stricte mise en page "1 slide = 1 page A4 Paysage" sans pages fantômes ni décalages.
  - Mise en forme corporate des tableaux (en-tête bleu nuit `#EFF6FF`, bordures `#CBD5E1`, fond alterné).
- Résultats obtenus :
  - `Projet1_Voix_du_Client_IA_Slides.pdf` : **Exactement 3 pages A4 Paysage**.
  - `Projet2_Segmentation_Portefeuille_Slides.pdf` : **Exactement 4 pages A4 Paysage**.
  - Intégration dans Streamlit avec redémarrage à chaud du serveur.
- Statut : **Projet 1 et Projet 2 intégralement finalisés et validés !**

## [Projet 2 : Segmentation & Portefeuille] - Étape 8 : Source Unique de Vérité, Panier Transactionnel AOV & Rigueur des Formulations
- Date : 2026-09-30
- Fait :
  - **Correction du Business Case A** : Calcul basé sur la valeur moyenne d'une commande `(df_at_risk["Monetary"] / df_at_risk["Frequency"]).mean()` (**£362.01** / commande), ramenant le ROI Net à **406.8 %** et le Seuil de rentabilité à **1.58 %**.
  - **Source Unique de Vérité (`portfolio/export_summary.py`)** : Script de génération unifiée produisant un fichier de métriques synthétiques léger (12 Ko vs 2.3 Mo) [`outputs/portfolio/summary_metrics.json`](outputs/portfolio/summary_metrics.json) et le modèle Excel interactif [`outputs/portfolio/business_case.xlsx`](outputs/portfolio/business_case.xlsx).
  - **Support Cloud Run & `.gitignore`** : Inclusion explicite de `!outputs/portfolio/summary_metrics.json` dans `.gitignore` et suppression des replis silencieux dans `portfolio/app.py` (chargement direct par clé sans valeurs par défaut en dur).
  - **Précision des Formulations & Limites** :
    - Remplacement de « panier moyen » par **« CA moyen par client sur la période »** pour le cumul RFM.
    - Précision de la formulation du critère C : *« moins de 20 % du volume d'achats réalisé par des clients Champions ou Fidèles »*.
    - Précision du périmètre du CA des grossistes : *« 32.06 % du CA des clients identifiés »*.
    - Précision du CA menacé : *« £1.64M de CA historique sur deux ans »*.
    - Ajout dans la section *Limites* du décalage temporel du Business Case B (CA à risque sur 2 ans vs économies logistiques annuelles).
- Résultats obtenus : 12/12 tests unitaires passés au vert (100%), déploiement Cloud Run 100% synchronisé avec le README et les slides PDF.

## [Projet 3 : Pricing & Élasticité] - Étape 1 : Préparation & Agrégation hebdomadaire par SKU
- Date : 2026-10-01
- Fait : Implémentation de `prepare_weekly_pricing_data()` dans `pricing/data_prep.py` (agrégation hebdomadaire ISO `%Y-W%V`, calcul du prix médian et du CA, calcul du CV du prix et filtrage des SKUs éligibles).
- Ce que j'ai compris : Importance du tri temporel ISO `%Y-W%V` sur 2 ans d'historique, rôle de la variabilité du prix ($CV \ge 5\%$) et de la taille d'échantillon ($\ge 40$ semaines) pour stabiliser la régression, et identification du biais d'endogénéité dû aux remises sur volume B2B.
- Points où j'ai été aidé (niveau d'aide) : Niveau 4 (Squelette et correction de la syntaxe pandas `.agg()`).
- Résultats obtenus (chiffres réels) : 4 905 SKUs analysés, **1 993 SKUs éligibles** (40.6% du catalogue), 50 SKUs éligibles retenus dans le top CA (4 811 observations hebdomadaires).
- Questions d'entretien travaillées : Nécessité de la variabilité du prix pour la régression ; biais d'endogénéité des remises sur volume.
- Prochaine étape : Étape 2 (Estimation de l'élasticité-prix par régression Log-Log).








