import pandas as pd
import numpy as np
import statsmodels.api as sm
from config import DATA_RAW, PRICING
from common.data import load_retail
from pricing.data_prep import prepare_weekly_pricing_data


def fit_log_log_ols(group_df: pd.DataFrame) -> dict:
    """Ajuste une régression Log-Log OLS avec effets fixes du mois sur un groupe de ventes hebdomadaires.

    Modèle : ln(quantity) = alpha + elasticity * ln(median_price) + sum(gamma_m * Month_m) + e

    Args:
        group_df (pd.DataFrame): Données hebdomadaires d'un SKU.

    Returns:
        dict: Coefficient d'élasticité, p-value, R², intervalle de confiance à 95% [ci_low, ci_high].
    """
    if len(group_df) < 8 or group_df["median_price"].nunique() <= 1:
        return None

    df = group_df.copy()
    df["log_q"] = np.log(df["quantity"])
    df["log_p"] = np.log(df["median_price"])

    df["Month"] = pd.to_datetime(df["YearWeek"] + "-1", format="%G-W%V-%u", errors="coerce").dt.month.astype(str)

    X = pd.DataFrame({"log_p": df["log_p"]})

    if df["Month"].nunique() > 1:
        month_dummies = pd.get_dummies(df["Month"], prefix="month", drop_first=True, dtype=float)
        X = pd.concat([X, month_dummies], axis=1)

    X = sm.add_constant(X)
    y = df["log_q"]

    try:
        model = sm.OLS(y, X).fit()
        
        elasticity = float(model.params["log_p"])
        p_val = float(model.pvalues["log_p"])
        r2 = float(model.rsquared)
        conf = model.conf_int().loc["log_p"]
        ci_low, ci_high = float(conf[0]), float(conf[1])

        return {
            "elasticity": round(elasticity, 4),
            "p_value": round(p_val, 6),
            "r2": round(r2, 4),
            "ci_low": round(ci_low, 4),
            "ci_high": round(ci_high, 4),
            "n_obs": len(df)
        }
    except Exception:
        return None


def compute_sku_elasticity(df_weekly_filtered: pd.DataFrame, sku_stats: pd.DataFrame) -> pd.DataFrame:
    """Calcule l'élasticité-prix globale et sur petites quantités pour chaque SKU éligible.

    Args:
        df_weekly_filtered (pd.DataFrame): Transactions hebdomadaires filtrées.
        sku_stats (pd.DataFrame): Statistiques d'éligibilité par SKU.

    Returns:
        pd.DataFrame: Table synthétique des élasticités par SKU avec classification métier.
    """
    results = []

    for stock_code, group in df_weekly_filtered.groupby("StockCode"):
        ols_global = fit_log_log_ols(group)
        if ols_global is None:
            continue

        # 2. Estimation sur les petites quantités (sous la médiane) pour tester le biais grossistes
        median_qty = group["quantity"].median()
        group_small = group[group["quantity"] <= median_qty]
        ols_small = fit_log_log_ols(group_small)

        elasticity_small = ols_small["elasticity"] if ols_small is not None else None

        eps = ols_global["elasticity"]
        p_val = ols_global["p_value"]

        if p_val < 0.10:
            if eps < -1.0:
                category = "Élastique"
            elif -1.0 <= eps < 0.0:
                category = "Inélastique"
            else:
                category = "Atypique (Positive)"
        else:
            category = "Non significatif"

        results.append({
            "StockCode": stock_code,
            "elasticity": eps,
            "elasticity_small_qty": elasticity_small,
            "r2": ols_global["r2"],
            "p_value": p_val,
            "ci_low": ols_global["ci_low"],
            "ci_high": ols_global["ci_high"],
            "n_obs": ols_global["n_obs"],
            "category": category
        })

    df_elasticity = pd.DataFrame(results)

    # Fusion avec les métriques et libellés du SKU
    df_merged = pd.merge(
        sku_stats,
        df_elasticity,
        on="StockCode",
        how="inner"
    )

    return df_merged


if __name__ == "__main__":
    df_clean, _ = load_retail(DATA_RAW)
    df_weekly, sku_stats = prepare_weekly_pricing_data(df_clean, PRICING)
    df_elasticity = compute_sku_elasticity(df_weekly, sku_stats)

    print(f"Total SKUs modélisés : {len(df_elasticity)}")
    print("\n--- RÉPARTITION PAR CATÉGORIE D'ÉLASTICITÉ ---")
    print(df_elasticity["category"].value_counts())
    print("\n--- APERÇU DES RÉSULTATS ---")
    print(df_elasticity[["StockCode", "Description", "elasticity", "elasticity_small_qty", "r2", "p_value", "category"]].head(10))
