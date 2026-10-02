import re
import hashlib
import json
import pandas as pd
import numpy as np
from pathlib import Path
from pydantic import BaseModel, Field

from config import PROMPTS, DATA_RAW, PRICING, OUTPUTS
from common.llm import LLMClient


class PricingJustificationSchema(BaseModel):
    justification: str = Field(description="Explicitation commerciale en 3 phrases.")


def extract_numbers(text: str) -> list[float]:
    """Extrait tous les nombres (décimaux ou entiers) présents dans un texte.

    Args:
        text (str): Texte à analyser.

    Returns:
        list[float]: Liste des valeurs numériques obtenues.
    """
    pattern = r"[-+]?\d+(?:[\.,]\d+)?"
    matches = re.findall(pattern, text)
    
    numbers = []
    for match in matches:
        try:
            val = float(match.replace(",", "."))
            numbers.append(val)
        except ValueError:
            continue
            
    return numbers


def verify_justification_numbers(text: str, allowed_values: list[float], tolerance: float = 0.05) -> tuple[bool, list[float]]:
    """Vérifie si tous les nombres extraits du texte figurent dans la liste des valeurs autorisées.

    Args:
        text (str): Justification texte générée par le LLM.
        allowed_values (list[float]): Liste des nombres autorisés issus des données de la recommandation.
        tolerance (float): Écart toléré pour la comparaison (ex: 0.05).

    Returns:
        tuple[bool, list[float]]: (est_valide, liste_nombres_non_autorises)
    """
    extracted = extract_numbers(text)
    unverified = []

    for num in extracted:
        match_found = any(abs(num - allowed) <= tolerance for allowed in allowed_values if allowed is not None)
        if not match_found:
            unverified.append(num)

    is_valid = (len(unverified) == 0)
    return is_valid, unverified


def generate_fallback_justification(row: dict) -> str:
    """Génère une justification standard sans LLM en cas d'hallucination ou d'erreur API.

    Args:
        row (dict): Données de la recommandation.

    Returns:
        str: Texte de repli en 3 phrases.
    """
    rec_price = float(row["rec_price"])
    change_pct = round(float(row["price_change_pct"]) * 100, 1)
    eps = float(row["elasticity"])
    margin_gain = float(row["margin_gain_gbp"])
    cat = str(row["category"])

    phrase1 = f"Nous recommandons un prix ajusté à {rec_price:.2f} £ (variation de {change_pct:+.1f} %)."
    phrase2 = f"Cette décision repose sur une élasticité mesurée à {eps:.2f} (catégorie {cat}) visant un gain de marge de {margin_gain:.2f} £."
    phrase3 = "Le risque principal réside dans la réaction des clients ou l'arbitrage avec les volumes grossistes."

    return f"{phrase1} {phrase2} {phrase3}"


