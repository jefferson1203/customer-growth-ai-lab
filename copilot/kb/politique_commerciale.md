# Politique Commerciale & Directives Négociation — Customer & Growth AI Lab

## 1. Cadre Général & Plafonds de Remises par Segment RFM

La politique tarifaire et les remises accordées aux clients sont strictement régies par leur classification RFM (Recency, Frequency, Monetary). 
Toute remise proposée par un commercial ou le Copilote AI doit respecter les plafonds maximaux ci-dessous :

| Segment RFM | Plafond Remise Max (%) | Conditions d'Eligibilité | Action Recommandée (Next Best Action) |
| :--- | :--- | :--- | :--- |
| **Champions** | **8.0 %** | Commandes > £500 | Accès VIP Concierge, Ventes privées avant-première |
| **Fidèles** | **6.0 %** | Fréquence >= 5 commandes | Cross-selling sur catégories complémentaires |
| **À risque** | **10.0 %** | Offre spéciale réactivation (1ère commande post-inactivité) | Campagne urgente de reconquête personnalisée |
| **En sommeil** | **5.0 %** | Soumis à réactivation téléphonique préalable | Questionnaire d'insatisfaction + offre timide |
| **Prometteurs** | **5.0 %** | Valable sur le 2ème achat | Parcours de bienvenue & découverte produit |
| **Nouveaux** | **5.0 %** | Offre de bienvenue premier réachat | Accompagnement prise en main + frais de port offerts |

---

## 2. Garde-fous et Produits Exclus de Remises

### Produits Exclus (Strict Discount Exclusion)
Certaines références d'articles et codes administratifs sont **strictement exclus** de tout geste commercial ou remise tarifaire :
- Codes administratifs : `TEST001`, `POST` (Frais de port), `MANUAL` (Ajustement manuel), `M` (Frais bancaires / manuels).
- Cartes / Chèques cadeaux : `GIFT_0001_30`, `GIFT_0001_20`.

> **Règle absolue** : Toute tentative d'appliquer une remise même de 1% sur une référence exclue doit être automatiquement rejetée par l'API et le Copilote (`status: Refusé (Produit exclu)`).

---

## 3. Matrice de Procédure d'Escalade et Validation Humaine

Lorsqu'un commercial souhaite accorder un geste supérieur aux plafonds autorisés :
1. **Dépassement <= Plafond Segment** : Approbation automatique déterministe via l'API.
2. **Dépassement > Plafond Segment** : Statut `Escalade requise (Dépassement plafond)`. La demande doit être validée par le Directeur Commercial via l'interface du Copilote.
3. **Escalade pour Client à Risque** : Une remise jusqu'à 15% peut être accordée exceptionnellement à un client *À risque* uniquement après accord écrit du VP Sales.

---

## 4. Stratégie d'Optimisation Tarifaire & Élasticités

- **Produits Élastiques (e < -1.0)** : Les baisses de prix mesurées stimulent fortement la demande en volume et maximisent la marge brute globale.
- **Produits Inélastiques (-1.0 <= e <= 0)** : Les prix peuvent être réhaussés sans perte majeure de volume pour capturer de la marge directe.
- **Produits à Faible Fiabilité Statistique (p-value > 0.05)** : Recommandation de prix verrouillée par sécurité (maintien du prix actuel).
