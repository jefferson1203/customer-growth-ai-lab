import pandas as pd

def compute_abc_analysis(df_clean: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df_prod = df_clean.groupby("StockCode").agg(
        Description=("Description", "last"),
        ca_total=("Revenue", "sum"),
        quantite_totale=("Quantity", "sum"),
        nb_commandes=("Invoice", "nunique")
    ).reset_index()

    df_prod = df_prod.sort_values(by="ca_total", ascending=False).reset_index(drop=True)
    
    total_ca = df_prod["ca_total"].sum()
    df_prod["pct_ca"] = df_prod["ca_total"] / total_ca
    df_prod["cum_pct_ca"] = df_prod["pct_ca"].cumsum()
    
    df_prod["categorie_abc"] = df_prod["cum_pct_ca"].apply(
        lambda x: "A" if x <= 0.80 else "B" if x <= 0.95 else "C"
    )

    summary = df_prod.groupby("categorie_abc").agg(
        nb_references=("StockCode", "count"),
        ca_total=("ca_total", "sum")
    ).reset_index()
    
    summary["pct_references"] = (summary["nb_references"] / len(df_prod) * 100).round(1)
    summary["pct_ca"] = (summary["ca_total"] / total_ca * 100).round(1)

    return df_prod, summary.to_dict(orient="records")


def identify_deletion_candidates(
    df_clean: pd.DataFrame, 
    df_rfm: pd.DataFrame, 
    df_abc: pd.DataFrame
) -> pd.DataFrame:
    df_c = df_abc[df_abc["categorie_abc"] == "C"].copy()
    
    cutoff_date = pd.to_datetime("2010-12-01")
    df_clean_p1 = df_clean[df_clean["InvoiceDate"] < cutoff_date]
    df_clean_p2 = df_clean[df_clean["InvoiceDate"] >= cutoff_date]

    ca_p1 = df_clean_p1.groupby("StockCode")["Revenue"].sum().rename("ca_p1")
    ca_p2 = df_clean_p2.groupby("StockCode")["Revenue"].sum().rename("ca_p2")
    
    df_c = df_c.merge(ca_p1, on="StockCode", how="left").merge(ca_p2, on="StockCode", how="left")
    df_c["ca_p1"] = df_c["ca_p1"].fillna(0)
    df_c["ca_p2"] = df_c["ca_p2"].fillna(0)

    df_c["tendance_pct"] = ((df_c["ca_p2"] - df_c["ca_p1"]) / df_c["ca_p1"].replace(0, 1) * 100).round(2)
    
    # Jointure des transactions avec le segment RFM du client
    df_valid_cust = df_clean.dropna(subset=["CustomerID"]).copy()
    df_valid_cust["CustomerID"] = df_valid_cust["CustomerID"].astype(str)
    df_transactions_rfm = df_valid_cust.merge(
        df_rfm[["CustomerID", "segment"]], on="CustomerID", how="left"
    )

    buyers_profile = df_transactions_rfm.groupby("StockCode").agg(
        nb_client=("CustomerID", "nunique"),
        nb_champions_fidele=("segment", lambda s: s.isin(["Champions", "Fidèles"]).sum()),
        nb_total_achats=("CustomerID", "count")
    ).reset_index()

    buyers_profile["pct_champions_fidele"] = (buyers_profile["nb_champions_fidele"] / buyers_profile["nb_total_achats"]).round(2)
    
    df_c = df_c.merge(buyers_profile, on="StockCode", how="left")
    df_c["pct_champions_fidele"] = df_c["pct_champions_fidele"].fillna(0)
    
    df_c["is_candidate"] = (df_c["ca_p2"] < df_c["ca_p1"]) & (df_c["pct_champions_fidele"] < 0.20)
    
    df_candidate = df_c[df_c["is_candidate"]].sort_values(by="ca_total", ascending=False).reset_index(drop=True)
    return df_candidate
