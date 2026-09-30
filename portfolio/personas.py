import time
import pandas as pd
from pathlib import Path
from pydantic import BaseModel, Field
from common.llm import LLMClient
from config import PROMPTS, LLM


class SegmentPersona(BaseModel):
    persona_name: str = Field(..., description="Nom du persona (ex: Le Grossiste Fidèle)")
    description: str = Field(..., description="Description courte du profil (2-3 phrases max)")
    next_best_action: str = Field(..., description="Action marketing recommandée (1 phrase max)")
    canal: str = Field(..., description="Canal de communication privilégié (email, sms, pub, etc.)")
    kpi: str = Field(..., description="Indicateur clé de succès pour mesurer l'impact de l'action")


def generate_persona_for_segment(segment_stats: dict, client: LLMClient) -> SegmentPersona:
    variables = {
        "segment": str(segment_stats["segment"]),
        "nb_clients": str(segment_stats["nb_clients"]),
        "pct_clients": str(segment_stats["pct_clients"]),
        "ca_total": str(segment_stats["ca_total"]),
        "pct_ca": str(segment_stats["pct_ca"]),
        "panier_moyen": str(segment_stats["panier_moyen"]),
        "recence_moyenne": str(segment_stats["recence_moyenne"]),
        "frequence_moyenne": str(segment_stats["frequence_moyenne"]),
    }
    
    cache_key = str(segment_stats["segment"])
    return client.complete_json(variables=variables, cache_key=cache_key, schema=SegmentPersona)


def generate_all_personas(summary_df: pd.DataFrame, cache_path: Path) -> dict[str, SegmentPersona]:
   
    prompt_path = PROMPTS / "portfolio_persona.txt"
    client = LLMClient(prompt_path=prompt_path, cache_path=cache_path)
    
    result = {}
    for _, row in summary_df.iterrows():
        segment_stats = row.to_dict()
        result[segment_stats["segment"]] = generate_persona_for_segment(segment_stats, client)
        time.sleep(LLM.get("delay_seconds", 1))
    return result

def build_next_best_action_table(personas:dict[str,SegmentPersona], summary_df:pd.DataFrame) -> pd.DataFrame:

    df = summary_df.copy()

    for segment_name, persona in personas.items():
        mask = df["segment"] == segment_name
        
        df.loc[mask, "persona_name"] = persona.persona_name
        df.loc[mask, "description"] = persona.description
        df.loc[mask, "next_best_action"] = persona.next_best_action
        df.loc[mask, "canal"] = persona.canal
        df.loc[mask, "kpi"] = persona.kpi
    return df
    