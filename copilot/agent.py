"""
copilot/agent.py - Agent commercial multi-fournisseurs (Gemini, Claude, OpenAI/ChatGPT, DeepSeek).
Recherche RAG dans la politique commerciale + appels d'outils REST déterministes.
"""

import os
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from google import genai
from google.genai import types

# Tenter d'importer optionnellement anthropic et openai
try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import openai
except ImportError:
    openai = None


class CommercialAgentEngine:
    """
    Moteur d'agent copilote commercial capable de faire du RAG et d'invoquer les API déterministes.
    Prend en charge : Gemini, Claude (Anthropic), ChatGPT (OpenAI) et DeepSeek.
    """

    def __init__(self, provider: str, api_key: str, api_base_url: str = "http://localhost:8000", model_name: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip("/")
        self.model_name = model_name
        
        # Charger la base de connaissances RAG
        kb_path = Path(__file__).parent / "kb" / "politique_commerciale.md"
        if kb_path.exists():
            with open(kb_path, "r", encoding="utf-8") as f:
                self.kb_content = f.read()
        else:
            self.kb_content = "Politique commerciale indisponible."

    def _call_api_endpoint(self, endpoint: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Appel HTTP helper vers l'API FastAPI déterministe."""
        url = f"{self.api_base_url}{endpoint}"
        headers = {"X-API-Key": "dev-secret-key", "Content-Type": "application/json"}
        try:
            if method == "POST":
                res = requests.post(url, json=payload, headers=headers, timeout=5)
            else:
                res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                return res.json()
            return {"error": f"Erreur API ({res.status_code}): {res.text}"}
        except Exception as e:
            return {"error": f"Impossible de contacter l'API REST ({e})"}

    def run_query(self, user_prompt: str, customer_id: Optional[str] = None, stock_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Traite la requête utilisateur en orchestrant la récupération de données déterministes et RAG.
        """
        # 1. Collecte de données contextuelles déterministes depuis l'API
        context_data = {}
        if customer_id:
            context_data["profile"] = self._call_api_endpoint(f"/clients/{customer_id}")
            context_data["opportunities"] = self._call_api_endpoint(f"/clients/{customer_id}/opportunites")
        if stock_code:
            context_data["product"] = self._call_api_endpoint(f"/produits/{stock_code}/prix")
        
        context_data["policy"] = self._call_api_endpoint("/politique-commerciale")

        system_instruction = (
            "Tu es un Copilote Commercial Expert et Conseiller Stratégique (Technical Mentor Style).\n"
            "Tu réponds de manière professionnelle, précise et directe en Français.\n"
            "Chiffres financiers impérativement en Livre Sterling (£).\n\n"
            "--- BASE DE CONNAISSANCES DE LA POLITIQUE COMMERCIALES (RAG) ---\n"
            f"{self.kb_content}\n\n"
            "--- DONNÉES DÉTERMINISTES EN TEMPS RÉEL DE L'API REST ---\n"
            f"{context_data}\n\n"
            "CONSIGNES :\n"
            "1. Base tes décisions tarifaires et recommandations STRICTEMENT sur les données fournies ci-dessus.\n"
            "2. Si l'utilisateur demande une remise, vérifie le plafond autorisé pour le segment client.\n"
            "3. Si la remise dépasse le plafond ou touche un produit exclu, indique clairement qu'une escalade/validation humaine est requise."
        )

        # 2. Dispatching selon le LLM Provider choisi
        if "gemini" in self.provider:
            return self._run_gemini(system_instruction, user_prompt)
        elif "claude" in self.provider or "anthropic" in self.provider:
            return self._run_claude(system_instruction, user_prompt)
        elif "chatgpt" in self.provider or "openai" in self.provider:
            return self._run_openai(system_instruction, user_prompt, base_url=None)
        elif "deepseek" in self.provider:
            return self._run_openai(system_instruction, user_prompt, base_url="https://api.deepseek.com")
        else:
            return {
                "answer": f"Fournisseur LLM '{self.provider}' non supporté.",
                "context": context_data
            }

    def _run_gemini(self, system_instruction: str, user_prompt: str) -> Dict[str, Any]:
        """Exécution via SDK Gemini (google-genai)."""
        try:
            client = genai.Client(api_key=self.api_key)
            prompt = f"{system_instruction}\n\nQuestion de l'utilisateur : {user_prompt}"
            target_model = self.model_name or "gemini-3.8-flash"
            res = client.models.generate_content(
                model=target_model,
                contents=prompt
            )
            return {"answer": res.text, "status": "success"}
        except Exception as e:
            return {"answer": f"Erreur lors de l'appel Gemini ({target_model}) : {e}", "status": "error"}

    def _run_claude(self, system_instruction: str, user_prompt: str) -> Dict[str, Any]:
        """Exécution via SDK Anthropic Claude."""
        if not anthropic:
            return {"answer": "Le package 'anthropic' n'est pas installé dans le virtuel environment.", "status": "error"}
        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            target_model = self.model_name or "claude-3-5-sonnet-20241022"
            res = client.messages.create(
                model=target_model,
                max_tokens=1024,
                system=system_instruction,
                messages=[{"role": "user", "content": user_prompt}]
            )
            answer = res.content[0].text if res.content else ""
            return {"answer": answer, "status": "success"}
        except Exception as e:
            return {"answer": f"Erreur lors de l'appel Claude Anthropic ({target_model}) : {e}", "status": "error"}

    def _run_openai(self, system_instruction: str, user_prompt: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Exécution via SDK OpenAI (utilisé pour ChatGPT et DeepSeek)."""
        if not openai:
            return {"answer": "Le package 'openai' n'est pas installé dans le virtuel environment.", "status": "error"}
        try:
            client = openai.OpenAI(api_key=self.api_key, base_url=base_url)
            target_model = self.model_name or ("deepseek-chat" if base_url else "gpt-4o-mini")
            res = client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ]
            )
            answer = res.choices[0].message.content or ""
            return {"answer": answer, "status": "success"}
        except Exception as e:
            return {"answer": f"Erreur lors de l'appel API OpenAI/DeepSeek ({target_model}) : {e}", "status": "error"}
