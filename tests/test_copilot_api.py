"""
tests/test_copilot_api.py - Tests unitaires des endpoints de l'API Copilote Commercial.
"""

import pytest
from fastapi.testclient import TestClient

from copilot.api.main import app

client = TestClient(app)

API_KEY_HEADER = {"X-API-Key": "dev-secret-key"}


def test_health_check():
    """Vérifie le point de contrôle de santé (non sécurisé par clé API)."""
    response = client.get("/sante")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"


def test_unauthorized_access():
    """Vérifie qu'une clé API manquante ou invalide renvoie une erreur 401."""
    # Clé manquante
    response = client.get("/clients/12345")
    assert response.status_code == 401
    assert "Clé d'API invalide" in response.json()["detail"]

    # Clé invalide
    response = client.get("/clients/12345", headers={"X-API-Key": "bad-key"})
    assert response.status_code == 401


def test_get_client_profile_success():
    """Vérifie la récupération d'un profil client existant."""
    response = client.get("/clients/12345", headers=API_KEY_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == "12345"
    assert "segment" in data
    assert "next_best_action" in data
    assert "avg_basket_gbp" in data


def test_get_client_profile_not_found():
    """Vérifie la gestion d'un client introuvable."""
    response = client.get("/clients/invalid_id", headers=API_KEY_HEADER)
    assert response.status_code == 404
    assert "introuvable" in response.json()["detail"]


def test_get_client_purchases():
    """Vérifie la récupération des achats d'un client."""
    response = client.get("/clients/12345/achats?top=3", headers=API_KEY_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == "12345"
    assert len(data["top_purchases"]) > 0
    assert "stock_code" in data["top_purchases"][0]


def test_get_product_pricing_success():
    """Vérifie la récupération des infos pricing d'un produit valide."""
    response = client.get("/produits/22423/prix", headers=API_KEY_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["stock_code"] == "22423"
    assert "elasticity" in data
    assert "rec_price_gbp" in data


def test_get_product_pricing_not_found():
    """Vérifie qu'un produit inexistant renvoie 404."""
    response = client.get("/produits/UNKNOWN999/prix", headers=API_KEY_HEADER)
    assert response.status_code == 404


def test_get_commercial_policy():
    """Vérifie la consultation de la politique commerciale."""
    response = client.get("/politique-commerciale", headers=API_KEY_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert len(data["rules_by_segment"]) > 0
    assert "excluded_stock_codes" in data
    assert data["escalation_threshold_pct"] == 10.0


def test_get_client_opportunities():
    """Vérifie la détection d'opportunités pour un client."""
    response = client.get("/clients/12345/opportunites", headers=API_KEY_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == "12345"
    assert "opportunities" in data


def test_verify_offer_compliance_approved():
    """Vérifie qu'une offre conforme (ex: 5% pour un client) est approuvée."""
    payload = {
        "customer_id": "12345",
        "stock_code": "22423",
        "proposed_discount_pct": 5.0
    }
    response = client.post("/offres/verifier", json=payload, headers=API_KEY_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["is_compliant"] is True
    assert "Approuvé" in data["status"]


def test_verify_offer_compliance_escalated():
    """Vérifie qu'une remise excessive déclenche une escalade."""
    payload = {
        "customer_id": "12345",
        "stock_code": "22423",
        "proposed_discount_pct": 25.0
    }
    response = client.post("/offres/verifier", json=payload, headers=API_KEY_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["is_compliant"] is False
    assert "Escalade requise" in data["status"]


def test_verify_offer_compliance_excluded_product():
    """Vérifie le refus automatique sur un produit exclu de toute remise."""
    payload = {
        "customer_id": "12345",
        "stock_code": "POST",
        "proposed_discount_pct": 2.0
    }
    response = client.post("/offres/verifier", json=payload, headers=API_KEY_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["is_compliant"] is False
    assert "Produit exclu" in data["status"]
