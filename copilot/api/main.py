"""
copilot/api/main.py - Application FastAPI pour le Copilote Commercial avec doc Swagger automatique.
"""

from fastapi import FastAPI, HTTPException, Security, Depends, status
from fastapi.security.api_key import APIKeyHeader
import os

from copilot.api.schemas import (
    ClientProfileResponse,
    CustomerPurchasesResponse,
    ProductPricingResponse,
    CommercialPolicyResponse,
    CustomerOpportunitiesResponse,
    OfferVerificationRequest,
    OfferVerificationResponse,
    HealthResponse
)
from copilot.api.services import (
    get_client_profile_service,
    get_client_purchases_service,
    get_product_pricing_service,
    get_commercial_policy_service,
    get_client_opportunities_service,
    verify_offer_compliance_service
)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(
    title="Customer & Growth AI Lab — API Copilote Commercial",
    description="API REST sécurisée en lecture seule pour alimenter l'agent décisionnel commercial avec documentation Swagger/OpenAPI.",
    version="1.0.0"
)


def verify_api_key(api_key: str = Security(api_key_header)):
    """Vérifie la clé API transmise dans l'en-tête HTTP X-API-Key."""
    expected_key = os.getenv("COPILOT_API_KEY", "dev-secret-key")
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé d'API invalide ou manquante dans l'en-tête X-API-Key."
        )


@app.get("/sante", response_model=HealthResponse, tags=["Système"])
def health_check():
    """Point de contrôle de l'état de l'API."""
    return HealthResponse(status="ok", version="1.0.0")


@app.get(
    "/clients/{customer_id}",
    response_model=ClientProfileResponse,
    tags=["Clients"],
    dependencies=[Depends(verify_api_key)]
)
def get_client_profile(customer_id: str):
    """Récupère le profil RFM, le segment et la Next Best Action d'un client."""
    profile = get_client_profile_service(customer_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Client '{customer_id}' introuvable dans la base RFM.")
    return profile


@app.get(
    "/clients/{customer_id}/achats",
    response_model=CustomerPurchasesResponse,
    tags=["Clients"],
    dependencies=[Depends(verify_api_key)]
)
def get_client_purchases(customer_id: str, top: int = 10):
    """Récupère les N articles les plus achetés par un client."""
    purchases = get_client_purchases_service(customer_id, top_n=top)
    if purchases is None:
        raise HTTPException(status_code=404, detail=f"Client '{customer_id}' introuvable.")
    return CustomerPurchasesResponse(customer_id=customer_id, top_purchases=purchases)


@app.get(
    "/produits/{stock_code}/prix",
    response_model=ProductPricingResponse,
    tags=["Produits & Pricing"],
    dependencies=[Depends(verify_api_key)]
)
def get_product_pricing(stock_code: str):
    """Récupère la recommandation de prix, l'élasticité et le statut de fiabilité d'un produit."""
    pricing_data = get_product_pricing_service(stock_code)
    if not pricing_data:
        raise HTTPException(status_code=404, detail=f"Produit '{stock_code}' introuvable dans le modèle de pricing.")
    return pricing_data


@app.get(
    "/politique-commerciale",
    response_model=CommercialPolicyResponse,
    tags=["Politique Commerciale"],
    dependencies=[Depends(verify_api_key)]
)
def get_commercial_policy():
    """Consulte les plafonds de remises autorisés par segment et les règles d'escalade."""
    return get_commercial_policy_service()


@app.get(
    "/clients/{customer_id}/opportunites",
    response_model=CustomerOpportunitiesResponse,
    tags=["Clients"],
    dependencies=[Depends(verify_api_key)]
)
def get_client_opportunities(customer_id: str):
    """Identifie les opportunités d'optimisation de pricing sur les produits achetés par un client."""
    opps = get_client_opportunities_service(customer_id)
    if not opps:
        raise HTTPException(status_code=404, detail=f"Client '{customer_id}' introuvable.")
    return opps


@app.post(
    "/offres/verifier",
    response_model=OfferVerificationResponse,
    tags=["Gouvernance & Garde-fous"],
    dependencies=[Depends(verify_api_key)]
)
def verify_offer_compliance(request: OfferVerificationRequest):
    """Vérifie déterministement la conformité d'une proposition commerciale contre les règles de gestion."""
    return verify_offer_compliance_service(
        request.customer_id,
        request.stock_code,
        request.proposed_discount_pct
    )
