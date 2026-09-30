import pandas as pd
import numpy as np
from config import BUSINESS_CASE


def compute_business_case_a(df_rfm: pd.DataFrame, config: dict = BUSINESS_CASE) -> dict:
    df_at_risk = df_rfm[df_rfm["segment"] == "À risque"].copy()
    
    nb_client = df_at_risk["CustomerID"].nunique()
    n_control = int(round(nb_client * config["control_group_pct"]))
    n_treatment = nb_client - n_control

    cost = float(round(n_treatment * config["contact_cost_eur"], 2))
    panier_moyen = float(round(df_at_risk["Monetary"].mean(), 2))
    
    n_responder = n_treatment * config["response_rate"]
    gross_margin = float(round(n_responder * panier_moyen * config["margin_rate"], 2))
    net_margin = float(round(gross_margin - cost, 2))

    break_event_rate = float(round(config["contact_cost_eur"] / (panier_moyen * config["margin_rate"]), 4))
    roi = float(round((net_margin / cost) * 100, 1)) if cost > 0 else 0.0

    return {
        "nb_client": nb_client,
        "n_control": n_control,
        "n_treatment": n_treatment,
        "cost": cost,
        "panier_moyen": panier_moyen,
        "n_responder": round(n_responder, 1),
        "gross_margin": gross_margin,
        "net_margin": net_margin,
        "break_event_rate": break_event_rate,
        "roi_pct": roi,
    }


def compute_business_case_b(df_candidates: pd.DataFrame, config: dict = BUSINESS_CASE) -> dict:
    nb_candidates = len(df_candidates)
    ca_at_risk = float(round(df_candidates["ca_total"].sum(), 2))
    
    lost_margin = float(round(ca_at_risk * (1 - config["transfer_rate"]) * config["margin_rate"], 2))
    saving = float(round(nb_candidates * config["cost_per_sku_eur"], 2))
    net_gain = float(round(saving - lost_margin, 2))

    return {
        "nb_candidates": nb_candidates,
        "ca_at_risk": ca_at_risk,
        "lost_margin": lost_margin,
        "saving": saving,
        "net_gain": net_gain
    }


def compute_sensitivity_tables(
    df_rfm: pd.DataFrame, 
    df_candidates: pd.DataFrame, 
    config: dict = BUSINESS_CASE
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_at_risk = df_rfm[df_rfm["segment"] == "À risque"]
    n_treatment = len(df_at_risk) * (1 - config["control_group_pct"])
    panier_moyen = df_at_risk["Monetary"].mean()
    cost_a = n_treatment * config["contact_cost_eur"]

    # Table Sensibilité Case A : Response Rate vs Margin Rate
    response_rates = [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15]
    margin_rates = [0.20, 0.25, 0.30, 0.35, 0.40, 0.50]
    
    sens_a = pd.DataFrame(index=[f"{r*100:.0f}%" for r in response_rates], columns=[f"{m*100:.0f}%" for m in margin_rates])
    for r in response_rates:
        for m in margin_rates:
            gain = (n_treatment * r * panier_moyen * m) - cost_a
            sens_a.loc[f"{r*100:.0f}%", f"{m*100:.0f}%"] = float(round(gain, 2))

    # Table Sensibilité Case B : Transfer Rate vs Cost per SKU
    transfer_rates = [0.10, 0.30, 0.50, 0.70, 0.90]
    sku_costs = [100, 300, 500, 750, 1000]
    ca_at_risk = df_candidates["ca_total"].sum()
    nb_candidates = len(df_candidates)
    
    sens_b = pd.DataFrame(index=[f"{t*100:.0f}%" for t in transfer_rates], columns=[f"{c} €" for c in sku_costs])
    for t in transfer_rates:
        for c in sku_costs:
            gain = (nb_candidates * c) - (ca_at_risk * (1 - t) * config["margin_rate"])
            sens_b.loc[f"{t*100:.0f}%", f"{c} €"] = float(round(gain, 2))

    return sens_a, sens_b
