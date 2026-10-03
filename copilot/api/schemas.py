"""
copilot/api/schemas.py - Modèles Pydantic pour la validation et la doc Swagger FastAPI.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ClientProfileResponse(BaseModel):
    """Schéma de réponse pour le profil RFM et Next Best Action d'un client."""
    customer_id: str = Field(..., description="Identifiant unique du client")
    segment: str = Field(..., description="Segment RFM (ex: Champions, À risque...)")
    recency_days: int = Field(..., description="Récence en jours depuis le dernier achat")
    frequency: int = Field(..., description="Nombre total de commandes passées")
    monetary_gbp: float = Field(..., description="Montant total dépensé en GBP (£)")
    rfm_score: str = Field(..., description="Score RFM (ex: '555')")
    avg_basket_gbp: float = Field(..., description="Panier moyen par commande en GBP (£)")
    last_purchase_date: Optional[str] = Field(None, description="Date du dernier achat (YYYY-MM-DD)")
    next_best_action: str = Field(..., description="Recommandation d'action commerciale")


class PurchasedItemSchema(BaseModel):
    """Schéma d'un article acheté par le client."""
    stock_code: str = Field(..., description="Code référence produit")
    description: str = Field(..., description="Description du produit")
    total_quantity: int = Field(..., description="Quantité totale achetée sur 2 ans")
    avg_price_paid_gbp: float = Field(..., description="Prix unitaire moyen payé par le client en GBP (£)")


class CustomerPurchasesResponse(BaseModel):
    """Schéma de réponse pour l'historique des articles achetés par un client."""
    customer_id: str = Field(..., description="Identifiant unique du client")
    top_purchases: List[PurchasedItemSchema] = Field(..., description="Liste des articles les plus achetés")


class ProductPricingResponse(BaseModel):
    """Schéma de réponse pour la recommandation de prix d'un produit."""
    stock_code: str = Field(..., description="Code référence produit")
    description: str = Field(..., description="Description du produit")
    category: str = Field(..., description="Catégorie d'élasticité (Élastique, Inélastique, Non significatif)")
    elasticity: float = Field(..., description="Élasticité-prix mesurée (OLS log-log)")
    current_price_gbp: float = Field(..., description="Prix actuel de référence sur 12 semaines (£)")
    rec_price_gbp: float = Field(..., description="Prix recommandé optimisé sous garde-fous (£)")
    price_change_pct: float = Field(..., description="Pourcentage de variation de prix")
    margin_gain_gbp: float = Field(..., description="Gain de marge attendu en GBP (£)")
    control_status: str = Field(..., description="Statut du contrôle anti-hallucination (ex: Validé)")
    justification: str = Field(..., description="Justification commerciale de l'ajustement tarifaire")


class HealthResponse(BaseModel):
    """Schéma de réponse du point de contrôle de santé."""
    status: str = Field(..., description="État du service (ex: ok)")
    version: str = Field(..., description="Version du service API")

# --- NOUVEAUX SCHÉMAS ENRICHIS ---

class PolicyRuleSchema(BaseModel):
    """Règle de remise autorisée par segment."""
    segment: str = Field(..., description="Nom du segment RFM")
    max_discount_pct: float = Field(..., description="Taux de remise maximal autorisé sans escalade (%)")
    conditions: str = Field(..., description="Conditions d'application de la remise")


class CommercialPolicyResponse(BaseModel):
    """Schéma de réponse de la politique commerciale globale."""
    rules_by_segment: List[PolicyRuleSchema] = Field(..., description="Règles de remises par segment")
    excluded_stock_codes: List[str] = Field(..., description="Liste des StockCodes exclus de toute remise")
    escalation_threshold_pct: float = Field(..., description="Seuil déclenchant une escalade obligatoire (%)")


class PricingOpportunitySchema(BaseModel):
    """Opportunité de pricing pour un produit acheté par un client."""
    stock_code: str = Field(..., description="Code référence produit")
    description: str = Field(..., description="Description du produit")
    current_price_gbp: float = Field(..., description="Prix actuel payé/référencé (£)")
    rec_price_gbp: float = Field(..., description="Prix recommandé optimisé (£)")
    price_change_pct: float = Field(..., description="Variation de prix proposée (%)")
    margin_gain_gbp: float = Field(..., description="Gain de marge attendu (£)")
    recommendation_type: str = Field(..., description="Type d'opportunité (Baisse stimulante, Hausse de marge)")


class CustomerOpportunitiesResponse(BaseModel):
    """Schéma de réponse pour les opportunités tarifaires croisées d'un client."""
    customer_id: str = Field(..., description="Identifiant unique du client")
    segment: str = Field(..., description="Segment RFM")
    opportunities: List[PricingOpportunitySchema] = Field(..., description="Liste des opportunités de pricing sur ses produits")


class OfferVerificationRequest(BaseModel):
    """Requête de vérification d'une proposition commerciale."""
    customer_id: str = Field(..., description="Identifiant du client")
    stock_code: str = Field(..., description="Code produit de l'offre")
    proposed_discount_pct: float = Field(..., description="Taux de remise proposé (%)")


class OfferVerificationResponse(BaseModel):
    """Résultat de la vérification déterministe de garde-fou."""
    is_compliant: bool = Field(..., description="Indique si l'offre respecte la politique commerciale")
    status: str = Field(..., description="Statut (Approuvé automatiquement, Escalade requise, Refusé)")
    max_allowed_discount_pct: float = Field(..., description="Plafond de remise autorisé pour ce segment (%)")
    explanation: str = Field(..., description="Explication détaillée de la règle appliquée")
