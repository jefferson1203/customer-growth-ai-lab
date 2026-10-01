from pathlib import Path
import pandas as pd

def load_olist(raw_dir: Path) -> dict[str, pd.DataFrame]:
    """Fichiers Olist utiles, dates converties."""
    orders_review = pd.read_csv(raw_dir / "olist_order_reviews_dataset.csv")
    orders = pd.read_csv(raw_dir / "olist_orders_dataset.csv")
    order_items = pd.read_csv(raw_dir / "olist_order_items_dataset.csv")
    products = pd.read_csv(raw_dir / "olist_products_dataset.csv")
    product_category_name_translation = pd.read_csv(raw_dir / "product_category_name_translation.csv")

    order_items["shipping_limit_date"] = pd.to_datetime(order_items["shipping_limit_date"])
    orders_review["review_creation_date"] = pd.to_datetime(orders_review["review_creation_date"])
    orders_review["review_answer_timestamp"] = pd.to_datetime(orders_review["review_answer_timestamp"])
    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
    orders["order_approved_at"] = pd.to_datetime(orders["order_approved_at"])
    orders["order_delivered_carrier_date"] = pd.to_datetime(orders["order_delivered_carrier_date"])
    orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"])
    orders["order_estimated_delivery_date"] = pd.to_datetime(orders["order_estimated_delivery_date"])

    return {
        "reviews": orders_review,
        "orders": orders,
        "items": order_items,
        "products": products,
        "categories": product_category_name_translation,
    }


def prepare_voc_data(raw_data: dict) -> pd.DataFrame:
    """Fusionner les données Olist et préparer les features VoC."""
    df = raw_data["reviews"].copy()
    
    df = df.merge(raw_data["orders"], on="order_id", how="left")
    df = df.merge(raw_data["items"], on="order_id", how="left")
    df = df.merge(raw_data["products"], on="product_id", how="left")
    df = df.merge(raw_data["categories"], on="product_category_name", how="left")
        
    df.drop_duplicates(subset="review_id", keep="first", inplace=True)
    df["retard_jours"] = (df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]).dt.days
    df = df.dropna(subset=["review_comment_message"])
    df = df[df["review_comment_message"].str.strip().astype(bool)]
    
    return df


def load_retail(raw_dir: Path, with_customer_only: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Online Retail II nettoyé selon les règles du Projet 2.
    - Écarte les factures d'annulation (commençant par 'C')
    - Écarte Quantity <= 0 et Price <= 0
    - Écarte les StockCode non-produits (POST, D, DOT, M, BANK CHARGES, AMAZONFEE, etc.)
    - Calcule Revenue = Quantity * Price
    - Optionnel : Écarte les Customer ID manquants

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (df_clean, audit_df)
    """
    parquet_cache = raw_dir / "online_retail_II_merged.parquet"
    excel_file = raw_dir / "online_retail_II.xlsx"

    if parquet_cache.exists():
        df_raw = pd.read_parquet(parquet_cache)
    elif excel_file.exists():
        print(f"Chargement initial depuis {excel_file} (combinaison des deux années)...")
        df_y1 = pd.read_excel(excel_file, sheet_name="Year 2009-2010")
        df_y2 = pd.read_excel(excel_file, sheet_name="Year 2010-2011")
        df_raw = pd.concat([df_y1, df_y2], ignore_index=True)
        # Normalisation des colonnes et des types pour Parquet
        df_raw.columns = [c.strip().replace(" ", "_") for c in df_raw.columns]
        for col in ["Invoice", "StockCode", "Description", "Country"]:
            if col in df_raw.columns:
                df_raw[col] = df_raw[col].astype(str)
        df_raw.to_parquet(parquet_cache, index=False)
        print(f"Cache Parquet sauvegardé dans {parquet_cache}")
    else:
        raise FileNotFoundError(f"Aucun fichier Online Retail II trouvé dans {raw_dir}")

    # Normalisation des noms de colonnes
    df_raw = df_raw.rename(columns={
        "Customer_ID": "CustomerID",
        "Invoice": "Invoice",
        "StockCode": "StockCode",
        "Description": "Description",
        "Quantity": "Quantity",
        "InvoiceDate": "InvoiceDate",
        "Price": "Price",
        "Country": "Country"
    })

    audit_logs = []
    initial_rows = len(df_raw)
    audit_logs.append({"Etape": "1. Transactions Brutes", "Lignes": initial_rows, "Retirées": 0})

    # Rule 1: Annulations
    df_step1 = df_raw[~df_raw["Invoice"].astype(str).str.startswith("C")].copy()
    cancellations_removed = len(df_raw) - len(df_step1)
    audit_logs.append({"Etape": "2. Retrait des Annulations (Invoice 'C')", "Lignes": len(df_step1), "Retirées": cancellations_removed})

    # Rule 2: Quantity > 0 and Price > 0
    df_step2 = df_step1[(df_step1["Quantity"] > 0) & (df_step1["Price"] > 0)].copy()
    invalid_qp_removed = len(df_step1) - len(df_step2)
    audit_logs.append({"Etape": "3. Retrait Quantity <= 0 et Price <= 0", "Lignes": len(df_step2), "Retirées": invalid_qp_removed})

    # Rule 3: Non-product StockCodes
    non_product_codes = [
        "POST", "D", "DOT", "M", "BANK CHARGES", "AMAZONFEE", 
        "ADJUST", "TEST", "PADS", "CRUK", "C2"
    ]
    stock_clean = df_step2["StockCode"].astype(str).str.strip().str.upper()
    df_step3 = df_step2[~stock_clean.isin(non_product_codes)].copy()
    df_step3 = df_step3[~stock_clean.str.startswith("TEST")].copy()
    non_prod_removed = len(df_step2) - len(df_step3)
    audit_logs.append({"Etape": "4. Retrait Frais & Non-produits (POST, DOT, M...)", "Lignes": len(df_step3), "Retirées": non_prod_removed})

    # Add Revenue
    df_clean = df_step3.copy()
    df_clean["Revenue"] = df_clean["Quantity"] * df_clean["Price"]
    df_clean["InvoiceDate"] = pd.to_datetime(df_clean["InvoiceDate"])

    # Rule 4 (Optionnel) : CustomerID Manquant
    if with_customer_only:
        df_customer = df_clean.dropna(subset=["CustomerID"]).copy()
        df_customer["CustomerID"] = df_customer["CustomerID"].astype(int).astype(str)
        missing_cust_removed = len(df_clean) - len(df_customer)
        audit_logs.append({"Etape": "5. Retrait CustomerID Manquant", "Lignes": len(df_customer), "Retirées": missing_cust_removed})
        df_clean = df_customer

    audit_df = pd.DataFrame(audit_logs)
    return df_clean, audit_df
        
    
    