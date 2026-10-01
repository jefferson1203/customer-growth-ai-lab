import pandas as pd
import numpy as np
from config import DATA_RAW
from common.data import load_retail


def analyze_price_dispersion(df_clean: pd.DataFrame) -> pd.DataFrame:
    """Analyse la dispersion des prix unitaires pratiqués pour chaque référence.

    Args:
        df_clean (pd.DataFrame): DataFrame propre des transactions.

    Returns:
        pd.DataFrame: Statistiques de dispersion par StockCode.
    """
    df = df_clean[df_clean["Price"] > 0].copy()

    dispersion = df.groupby("StockCode").agg(
        min_price =  ("Price", "min"),
        max_price = ("Price", "max"),
        mean_price = ("Price", "mean"),
        median_price = ("Price", "median"),
        std_price = ("Price", "std"),
    ).reset_index()

    dispersion["price_ratio_max_min"] = (dispersion["max_price"] / dispersion["min_price"]).round(2)
    dispersion["cv_price"] = (dispersion["std_price"] / dispersion["mean_price"]).round(4)

    return dispersion


def analyze_customer_discounts(df_clean: pd.DataFrame) -> dict:
    """Mesure le niveau de remise unitaire implicite accordé aux gros clients (Top 1% CA) vs autres clients.

    Args:
        df_clean (pd.DataFrame): DataFrame des transactions.

    Returns:
        dict: Métriques de comparaison et taux de remise moyen.
    """
    df_cust = df_clean.dropna(subset=["CustomerID"]).copy()

    cust_rev = df_cust.groupby("CustomerID")["Revenue"].sum().sort_values(ascending=False)
    top_1pct_threshold = cust_rev.quantile(0.99)
    top_clients = cust_rev[cust_rev >= top_1pct_threshold].index

    df_cust["is_top_1pct"] = df_cust["CustomerID"].isin(top_clients)

    median_price_top = float(df_cust[df_cust["is_top_1pct"]]["Price"].median())
    median_price_others = float(df_cust[~df_cust["is_top_1pct"]]["Price"].median())

    implicit_discount_pct = 1 - (median_price_top / median_price_others)

    return {
        "nb_top_clients": len(top_clients),
        "median_price_top_clients": round(median_price_top, 2),
        "median_price_other_clients": round(median_price_others, 2),
        "implicit_discount_pct": round(implicit_discount_pct, 4)
    }

def analyze_price_trends(df_clean: pd.DataFrame) -> pd.DataFrame:
    """Mesure l'évolution temporelle du prix unitaire moyen et médian mois par mois.

    Args:
        df_clean (pd.DataFrame): DataFrame des transactions.

    Returns:
        pd.DataFrame: Évolution mensuelle des prix et volumes.
    """
    df = df_clean[df_clean["Price"] > 0].copy()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["YearMonth"] = df["InvoiceDate"].dt.strftime("%Y-%m")

    trends = df.groupby("YearMonth").agg(
        mean_price=("Price", "mean"),
        median_price=("Price", "median"),
        total_revenue=("Revenue", "sum"),
        total_quantity=("Quantity", "sum")
    ).round(2).reset_index()

    return trends


def run_pricing_diagnostic(df_clean: pd.DataFrame) -> dict:
    dispersion_df = analyze_price_dispersion(df_clean)
    discounts = analyze_customer_discounts(df_clean)
    trends_df = analyze_price_trends(df_clean)

    median_ratio = float(dispersion_df["price_ratio_max_min"].median())
    pct_high_dispersion = float((dispersion_df["price_ratio_max_min"] >= 2.0).mean())

    return {
        "total_skus_analyzed": len(dispersion_df),
        "median_price_ratio_max_min": round(median_ratio, 2),
        "pct_skus_high_dispersion": round(pct_high_dispersion, 4),
        "discounts_summary": discounts,
        "monthly_trends": trends_df.to_dict(orient="records")
    }



if __name__ == "__main__":
    df_clean, _ = load_retail(DATA_RAW)
    diag = run_pricing_diagnostic(df_clean)

    print("--- DIAGNOSTIC TARIFAIRE ACTUEL ---")
    print(f"Total SKUs analysés : {diag['total_skus_analyzed']}")
    print(f"Ratio médian Prix Max / Prix Min : {diag['median_price_ratio_max_min']}x")
    print(f"% de SKUs avec écart de prix >= 2x : {diag['pct_skus_high_dispersion'] * 100:.1f}%")
    print(f"Prix unitaire médian Top 1% Grossistes : £{diag['discounts_summary']['median_price_top_clients']}")
    print(f"Prix unitaire médian Autres clients : £{diag['discounts_summary']['median_price_other_clients']}")
    print(f"Remise implicite accordée aux Top 1% : {diag['discounts_summary']['implicit_discount_pct'] * 100:.2f}%")
