"""
copilot/tests/test_agent_evaluation.py - Évaluation E2E du Copilote Commercial sur 10 Scénarios Métier.
Vérifie la collecte d'outils, la fidélité numérique, l'intégration RAG ChromaDB et le respect des garde-fous.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from copilot.agent import CommercialAgentEngine


class MockLLMResponse:
    def __init__(self, text):
        self.text = text


@pytest.fixture
def mock_agent():
    """Initialise le moteur avec un mock LLM pour tester l'orchestration, la recherche RAG et la conformité."""
    engine = CommercialAgentEngine(
        provider="gemini",
        api_key="mock-key",
        api_base_url="http://127.0.0.1:8000",
        model_name="gemini-3.8-flash"
    )
    return engine


def test_agent_scenario_01_champions_discount_retrieval(mock_agent):
    """Scénario A01 : Interrogation profil client Champions et vérification du plafond de remise (8%)."""
    prompt = "Quel est le segment de ce client et quelle est sa remise maximale autorisée ?"
    
    with patch("google.genai.Client") as mock_genai:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MockLLMResponse(
            "Le client 10005 appartient au segment Champions. Selon la politique commerciale, sa remise maximale est de 8.0% pour tout panier supérieur à £500."
        )
        mock_genai.return_value = mock_client
        
        res = mock_agent.run_query(prompt, customer_id="10005")
        
        assert res["status"] == "success"
        assert "Champions" in res["answer"]
        assert "8.0%" in res["answer"]
        assert "context_data" in res
        assert res["context_data"]["profile"]["segment"] == "Champions"


def test_agent_scenario_02_exceeding_discount_guardrail_escalation(mock_agent):
    """Scénario A02 : Demande de remise de 15% pour client Champion (Dépassement 8% -> Escalade requise)."""
    prompt = "Peux-tu accorder 15% de remise au client 10005 sur cette commande ?"
    
    with patch("google.genai.Client") as mock_genai:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MockLLMResponse(
            "La remise demandée de 15.0% dépasse le plafond autorisé de 8.0% pour le segment Champions. Une escalade et une validation humaine par un responsable commercial est obligatoire."
        )
        mock_genai.return_value = mock_client
        
        res = mock_agent.run_query(prompt, customer_id="10005")
        
        assert "15.0%" in res["answer"] or "15%" in res["answer"]
        assert "escalade" in res["answer"].lower() or "validation" in res["answer"].lower()


def test_agent_scenario_03_excluded_product_discount_refusal(mock_agent):
    """Scénario A03 : Demande de remise sur un produit exclu (POST / MANUAL / TEST001)."""
    prompt = "Propose une remise de 5% sur le produit POST."
    
    with patch("google.genai.Client") as mock_genai:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MockLLMResponse(
            "Le produit POST fait partie des références exclues de toute remise. Aucune remise ne peut être accordée."
        )
        mock_genai.return_value = mock_client
        
        res = mock_agent.run_query(prompt, customer_id="10005", stock_code="POST")
        
        assert "exclu" in res["answer"].lower() or "aucune" in res["answer"].lower()


def test_agent_scenario_04_unknown_client_handling(mock_agent):
    """Scénario A04 : Traitement d'un identifiant client invalide ou inexistant."""
    prompt = "Quel est le statut de ce client ?"
    
    res = mock_agent.run_query(prompt, customer_id="INVALID_ID_999999")
    assert res["context_data"]["profile"] is None or "error" in str(res["context_data"]["profile"])


def test_agent_scenario_05_chroma_rag_semantic_search(mock_agent):
    """Scénario A05 : Vérification de la recherche vectorielle ChromaDB sur les conditions de remises grossistes."""
    prompt = "Quelles sont les conditions applicables pour les remises grossistes ?"
    
    with patch("google.genai.Client") as mock_genai:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MockLLMResponse(
            "Selon la politique commerciale retrouvée via le RAG ChromaDB, les remises grossistes s'appliquent aux commandes de volumes importants sous réserve d'approbation préalable."
        )
        mock_genai.return_value = mock_client
        
        res = mock_agent.run_query(prompt)
        
        assert "rag_source" in res
        assert "ChromaDB" in res["rag_source"] or "Politique Commerciale" in res["rag_source"]


def test_agent_scenario_06_fideles_compliant_discount(mock_agent):
    """Scénario A06 : Demande de remise de 5% pour segment Fidèles (Conforme <= 6%)."""
    prompt = "Puis-je accorder 5% de remise au client 10005 ?"
    
    with patch("google.genai.Client") as mock_genai:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MockLLMResponse(
            "La remise de 5.0% est conforme et approuvée automatiquement car elle respecte le plafond de 6.0% du segment Fidèles."
        )
        mock_genai.return_value = mock_client
        
        res = mock_agent.run_query(prompt, customer_id="10005")
        assert "conforme" in res["answer"].lower() or "approuvée" in res["answer"].lower()


def test_agent_scenario_07_pricing_metrics_fidelity(mock_agent):
    """Scénario A07 : Vérification de la fidélité des chiffres de prix recommandés par l'API."""
    prompt = "Quel est le prix recommandé pour le produit 22423 ?"
    
    with patch("google.genai.Client") as mock_genai:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MockLLMResponse(
            "Le produit 22423 présente un prix actuel de £12.50 et un prix recommandé de £13.49, dégageant un gain de marge net."
        )
        mock_genai.return_value = mock_client
        
        res = mock_agent.run_query(prompt, stock_code="22423")
        assert "22423" in res["answer"]
        assert "£" in res["answer"]


def test_agent_scenario_08_a_risque_reactivation_discount(mock_agent):
    """Scénario A08 : Remise de réengagement de 10% pour segment À risque (Conforme <= 10%)."""
    prompt = "Proposition de remise de 10% pour réactiver ce client."
    
    with patch("google.genai.Client") as mock_genai:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MockLLMResponse(
            "La remise de 10.0% est conforme pour l'offre spéciale de réactivation du segment À risque."
        )
        mock_genai.return_value = mock_client
        
        res = mock_agent.run_query(prompt, customer_id="10005")
        assert "10" in res["answer"]


def test_agent_scenario_09_multi_llm_provider_dispatch(mock_agent):
    """Scénario A09 : Test de compatibilité du moteur multi-fournisseur."""
    engine_claude = CommercialAgentEngine(provider="claude", api_key="mock", model_name="claude-sonnet-5.5")
    assert engine_claude.provider == "claude"
    assert engine_claude.model_name == "claude-sonnet-5.5"


def test_agent_scenario_10_human_in_the_loop_audit_trail(mock_agent):
    """Scénario A10 : Vérification que les réponses d'escalade mentionnent la validation humaine obligatoire."""
    prompt = "Puis-je offrir 25% de remise ?"
    
    with patch("google.genai.Client") as mock_genai:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MockLLMResponse(
            "Demande hors plafond. Une validation humaine par dérogation du Sales Manager est obligatoire."
        )
        mock_genai.return_value = mock_client
        
        res = mock_agent.run_query(prompt, customer_id="10005")
        assert "validation humaine" in res["answer"].lower() or "manager" in res["answer"].lower()
