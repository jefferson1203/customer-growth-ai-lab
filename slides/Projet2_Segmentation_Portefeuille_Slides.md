# Restitution Stratégique - Segmentation & Portefeuille Produits (Online Retail II)

---

## Slide 1 : Le Portefeuille Clients
### Les 25,2 % de clients Champions génèrent 69,3 % du chiffre d'affaires, tandis que 59 grossistes concentrent à eux seuls 32,1 % de l'activité.

> **Synthèse Exécutive** : L'analyse déterministe RFM sur 5 852 clients identifie une ultra-concentration des revenus et une fragilité majeure sur le segment à risque (£1.64M sous menace de churn).

### Poids des Segments Clients & Dépendance Grossistes
- **Champions** (*25.2 % des clients*) : **£12.08M** du CA (*69.3 %* du chiffre d'affaires total, panier moyen £8 190.82).
- **Fidèles** (*20.6 % des clients*) : **£2.46M** du CA (*14.1 %* du CA, panier moyen £2 042.14).
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

## Slide 4 : Les Business Cases Financiers
### Deux leviers complémentaires génèrent un gain net combiné de £796 449 par an avec des retours sur investissement exceptionnels.

> **Synthèse des Business Cases** : Évaluation financière rigoureuse intégrant les coûts opérationnels, les groupes de contrôle et l'analyse de sensibilité.

### Business Case A : Reconquête des Clients À Risque (Scénario Central)
- **Périmètre Cible** : 745 clients ciblés (83 clients préservés en groupe de contrôle AB testing).
- **Investissement & Coût** : **£1 490** (£2.00 / contact).
- **Gain Net Financier** : **£39 779.84** (ROI : **2 669.8 %**).
- **Seuil de Rentabilité (Break-even)** : **0.29 %** de taux de réponse.
- **Sensibilité Clé** : Sensible au taux de marge (de £22k à 20% de marge à £68k à 50% de marge).

### Business Case B : Rationalisation Catalogue SKUs (Scénario Central)
- **Périmètre Cible** : **1 737 références C** supprimées.
- **Économies Logistiques** : **£868 500** (£500 de coût de complexité économisé par SKU/an).
- **Marge Perdue** : **£111 830.36** (Hypothèse de 50 % de transfert d'achat vers références A/B).
- **Gain Net Financier** : **£756 669.64**.
- **Sensibilité Clé** : Si le taux de transfert tombe à 10 %, le gain net reste très largement positif à **£687k**.

### Hypothèses Clés à Valider avec le Client en Atelier
1. **Coût de contact CRM** : Confirmer le coût unitaire réel de £2.00 / client à risque.
2. **Taux de transfert d'achat B** : Valider avec le Merchandising l'existence de substituts proches pour les 1 737 SKUs C.
3. **Coût annuel de complexité SKU** : Valider avec la Logistique le coût fixe de possession de £500 / SKU / an.


