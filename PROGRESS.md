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
- Points où j'ai été aidé (niveau d'aide) : Niveau 1 (conseil syntaxique `groupby().sample()`).
- Résultats obtenus (chiffres réels) : Échantillon exact de 1 500 avis (300 avis par note de 1 à 5).
- Questions d'entretien travaillées : Redressement des proportions par la pondération réelle des notes.
- Prochaine étape : Étape 3 - Classification par LLM (implémentation de `common/llm.py` et `voc/classify.py`).