def generate_pricing_justifications(
    df_recommendations: pd.DataFrame,
    client: LLMClient = None
) -> tuple[pd.DataFrame, dict]:
    """Génère et contrôle automatiquement les justifications LLM pour chaque recommandation de prix via LLMClient.

    Args:
        df_recommendations (pd.DataFrame): DataFrame des recommandations (issue de optimize_sku_prices).
        client (LLMClient, optional): Client LLM initialisé.

    Returns:
        tuple[pd.DataFrame, dict]: (df_avec_justifications, métriques_controle)
    """
    if client is None:
        prompt_path = PROMPTS / "pricing_justification.txt"
        cache_path = OUTPUTS / "pricing" / "justifications_cache.json"
        client = LLMClient(prompt_path=prompt_path, cache_path=cache_path)

    df_res = df_recommendations.copy()

    justifications = []
    statuses = []
    first_try_successes = 0
    api_errors = 0
    regex_rejections = 0

    for idx, row in df_res.iterrows():
        stock_code = str(row["StockCode"])
        current_price = float(row["current_price"])
        rec_price = float(row["rec_price"])
        price_change_pct = round(float(row["price_change_pct"]) * 100, 2)
        elasticity = float(row["elasticity"])
        margin_gain_gbp = float(row["margin_gain_gbp"])
        description = str(row["Description"])
        category = str(row["category"])

        # Liste complète des représentations numériques autorisées (brutes, arrondies, entières, pourcentage)
        allowed_values = [
            current_price, round(current_price, 1), round(current_price, 0), int(np.round(current_price)),
            rec_price, round(rec_price, 1), round(rec_price, 0), int(np.round(rec_price)),
            price_change_pct, abs(price_change_pct), round(price_change_pct, 1), round(abs(price_change_pct), 1), int(np.round(abs(price_change_pct))),
            elasticity, abs(elasticity), round(elasticity, 1), round(abs(elasticity), 1),
            margin_gain_gbp, abs(margin_gain_gbp), round(margin_gain_gbp, 1), round(margin_gain_gbp, 0), int(np.round(abs(margin_gain_gbp)))
        ]

        variables = {
            "description": description,
            "stock_code": stock_code,
            "current_price": f"{current_price:.2f}",
            "rec_price": f"{rec_price:.2f}",
            "price_change_pct": f"{price_change_pct:+.2f}",
            "elasticity": f"{elasticity:.2f}",
            "category": category,
            "margin_gain_gbp": f"{margin_gain_gbp:.2f}"
        }

        # La cache_key intègre le hash des variables pour s'invalider dès qu'un prix change
        var_hash = hashlib.md5(json.dumps(variables, sort_keys=True).encode("utf-8")).hexdigest()[:8]
        cache_key = f"{stock_code}_{var_hash}"

        try:
            res_obj = client.complete_json(variables=variables, cache_key=cache_key, schema=PricingJustificationSchema)
            text = res_obj.justification.strip()
            api_success = True
        except Exception:
            text = generate_fallback_justification(row.to_dict())
            api_success = False

        if not api_success:
            justifications.append(text)
            statuses.append("Erreur API (Fallback Modèle)")
            api_errors += 1
        else:
            is_valid, unverified = verify_justification_numbers(text, allowed_values)

            if is_valid:
                justifications.append(text)
                statuses.append("Validé (1er essai)")
                first_try_successes += 1
            else:
                fallback_text = generate_fallback_justification(row.to_dict())
                justifications.append(fallback_text)
                statuses.append("Rejeté (Hallucination Regex)")
                regex_rejections += 1

    df_res["llm_justification"] = justifications
    df_res["control_status"] = statuses

    total_count = len(df_res)
    first_try_rate = (first_try_successes / total_count) if total_count > 0 else 0.0

    control_metrics = {
        "total_recommendations": total_count,
        "first_try_successes": first_try_successes,
        "regex_rejections": regex_rejections,
        "api_errors": api_errors,
        "first_try_acceptance_rate": round(first_try_rate, 4),
        "status_breakdown": pd.Series(statuses).value_counts().to_dict()
    }

    return df_res, control_metrics


if __name__ == "__main__":
    from common.data import load_retail
    from pricing.data_prep import prepare_weekly_pricing_data
    from pricing.elasticity import compute_sku_elasticity
    from pricing.optimization import optimize_sku_prices

    print("⏳ Test du module LLM Justification et Contrôle Anti-Hallucination...")
    df_clean, _ = load_retail(DATA_RAW)
    df_weekly, sku_stats = prepare_weekly_pricing_data(df_clean, PRICING)
    df_elasticity = compute_sku_elasticity(df_weekly, sku_stats)
    df_opt = optimize_sku_prices(df_elasticity, PRICING, cost_ratio=0.50).head(15)

    df_justified, metrics = generate_pricing_justifications(df_opt)

    print("\n--- MÉTRIQUES DU CONTRÔLE ANTI-HALLUCINATION ---")
    print(f"Total Recommandations : {metrics['total_recommendations']}")
    print(f"Validés (1er essai) : {metrics['first_try_successes']}")
    print(f"Rejetés (Regex) : {metrics['regex_rejections']}")
    print(f"Erreurs API : {metrics['api_errors']}")
    print(f"Taux d'acceptation au 1er essai : {metrics['first_try_acceptance_rate'] * 100:.1f} %")
    print("\n--- APERÇU DES JUSTIFICATIONS GÉNÉRÉES ---")
    for idx, row in df_justified.iterrows():
        print(f"\nSKU : {row['StockCode']} | Statut : {row['control_status']}")
        print(f"Justification : {row['llm_justification']}")