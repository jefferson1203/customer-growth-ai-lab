# Restitution Stratégique — Voix du Client IA (Olist E-Commerce)

---

## Slide 1 : Le Constat
### 🎯 Les retards de livraison et les colis non reçus expliquent plus de 61 % des détracteurs d'Olist.

* **NPS Proxy Global** : **+15.09** (Basé sur 40 641 avis — 64.8 % de Promoteurs 5★ vs 35.2 % de Détracteurs 1-3★).
* **Top 3 des Irritants Clients** (détectés par LLM Gemini) :
  1. **`LIV_NONRECU`** (Colis non reçu / incomplet) : **39.7 %** des avis négatifs (Note moyenne : 1.81 / 5).
  2. **`SAV`** (Support / Remboursement lent ou inefficace) : **21.8 %** des avis négatifs (Note moyenne : 1.68 / 5).
  3. **`PROD_NONCONFORME`** (Produit différent de la description) : **19.3 %** des avis négatifs (Note moyenne : 2.19 / 5).
* **Facteur aggravant** : Les irritants logistiques cumulés représentent la majorité absolue du mécontentement client.

---

## Slide 2 : Les Causes & Le Seuil Critique
### 🚨 À partir de 4 jours de retard de livraison, le taux de détracteurs bondit à 87.3 %.

* **Dégradation de la satisfaction par tranche de retard** :
  * *À l'heure ou en avance* : Note moyenne **3.98 / 5** | **27.1 %** de détracteurs (35 049 commandes).
  * *Retard de 1 à 3 jours* : Note moyenne **2.79 / 5** | **60.2 %** de détracteurs (889 commandes).
  * *Retard de 4 à 10 jours* : Note moyenne **1.72 / 5** | **87.3 %** de détracteurs (1 515 commandes).
  * *Retard > 10 jours* : Note moyenne **1.56 / 5** | **91.4 %** de détracteurs (1 343 commandes).
* **Verbatims représentatifs (Traduits & Résumés par LLM)** :
  > *"Produit jamais reçu, aucune réponse du service client après 3 semaines de retard."* (Score : 1★)
  > *"Livraison décalée deux fois sans information, le vendeur ne répond pas aux messages."* (Score : 1★)

---

## Slide 3 : Plan d'Action & Recommandations
### 💡 Trois chantiers prioritaires pour réduire de 25 % les détracteurs et redresser le NPS de +10 points.

| Chantier Prioritaire | Action Concrète | Effort | Impact Attendu | KPI de Suivi |
|---|---|---|---|---|
| **1. Boucle d'action proactive (NPS Prédictif)** | Déclencher une alerte et un coupon d'excuse préventif dès la livraison pour le Top 10% des commandes à risque (Gradient Boosting). | **Moyen** (API & CRM) | **Fort** (Ciblage de 90% de vrais détracteurs avec un Lift de 2.56x). | Taux de rétention des commandes à risque (KPI cible : > 75%). |
| **2. Gestion du seuil critique des 4 jours** | Envoyer une notification SMS/WhatsApp automatique au 3ème jour de retard avec réestimation transparente de la date de livraison. | **Faible** (Automatisation) | **Fort** (Réduction de la frustration d'attente passive). | Taux de réclamation SAV sur retard (Cible : -30%). |
| **3. SLA & Pénalités Vendeurs Marketplace** | Mettre sous surveillance et pénaliser les vendeurs avec plus de 5% de produits non conformes ou de retards d'expédition. | **Élevé** (Gouvernance) | **Très Fort** (Éradication de la cause racine `LIV_NONRECU`). | Taux de conformité des expéditions vendeurs (Cible : > 98%). |
