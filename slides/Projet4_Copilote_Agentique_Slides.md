# Slides de Cadrage Executive — Projet 4 : Copilote Agentique Commercial
*Customer & Growth AI Lab*

---

## Slide 1 : Le Cas d'Usage Commercial
### L'IA au Service des Conseillers & Commerciaux

- **Objectif** : Réduire le temps de préparation des rendez-vous clients et sécuriser les propositions tarifaires.
- **Tâche automatisée** : Synthèse du profil client (RFM), recommandations de pricing dynamique, vérification des remises et génération du projet d'e-mail.
- **Gain de temps estimé** : **-60% de temps de préparation** (passant de 25 min à 10 min par appel client).
  > *Note : Ce gain de temps est une hypothèse à mesurer lors de la phase pilote.*

---

## Slide 2 : Architecture & Garde-fous Anti-Hallucination
### Une Décision Assistée sous Contrôle Déterministe

```
Commercial (Chat n8n / Web UI) ──► Agent IA (LLM + Mémoire + RAG)
                                        │
┌───────────────────────────────────────┴───────────────────────────────────────┐
│                          Outils REST FastAPI (Lecture Seule)                  │
├───────────────────────────────┬───────────────────────────────┬───────────────┤
│ Profil Client RFM             │ Historique Achats             │ Pricing & Recommandation
└───────────────────────────────┴───────────────────────────────┴───────────────┘
                                        │
                                        ▼
                   Brouillon d'Offre Commerciale
                                        │
                                        ▼
             Contrôle Déterministe (Plafond Remise Segment)
                                        │
           ┌────────────────────────────┴────────────────────────────┐
           ▼                                                         ▼
[Approuvé Auto (<= Plafond)]                             [Escalade / Validation Humaine]
           │                                                         │
           └────────────────────────────┬────────────────────────────┘
                                        ▼
                           Journal d'Audit & Décisions
```

- **Sécurité** : Aucun accès SQL direct par l'agent. Les chiffres proviennent à 100% de l'API REST FastAPI déterministe.
- **Validation Humaine (Human-in-the-loop)** : Aucune proposition commerciale n'est envoyée au client sans l'approbation explicite d'un responsable.

---

## Slide 3 : Déploiement GCP Cloud Run & Gouvernance
### Industrialisation, Indicateurs & Conformité

- **Déploiement GCP Cloud Run** : Conteneur hybride Uvicorn + Streamlit déployé et actif en production sur Google Cloud Run.
- **Indicateurs de Performance (KPIs)** :
  1. Taux d'acceptation sans modification des brouillons d'e-mails (Cible > 80%).
  2. Temps moyen de préparation des appels (-60% de gain de temps).
  3. Évolution des remises moyennes accordées (Cible : baisse des dérogations hors plafond).
- **Gouvernance & RGPD** :
  - Minimisation des données : seuls des identifiants clients anonymisés sont manipulés.
  - Conformité AI Act : transparence totale vis-à-vis des utilisateurs et supervision humaine systématique.
