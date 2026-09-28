from pydantic import BaseModel

class LLMClient:
    def complete_json(self, prompt_name: str, variables: dict, schema: type[BaseModel],
                      cache_key: str) -> BaseModel:
        """Charge le prompt depuis prompts/, appelle le LLM, valide la réponse
        contre le schéma Pydantic, réessaie si besoin, met en cache le résultat."""