# Restitution Stratégique - Segmentation & Portefeuille Produits (Online Retail II)

---

## Slide 1 : Le Portefeuille Clients
### Les 25,2 % de clients Champions génèrent 69,3 % du chiffre d'affaires, tandis que 59 grossistes concentrent à eux seuls 32,1 % de l'activité.

> **Synthèse Exécutive** : L'analyse déterministe RFM sur 5 852 clients identifie une ultra-concentration des revenus et une fragilité majeure sur le segment à risque (£1.64M sous menace de churn).

### Poids des Segments Clients & Dépendance Grossistes
- **Champions** (*25.2 % des clients*) : **£12.08M** du CA (*69.3 %* du chiffre d'affaires total, CA moyen par client sur la période £8 190.82).
- **Fidèles** (*20.6 % des clients*) : **£2.46M** du CA (*14.1 %* du CA, CA moyen par client sur la période £2 042.14).
- **À risque** (*14.1 % des clients*) : **£1.64M** de CA menacé (*9.4 %* du CA, récence moyenne de **368 jours**).
- **En sommeil** (*25.8 % des clients*) : **£633k** de CA dormant (*3.6 %* du CA, récence moyenne de **457 jours**).
- **Dépendance Grossistes (Top 1% CA)** : **59 clients** représentent à eux seuls **32.06 % du CA global** (£5.59M).

---

## Slide 2 : Personas & Next Best Actions
### Chaque segment client requiert une stratégie d'activation dédiée pour maximiser la valeur et prévenir le churn.

> **Feuille de Route d'Activation LLM** : Traduction des statistiques RFM en 6 personas actionnables pour alimenter la personnalisation CRM et le copilote d'action.

| Segment | Persona LLM | Action Marketing Recommandée (Next Best Action) | Canal Privilégié | KPI de Suivi |
|---|---|---|---|---|
| **Champions** | L'Élite Ambassadrice | Offrir un accès VIP avant-première et un service conciergerie personnalisé. | Conciergerie / Email VIP | Taux de rétention VIP (>95%) |
| **Fidèles** | Le Pilier Régulier | Proposer un programme de fidélité à paliers et des recommandations croisées. | Email personnalisé | Fréquence d'achat (+15%) |
| **Prometteurs** | L'Acheteur en Ascension | Envoyer une offre d'upsell ciblée sur les catégories complémentaires. | Notifications App / Email | Taux de conversion basket (+10%) |
| **Nouveaux** | L'Explorateur à Fort Potentiel | Déclencher un parcours de bienvenue avec tutoriels et remise 2ème achat. | SMS / Email d'accueil | Taux de réachat à 30j (>30%) |
| **À risque** | Le Grand Habitué Endormi | Lancer une campagne d'appel ou de réengagement direct avec coupon exclusif. | Phoning / SMS dédié | Réactivation du CA (£1.64M) |
| **En sommeil** | Le Client Distant | Activer une séquence automatique de relance promotionnelle automatisée. | Email réengagement | Taux de réactivation (>5%) |

---

## Slide 3 : Le Portefeuille Produits
### La longue traîne étouffe la rentabilité : 52,8 % des références ne génèrent que 5 % du CA et 1 737 produits C doivent être supprimés.

> **Rationalisation du Catalogue** : Application de la loi de Pareto (80/15/5) révélant une saturation logistique par des références sans contribution ni pertinence pour les clients VIP.

### Répartition Pareto ABC & Opportunité de Suppression
- **Classe A (80 % du CA)** : **1 036 références** (21.1 % du catalogue) génèrent **£16.10M**.
- **Classe B (15 % du CA)** : **1 281 références** (26.1 % du catalogue) génèrent **£3.02M**.
- **Classe C (5 % du CA)** : **2 590 références** (52.8 % du catalogue) ne génèrent que **£1.01M**.
- **Déréférenciation Ciblée** : **1 737 références C** identifiées pour suppression (tendance des ventes négative et absence d'achat par les clients Champions/Fidèles).
- **CA Produit à Risque** : **£639k** couverts par des produits de substitution du catalogue.

---

## Slide 4 : Business Cases Financiers & Sensibilité
### La réactivation est rentable dès 0,29 % de réponse incrémentale et la déréférenciation est rentable dès £76,89 de coût logistique par SKU.

> **Synthèse des Business Cases** : Évaluation financière rigoureuse intégrant les coûts opérationnels, les groupes de contrôle et les seuils de rentabilité.

### Business Case A : Reconquête des Clients À Risque (Seuil de Rentabilité)
- **Périmètre Cible** : 745 clients ciblés (83 clients préservés en groupe de contrôle AB testing).
- **Investissement & Coût** : **£1 490** (£2.00 / contact).
- **Seuil de Rentabilité (Break-even)** : **0.29 %** de taux de réponse incrémentale minimum.
- **Gain Net Financier (Scénario 6 %)** : **£39 779.84** (ROI : **2 669.8 %**).
- **Sensibilité Clé** : Sensible au taux de marge (de £22k à 20% de marge à £68k à 50% de marge).

### Business Case B : Rationalisation Catalogue SKUs (Seuil de Rentabilité)
- **Périmètre Cible** : **1 737 références C** supprimées.
- **Seuil de Rentabilité Logistique (Break-even SKU Cost)** : Rentable dès **£76.89 / SKU / an** de coût de complexité fixe (vs £500 retenus dans le scénario central, dégageant **£756 670** net).
- **Taux de Transfert Minimum (Break-even Transfer Rate)** : Opération rentable dès **0 % de report d'achat** (marge perdue de £111,8k largement inférieure aux £868,5k d'économies logistiques).
- **Sensibilité Clé** : Si le taux de transfert tombe à 10 %, le gain net reste très largement positif à **£687k**.

### Limites & Périmètre d'Interprétation (Projet 2)
1. **Données transactionnelles historiques** : Absence d'informations sociodémographiques clients ou de mesure directe de la satisfaction; périmètre limité aux transactions enregistrées.
2. **Hypothèses des Business Cases** : Le taux de réengagement (6 %) et le taux de transfert (50 %) reposent sur des benchmarks sectoriels et nécessitent une validation in vivo par A/B Testing.
3. **Coûts de complexité logistique** : Le coût fixe de £500 / SKU / an est une moyenne forfaitaire; la déréférenciation effective exige de vérifier les contraintes contractuelles fournisseurs (MOQ, pénalités) et la gestion des stocks résiduels.
