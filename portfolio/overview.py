import pandas as pd
from common.data import load_retail
from pathlib import Path
from config import DATA_RAW

def compute_overview_metrics(raw_dir: Path) -> dict:
    df_clean, audit_df = load_retail(raw_dir, with_customer_only=False)

    summary = {}

    # 1. Chiffre d'affaires total
    summary["total_revenue"] = df_clean["Revenue"].sum()

    # 2. Nombre total de transactions      
    summary["total_transactions"] = df_clean["Invoice"].nunique()

    # 3. Nombre total de clients uniques
    summary["unique_customers"] = df_clean["CustomerID"].nunique()
    
    # 4. Nombre de reference produit unique
    summary["unique_products"] = df_clean["StockCode"].nunique()

    #5. Part du CA réalisé au UK
    df_uk = df_clean[df_clean["Country"] == "United Kingdom"]
    summary["uk_revenue_share"] = float(df_uk["Revenue"].sum() / summary["total_revenue"])

    summary["audit_table"] = audit_df.to_dict(orient="records")
    
    return summary
    

    