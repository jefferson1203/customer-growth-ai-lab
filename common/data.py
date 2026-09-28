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

def load_retail(raw_dir: Path, with_customer_only: bool = False) -> pd.DataFrame:
    """Online Retail II nettoyé (règles du projet 2), colonne Revenue ajoutée.
    Renvoie aussi le tableau des lignes retirées par règle."""