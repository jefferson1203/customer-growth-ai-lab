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
- Prochaine étape : Étape 5 - Analyse et priorisation des irritants (Matrice Fréquence x Impact, proxy NPS).

