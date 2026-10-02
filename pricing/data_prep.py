import pandas as pd

def prepare_weekly_pricing_data(df_clean: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_clean_w = df_clean.copy()

    df_clean_w["YearWeek"] = df_clean_w["InvoiceDate"].dt.strftime("%G-W%V")
    df_clean_w = df_clean_w.groupby(['StockCode', 'YearWeek']).agg(
        Description=("Description", "last"),
        quantity=("Quantity", "sum"),
        revenue=("Revenue", "sum"),
        median_price=("Price", "median"),
        nb_client=("CustomerID", "nunique")
    ).round(2).reset_index()
    

    df_clean_w_filtered = df_clean_w[(df_clean_w["quantity"] > 0) & (df_clean_w["median_price"] > 0)]

    # Calcul du prix moyen récent sur les 12 dernières semaines observées pour chaque SKU
    recent_prices = df_clean_w_filtered.sort_values(by="YearWeek").groupby("StockCode").tail(12).groupby("StockCode")["median_price"].mean().round(2).rename("recent_12w_price")

    df_sku_stat = df_clean_w_filtered.groupby("StockCode").agg(
        nb_weeks=("YearWeek", "count"),
        mean_price=("median_price", "mean"),
        std_price=("median_price", "std"),
        total_qty=("quantity", "sum"),
        total_rev=("revenue", "sum"),
    ).reset_index()

    df_sku_stat = df_sku_stat.merge(recent_prices, on="StockCode", how="left")
    df_sku_stat["recent_12w_price"] = df_sku_stat["recent_12w_price"].round(2)

    df_sku_stat["std_price"] = df_sku_stat["std_price"].fillna(0)
    df_sku_stat["cv_price"] = (df_sku_stat["std_price"] / df_sku_stat["mean_price"]).round(4)
    df_descriptions = df_clean_w_filtered[['StockCode', 'Description']].drop_duplicates(subset=['StockCode'])
    df_sku_stat = df_sku_stat.merge(df_descriptions, on="StockCode", how="left")

    df_sku_stat["is_eligible"] = (
        (df_sku_stat["nb_weeks"] >= config.get("min_weeks", 40)) & 
        (df_sku_stat["cv_price"] >= config.get("min_price_cv", 0.05))
    ).astype(int)

    df_eligible_skus = df_sku_stat[df_sku_stat["is_eligible"] == 1].sort_values(by="total_rev", ascending=False).head(50)

    df_clean_w_eligible = df_clean_w_filtered[df_clean_w_filtered['StockCode'].isin(df_eligible_skus['StockCode'])].copy()

    return df_clean_w_eligible, df_sku_stat

if __name__ == "__main__":
    from config import DATA_RAW, PRICING
    from common.data import load_retail

    df_clean, _ = load_retail(DATA_RAW)
    df_weekly, sku_stats = prepare_weekly_pricing_data(df_clean, PRICING)

    print(f"Total SKUs analysés : {len(sku_stats)}")
    print(f"SKUs éligibles (is_eligible == 1) : {sku_stats['is_eligible'].sum()}")
    print(f"SKUs retenus dans le top 50 : {df_weekly['StockCode'].nunique()}")
    print(f"Nombre de lignes hebdomadaires obtenues : {len(df_weekly)}")
