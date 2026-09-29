"""
voc/schema.py - Schéma Pydantic strict pour la classification des avis VoC.
"""

from typing import List, Literal
from pydantic import BaseModel, Field

# Grille stricte des 9 codes d'irritants
IrritantCode = Literal[
    "LIV_RETARD",
    "LIV_NONRECU",
    "SAV",
    "PROD_QUALITE",
    "PROD_NONCONFORME",
    "PROD_ENDOMMAGE",
    "PRIX",
    "POSITIF",
    "AUTRE"
]

SentimentType = Literal["positif", "negatif", "neutre"]
UrgenceType = Literal["haute", "moyenne", "basse"]


class ReviewLabel(BaseModel):
    irritants: List[IrritantCode] = Field(..., description="Liste des codes d'irritants applicables")
    sentiment: SentimentType = Field(..., description="Sentiment global de l'avis")
    urgence: UrgenceType = Field(..., description="Niveau d'urgence de la réclamation")
    resume_fr: str = Field(..., description="Résumé synthétique en français (1-2 phrases)")
