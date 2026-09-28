from pydantic import json_schema
from pydantic import json_schema
import httpx
from typing import Literal
from pydantic import BaseModel, Field
import json
from config import OUTPUTS, PROMPTS, LLM
from pathlib import Path
import os
from google import genai
from google.genai import types



class ReviewLabel(BaseModel):
    irritants: list[str] = Field(description="Liste des codes d'irritants détectés (ex: LIV_RETARD, SAV, POSITIF...)")
    sentiment: Literal["positif", "negatif", "neutre"]
    urgence: Literal["haute", "moyenne", "basse"]
    resume_fr: str = Field(description="Résumé court de l'avis en français (1 à 2 phrases max)")

    

class LLMClient:
    def __init__(self, OUTPUTS: Path):
        
        cache_path = OUTPUTS / "voc" / "classifications.jsonl"
        if cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                self.cache = json.load(f)
        else:
            self.cache = {}
        
        self.client = genai.Client(api_key=os.getenv("LLM_API_KEY"))
        

    def complete_json(self, prompt_name: str, variables: dict, schema: type[BaseModel],
                      cache_key: str) -> BaseModel:
        """Charge le prompt depuis prompts/, appelle le LLM, valide la réponse
        contre le schéma Pydantic, réessaie si besoin, met en cache le résultat."""

        prompt_path = PROMPTS / f"{prompt_name}.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
        
        if cache_key in self.cache:
            return schema(**self.cache[cache_key])
        else:
            response = self.client.models.generate_content(
                model=LLM["model"],
                contents=prompt_template.format(**variables),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=LLM["temperature"],
                )
            )
            parsed = schema.model_validate_json(response.text)
            self.cache[cache_key] = parsed.model_dump()
            self.save_cache()
            return parsed

        
    
    def save_cache(self):
        cache_path = OUTPUTS / "voc" / "classifications.jsonl"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)