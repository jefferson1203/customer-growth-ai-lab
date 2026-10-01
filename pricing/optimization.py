import pandas as pd
import numpy as np
from config import DATA_RAW, PRICING
from common.data import load_retail
from pricing.data_prep import prepare_weekly_pricing_data
from pricing.elasticity import compute_sku_elasticity


def round_psychological_price(price: float) -> float:
    """Arrondit un prix au niveau psychologique le plus proche (,49 ou ,99).

    Args:
        price (float): Prix brut calculé.

    Returns:
        float: Prix arrondi à ,49 ou ,99.
    """
    if price <= 0:
        return price
    
    integer_part = np.floor(price)
    decimal_part = price - integer_part

    if decimal_part < 0.74:
        return float(integer_part + 0.49)
    else:
        return float(integer_part + 0.99)


def optimize_sku_prices(
    df_elasticity: pd.DataFrame,
    config: dict = PRICING,
    cost_ratio: float = None
) -> pd.DataFrame:
    """Optimise les prix par SKU avec garde-fous métier (±10% max, markup >= 1.2, arrondi psychologique).

    Args:
        df_elasticity (pd.DataFrame): Données d'élasticités par SKU.
        config (dict): Paramètres PRICING.
        cost_ratio (float, optional): Ratio de coût unitaire (par défaut 0.50).

    Returns:
        pd.DataFrame: Table d'optimisation avec prix recommandés et gains chiffrés.
    """
    if cost_ratio is None:
        cost_ratio = config.get("cost_ratio", 0.50)

    max_change = config.get("max_change", 0.10)
    min_markup = config.get("min_markup", 1.2)

    df_opt = df_elasticity.copy()

    df_opt["current_price"] = df_opt["mean_price"]
    df_opt["unit_cost"] = df_opt["current_price"] * cost_ratio
    df_opt["current_quantity"] = df_opt["total_qty"]
    df_opt["current_revenue"] = df_opt["current_price"] * df_opt["current_quantity"]
    df_opt["current_margin"] = (df_opt["current_price"] - df_opt["unit_cost"]) * df_opt["current_quantity"]

    rec_prices = []
    rec_quantities = []
    rec_revenues = []
    rec_margins = []
    opt_reasons = []

    for idx, row in df_opt.iterrows():
        p_curr = row["current_price"]
        cost = row["unit_cost"]
        eps = row["elasticity"]
        cat = row["category"]
        q_curr = row["current_quantity"]

        # Bornes de prix opérationnelles (Garde-fous)
        p_min = p_curr * (1.0 - max_change)
        p_max = p_curr * (1.0 + max_change)
        p_floor = cost * min_markup

        lower_bound = max(p_min, p_floor)
        upper_bound = p_max

        if cat == "Élastique" and eps < -1.0:
            p_star = (eps / (1.0 + eps)) * cost
            p_rec_raw = float(np.clip(p_star, lower_bound, upper_bound))
            p_rec = round_psychological_price(p_rec_raw)
            reason = "Optimisation Marge (Élastique)"
        elif cat == "Inélastique":
            p_rec_raw = upper_bound
            p_rec = round_psychological_price(p_rec_raw)
            reason = "Ajustement Hausse (Inélastique)"
        else:
            p_rec = p_curr
            reason = "Maintien (Non Significatif / Atypique)"

        if p_rec == p_curr or q_curr == 0:
            q_rec = q_curr
        else:
            q_rec = q_curr * ((p_rec / p_curr) ** eps)

        q_rec = float(np.maximum(q_rec, 0))
        r_rec = p_rec * q_rec
        m_rec = (p_rec - cost) * q_rec

        rec_prices.append(round(p_rec, 2))
        rec_quantities.append(round(q_rec, 2))
        rec_revenues.append(round(r_rec, 2))
        rec_margins.append(round(m_rec, 2))
        opt_reasons.append(reason)

    df_opt["rec_price"] = rec_prices
    df_opt["price_change_pct"] = ((df_opt["rec_price"] - df_opt["current_price"]) / df_opt["current_price"]).round(4)
    df_opt["rec_quantity"] = rec_quantities
    df_opt["rec_revenue"] = rec_revenues
    df_opt["rec_margin"] = rec_margins
    df_opt["opt_reason"] = opt_reasons

    # Gains financiers
    df_opt["margin_gain_gbp"] = (df_opt["rec_margin"] - df_opt["current_margin"]).round(2)
    df_opt["revenue_gain_gbp"] = (df_opt["rec_revenue"] - df_opt["current_revenue"]).round(2)

    return df_opt


def run_sensitivity_analysis(df_elasticity: pd.DataFrame, config: dict = PRICING) -> dict:
    """Exécute l'analyse de sensibilité sur la grille de ratios de coût (40%, 50%, 60%).

    Args:
        df_elasticity (pd.DataFrame): Table des élasticités.
        config (dict): Configuration PRICING.

    Returns:
        dict: Synthèse des gains par ratio de coût.
    """
    grid = config.get("cost_ratio_grid", (0.40, 0.50, 0.60))
    sensitivity_results = {}

    for cr in grid:
        df_opt = optimize_sku_prices(df_elasticity, config, cost_ratio=cr)
        
        tot_curr_margin = float(df_opt["current_margin"].sum())
        tot_rec_margin = float(df_opt["rec_margin"].sum())
        tot_margin_gain = float(df_opt["margin_gain_gbp"].sum())
        gain_pct = (tot_margin_gain / tot_curr_margin) if tot_curr_margin > 0 else 0.0

        sensitivity_results[f"cost_ratio_{int(cr*100)}"] = {
            "cost_ratio": cr,
            "cost_ratio_pct": f"{int(cr*100)}%",
            "current_margin_gbp": round(tot_curr_margin, 2),
            "rec_margin_gbp": round(tot_rec_margin, 2),
            "margin_gain_gbp": round(tot_margin_gain, 2),
            "margin_gain_pct": round(gain_pct, 4)
        }

    return sensitivity_results


if __name__ == "__main__":
    df_clean, _ = load_retail(DATA_RAW)
    df_weekly, sku_stats = prepare_weekly_pricing_data(df_clean, PRICING)
    df_elasticity = compute_sku_elasticity(df_weekly, sku_stats)
    df_opt = optimize_sku_prices(df_elasticity, PRICING, cost_ratio=0.50)
    sensitivity = run_sensitivity_analysis(df_elasticity, PRICING)

    print("--- RÉSULTATS DE L'OPTIMISATION DU PRICING ---")
    print(f"Marge Baseline Total : £{df_opt['current_margin'].sum():,.2f}")
    print(f"Marge Optimisée Total : £{df_opt['rec_margin'].sum():,.2f}")
    print(f"Gain de Marge Potentiel : £{df_opt['margin_gain_gbp'].sum():,.2f} ({df_opt['margin_gain_gbp'].sum()/df_opt['current_margin'].sum()*100:.2f}%)")
    print("\n--- ANALYSE DE SENSIBILITÉ (COÛTS 40%, 50%, 60%) ---")
    for k, v in sensitivity.items():
        print(f"Coût {v['cost_ratio_pct']} -> Marge Baseline: £{v['current_margin_gbp']:,.2f} | Gain: £{v['margin_gain_gbp']:,.2f} (+{v['margin_gain_pct']*100:.2f}%)")
