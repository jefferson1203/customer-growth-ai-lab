# Restitution Stratégique — Optimisation du Pricing & Élasticité Prix

---

## Slide 1 : La Politique Tarifaire Actuelle
### 75,5 % des références présentent une dispersion de prix supérieure à 2x sans grille tarifaire structurée.

> **Synthèse Exécutive** : L'audit de la politique tarifaire sur 4 905 SKUs du catalogue Online Retail II met en évidence une dispersion extrême des prix unitaires (ratio médian Pmax / Pmin = 2.6x). La remise implicite moyenne accordée au Top 1% des grossistes n'est que de 5.13 %, témoignant de remises informelles et non négociées qui dégradent la marge brute.

### Audit Tarifaire & Fuites de Marge
- **Périmètre Catalogue Analysé** : **4 905 SKUs** (dont **1 993 éligibles** sur au moins 40 semaines de ventes et CV >= 5%).
- **Dispersion des Prix Unitaires** : **75,5 %** des références affichent un écart Pmax / Pmin >= 2x, lié à l'absence de tarif de référence dynamique.
- **Politique de Remises Informelle** : Prix unitaire moyen de **£1.95** pour les clients standards vs **£1.85** pour le Top 1% grossistes (remise de **5.13 %** seulement malgré des volumes 10x plus élevés).
- **Enjeu Stratégique** : Structurer une politique de pricing dynamique basée sur l'élasticité réelle pour stopper la fuite de valeur.

---

## Slide 2 : Ce que Disent les Données (Économétrie & Élasticités)
### 74 % de demandes élastiques et 22 % de références exclues par incertitude statistique (p >= 0.10).

> **Modélisation Économétrique** : Ajustement Log-Log OLS (ln(Q) = alpha + elasticity * ln(P) + effets_mois) sur le Top 50 SKUs par CA pour neutraliser les biais de saisonnalité mensuelle.

### Distribution des Élasticités (N = 50) & Justification des Exclusions
- **Demandes Élastiques (elasticity < -1.0, p < 0.10)** : **37 SKUs (74 %)**, élasticité moyenne de **-2.78**. Une baisse optimisée de prix stimule fortement les volumes et le CA.
- **Demandes Inélastiques (-1.0 <= elasticity < 0, p < 0.10)** : **2 SKUs (4 %)**. Une hausse mesurée augmente la marge nette sans perdre de volume significatif.
- **Références Exclues / Non Concluantes (p >= 0.10 ou elasticity >= 0)** : **11 SKUs (22 %)** où l'on ne peut pas conclure scientifiquement.
  * *Pourquoi ?* P-value trop élevée (p >= 0.10, incertitude statistique due au bruit) ou élasticité positive (effet Veblen/Giffen ou promotions croisées).
  * *Règle de Prudence* : Exclusion automatique de toute recommandation algorithmique pour prévenir les pertes financières.

---

## Slide 3 : Le Moteur d'Optimisation & Plan d'Action
### Un gain central de +£123 012,77 (+6,72 %) sécurisé sous garde-fous métier et validation humaine.

> **Moteur de Recommandation & Gouvernance** : Application de prix cibles sous contraintes strictes, contrôlés par LLM anti-hallucination (Regex) et soumis à arbitrage humain.

### Impact Financier, Garde-fous et Feuille de Route
- **Impact Financier selon le Coût Unitaire** :
  * **Scénario Central (Coût = 50% prix)** : **+£123 012,77** de marge additionnelle (**+6,72 %**).
  * **Analyse de Sensibilité** : Gain de **+£167 010,45 (+7,62 %)** à 40% de coût et **+£92 015,10 (+6,29 %)** à 60% de coût.
- **Garde-fous Métier Stricts** : Variation maximale plafonnée à **+/- 10%**, markup minimum de **1.2x**, arrondis psychologiques obligatoires en `,49` ou `,99`.
- **Validation Humaine (Human-in-the-Loop)** : Décision enregistrée dans `outputs/pricing/decisions.csv` après lecture des justifications Gemini (validées à 100% par Regex anti-hallucination).
- **Prochaine Étape Opérationnelle** : Lancer un **Test A/B in vivo sur 5 références clés** pour mesurer l'élasticité réelle sur 4 semaines avant le déploiement généralisé.
