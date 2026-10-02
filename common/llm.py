"""
common/llm.py - Client LLM Gemini standardisé avec cache unifié, FinOps & retry typé.
"""

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from string import Template
from typing import Dict, Any, Type
import pandas as pd
from pydantic import BaseModel, ValidationError

from google import genai
from google.genai import types
from google.genai.errors import APIError

from config import LLM


def get_prompt_hash(prompt_text: str) -> str:
    """Calcule une empreinte MD5 courte (8 caractères) du contenu d'un prompt."""
    return hashlib.md5(prompt_text.encode("utf-8")).hexdigest()[:8]


class LLMClient:
    """
    Client wrapper pour l'API Gemini (via le SDK google-genai) avec :
    - Format de cache unifié et écriture atomique (compatible str et pathlib.Path)
    - Clé de cache composée (prompt:hash:modèle:cache_key)
    - Retry typé (APIError 429/5xx, ValidationError, JSONDecodeError)
    - Garde-fou FinOps (plafond d'appels max par run ; peut être dépassé de quelques unités en cas de retry)
    """

    def __init__(self, prompt_path: str | Path, cache_path: str | Path):
        self.prompt_path = Path(prompt_path)
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Fichier de prompt introuvable : {self.prompt_path}")

        self.prompt_name = self.prompt_path.stem
        
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            self.prompt_raw = f.read()

        self.prompt_template = Template(self.prompt_raw)
        self.prompt_hash = get_prompt_hash(self.prompt_raw)
        
        self.cache_path = Path(cache_path)
        self.model = LLM["model"]
        self.temperature = LLM["temperature"]
        self.max_retries = LLM["max_retries"]
        self.retry_delay = LLM["delay_seconds"]
        self.max_calls_per_run = LLM["max_calls_per_run"]
        
        self.call_count = 0
        self.cache: Dict[str, Any] = self._load_cache()

        # Initialisation du client SDK Gemini
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            logging.warning("LLM_API_KEY non définie dans l'environnement. Les appels API échoueront s'ils ne sont pas en cache.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

    def _load_cache(self) -> Dict[str, Any]:
        """
        Charge le cache JSON existant.
        Si le fichier existe mais qu'il est illisible ou corrompu, LÈVE une erreur
        pour éviter d'écraser le fichier avec un cache vide.
        """
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logging.critical(f"Fichier de cache corrompu ou illisible ({self.cache_path}): {e}")
                raise
        return {}

    def _save_cache(self) -> None:
        """Écriture atomique du cache via un fichier temporaire .tmp."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.cache_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.cache_path)

    def complete_json(self, variables: Dict[str, Any], cache_key: str, schema: Type[BaseModel]) -> BaseModel:
        """
        Exécute la complétion JSON avec validation Pydantic et gestion du cache.
        Format unifié de la clé de cache : {prompt_name}:{prompt_hash}:{model}:{cache_key}
        """
        composite_key = f"{self.prompt_name}:{self.prompt_hash}:{self.model}:{cache_key}"

        # 1. Vérification dans le cache
        if composite_key in self.cache:
            entry = self.cache[composite_key]
            return schema(**entry["data"])

        # 2. Vérification de la limite FinOps
        if self.call_count >= self.max_calls_per_run:
            raise RuntimeError(f"Plafond d'appels LLM atteint ({self.max_calls_per_run} appels). Arrêt par sécurité FinOps.")

        if not self.client:
            raise ValueError("LLM_API_KEY non configurée pour effectuer de nouveaux appels API.")

        # 3. Préparation du prompt via string.Template (substitute lève KeyError si variable manquante)
        prompt_content = self.prompt_template.substitute(**variables)

        # 4. Boucle de retry avec backoff exponentiel et gestion typée d'exceptions
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                self.call_count += 1
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt_content,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                        temperature=self.temperature
                    )
                )

                if not response.text:
                    raise ValueError(f"Réponse vide du modèle (bloquée par les filtres de sécurité API) pour {cache_key}.")

                raw_json = response.text
                parsed_dict = json.loads(raw_json)
                parsed_obj = schema(**parsed_dict)

                # Stockage dans le format unifié du cache avec item_id générique
                self.cache[composite_key] = {
                    "item_id": cache_key,
                    "prompt": self.prompt_name,
                    "prompt_hash": self.prompt_hash,
                    "model": self.model,
                    "data": parsed_obj.model_dump()
                }
                self._save_cache()
                return parsed_obj

            except Exception as e:
                last_exception = e
                is_retryable = False

                if isinstance(e, (ValidationError, json.JSONDecodeError)):
                    is_retryable = True
                elif isinstance(e, APIError):
                    # Seules les erreurs HTTP 429 et 5xx sont réessayées
                    if hasattr(e, "code") and e.code in [429, 500, 502, 503, 504]:
                        is_retryable = True

                if not is_retryable or attempt == self.max_retries:
                    logging.error(f"Erreur non réessayable ou nombre maximal d'essais atteint ({e}). Échec.")
                    raise

                sleep_time = self.retry_delay * (2 ** (attempt - 1))
                logging.warning(f"Tentative {attempt}/{self.max_retries} échouée pour {cache_key}: {e}. Retry dans {sleep_time}s...")
                time.sleep(sleep_time)

        raise last_exception or RuntimeError("Échec inconnu lors de l'appel LLM.")


def load_labels(cache_path: str | Path, schema: Type[BaseModel]) -> pd.DataFrame:
    """
    Fonction unique de lecture du cache pour l'ensemble des modules du projet.
    Charge le fichier JSON de cache, valide chaque entrée avec la classe Pydantic `schema`
    et retourne un DataFrame structuré. Lève une exception explicite si une entrée est invalide
    ou si des doublons d'item_id sont détectés.
    """
    cache_file = Path(cache_path)
    if not cache_file.exists():
        raise FileNotFoundError(f"Fichier de cache introuvable : {cache_file}")

    with open(cache_file, "r", encoding="utf-8") as f:
        cache_data = json.load(f)

    rows = []
    seen_ids = set()

    for key, entry in cache_data.items():
        if not isinstance(entry, dict) or "data" not in entry:
            raise ValueError(f"Entrée de cache corrompue pour la clé '{key}'.")

        item_id = entry.get("item_id") or entry.get("review_id")
        if not item_id:
            raise ValueError(f"Entrée de cache sans item_id pour la clé '{key}'.")

        if item_id in seen_ids:
            raise ValueError(f"Doublon d'identifiant détecté dans le cache pour item_id '{item_id}'.")
        seen_ids.add(item_id)

        # Validation Pydantic stricte
        validated_obj = schema(**entry["data"])
        obj_dict = validated_obj.model_dump()

        # Métadonnées d'identification
        obj_dict["item_id"] = item_id
        obj_dict["review_id"] = item_id  # Rétrocompatibilité avec les vues VoC
        obj_dict["prompt"] = entry.get("prompt", "")
        obj_dict["model"] = entry.get("model", "")
        rows.append(obj_dict)

    return pd.DataFrame(rows)