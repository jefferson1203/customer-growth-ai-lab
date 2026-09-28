# Progression du Projet - Customer & Growth AI Lab

## [Projet 1 : Voix du Client IA] - Étape 1 : Chargement et préparation des données Olist
- Date : 2026-09-28
- Fait : Implémentation de `load_olist()` et `prepare_voc_data()` dans `common/data.py` (chargement des 5 CSV, conversions de dates, jointures `left`, calcul du `retard_jours`, dédoublonnage et filtrage des avis texte).
- Ce que j'ai compris : Gestion des relations 1:N entre commandes et articles (`drop_duplicates`), importance du typage des dates, et distinction entre la note de satisfaction transactionnelle (1-5 stars) et le vrai NPS (recommandation 0-10).
- Points où j'ai été aidé (niveau d'aide) : Niveau 2 (décompression des archives, structure séquentielle des jointures et gestion des `NaN`).
- Résultats obtenus (chiffres réels) : 40 641 avis avec verbatims texte conservés sur 99 224 avis initiaux.
- Questions d'entretien travaillées : Risque de duplication des avis sur commandes multi-articles ; différence entre satisfaction transactionnelle et NPS.
- Prochaine étape : Étape 2 - Échantillonnage stratifié des 1 500 avis (300 par note).
