from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parent
DATA_RAW = ROOT / "data" / "raw"
OUTPUTS = ROOT / "outputs"
PROMPTS = ROOT / "prompts"

LLM = {
    "model": os.getenv("LLM_MODEL"),   # [choix] modèle rapide et peu coûteux suffit
    "temperature": 0,                  # [choix] résultats reproductibles pour de la classification
    "max_retries": 2,                  # [choix]
    "delay_seconds": 0.5,              # [choix] respect des limites de l'API
    "max_calls_per_run": 2000,         # [choix] plafond de sécurité sur le coût
}

VOC = {
    "sample_per_score": 300,           # [choix] 5 notes × 300 = 1 500 avis
    "manual_labels": 100,              # [choix] taille de l'échantillon de validation
    "detractor_max_score": 3,          # [choix] convention du NPS proxy sur une note de 1 à 5
    "seed": 42,                        # [choix]
}

PORTFOLIO = {
    "rfm_bins": 5,                     # [standard] quintiles
    "abc_thresholds": (0.80, 0.95),    # [standard] seuils Pareto usuels
    "kmeans_k": (4, 5, 6),             # [choix]
    "top_clients_pct": 0.01,           # [choix] définition des très gros clients
}

BUSINESS_CASE = {
    "contact_cost_eur": 2.0,           # [illustratif]
    "response_rate": 0.08,             # [illustratif]
    "margin_rate": 0.35,               # [illustratif]
    "control_group_pct": 0.10,         # [choix]
    "transfer_rate": 0.50,             # [illustratif] report des achats après suppression d'une référence
    "cost_per_sku_eur": 500,           # [illustratif] coût annuel de complexité par référence
}

PRICING = {
    "min_weeks": 40,                   # [choix]
    "min_price_cv": 0.05,              # [choix]
    "max_change": 0.10,                # [choix] garde-fou ±10 %
    "min_markup": 1.2,                 # [choix]
    "cost_ratio": 0.50,                # [illustratif] coût = 50 % du prix médian
    "cost_ratio_grid": (0.40, 0.50, 0.60),  # [choix] sensibilité
}