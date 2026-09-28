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

def prepare_voc_data(raw_data :dict) -> pd.DataFrame:
    """ fusionner les données olist et retail  """
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


        

def load_retail(raw_dir: Path, with_customer_only: bool = False) -> pd.DataFrame:
    """Online Retail II nettoyé (règles du projet 2), colonne Revenue ajoutée.
    Renvoie aussi le tableau des lignes retirées par règle."""