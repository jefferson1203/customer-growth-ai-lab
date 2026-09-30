# Restitution Stratégique - Voix du Client IA (Olist E-Commerce)

---

## Slide 1 : Le Constat
### Les problèmes d'expédition et de livraison génèrent 61,4 % de la totalité des détracteurs d'Olist.

> **Synthèse Exécutive** : L'analyse sémantique automatisée par LLM sur 40 641 avis montre un **NPS Proxy de +15.09**. La satisfaction globale est lourdement pénalisée par deux irritants majeurs concentrés sur la chaîne logistique et le SAV.

### Chiffres Clés & Matrice des Irritants
- **NPS Proxy Global** : **+15.09** (*64.8 %* Promoteurs 5 étoiles | *35.2 %* Détracteurs 1-3 étoiles).
- **Top 3 des Irritants Négatifs** (Classifiés par LLM Gemini) :
  1. **`LIV_NONRECU`** (Commande non reçue ou incomplète) : **39.67 %** des avis négatifs (Note moyenne : 1.81 / 5).
  2. **`SAV`** (Service client injoignable / litiges) : **21.78 %** des avis négatifs (Note moyenne : 1.68 / 5).
  3. **`PROD_NONCONFORME`** (Produit différent du catalogue) : **19.33 %** des avis négatifs (Note moyenne : 2.19 / 5).
- **Conclusion** : Le non-respect des promesses de livraison constitue le premier levier de destruction de valeur client.

---

## Slide 2 : Les Causes
### À partir de 4 jours de retard de livraison, le taux de détracteurs s'effondre à 87,3 %.

> **Seuil Critique Opérationnel** : L'insatisfaction n'est pas linéaire. Jusqu'à 3 jours de retard, la tolérance client existe encore. Dès le 4ème jour, le basculement en détracteur devient quasi-systématique.

### Dégradation de la Note selon le Retard
- **À l'heure ou en avance** (N = 35 049) : Note moyenne **3.98 / 5** | **27.14 %** de détracteurs.
- **Retard de 1 à 3 jours** (N = 889) : Note moyenne **2.79 / 5** | **60.18 %** de détracteurs (*+33 points*).
- **Retard de 4 à 10 jours** (N = 1 515) : Note moyenne **1.72 / 5** | **87.33 %** de détracteurs (*+60 points*).
- **Retard > 10 jours** (N = 1 343) : Note moyenne **1.56 / 5** | **91.44 %** de détracteurs.

### Verbatims Clients Représentatifs (Traduits & Résumés)
> *"Colis toujours pas reçu après 2 semaines, aucune réponse du service client."* - (Note : 1 star | Code : `LIV_NONRECU`, `SAV`)
> *"Produit livré avec 6 jours de retard sans aucun message d'information."* - (Note : 1 star | Code : `LIV_RETARD`)

---

## Slide 3 : Les Actions
### Trois chantiers prioritaires pour capter 90 % des détracteurs avant dépôt de l'avis et redresser le NPS de +10 points.

> **Feuille de Route à 6 mois** : Basculer d'une gestion réactive des réclamations à une **boucle d'action proactive** pilotée par Machine Learning dès la livraison.

| Chantier Prioritaire | Action Concrète | Niveau d'Effort | Impact Attendu | KPI de Suivi |
|---|---|---|---|---|
| **1. Boucle d'Action Proactive (NPS Prédictif)** | Déclencher automatiquement une alerte et un coupon d'excuse préventif pour le Top 10% des commandes à haut risque détectées par le modèle (HistGradientBoosting). | **Moyen** (API & CRM) | **Très Fort** (Capte **90.02 %** de vrais détracteurs — Lift **2.56x** par rapport au hasard). | Taux de rétention des commandes ciblées (Cible : > 75%). |
| **2. Gestion de la Rupture des 4 Jours** | Envoyer une notification SMS/WhatsApp automatique au 3ème jour de retard avec réestimation transparente de la date de livraison. | **Faible** (Automatisation) | **Fort** (Réduction de l'anxiété d'attente et des appels SAV). | Volume d'appels SAV pour retard (Cible : -35%). |
| **3. SLA & Modération Vendeurs Marketplace** | Mettre sous surveillance et appliquer des pénalités aux vendeurs présentant >5% d'expéditions hors délais ou de produits non conformes. | **Élevé** (Gouvernance) | **Fort** (Éradication des causes racines `LIV_NONRECU` et `PROD_NONCONFORME`). | Taux de conformité d'expédition vendeurs (Cible : > 98%). |


