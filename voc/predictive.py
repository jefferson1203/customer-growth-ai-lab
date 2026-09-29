import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import HistGradientBoostingClassifier
from config import VOC


def prepare_ml_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Prépare les variables explicatives X et la cible binaire y (is_detractor) sans data leakage."""
    y = (df["review_score"] <= 3).astype(int)
    
    df_temp = df.copy()
    if "delai_livraison_jours" not in df_temp.columns:
        df_temp["delai_livraison_jours"] = (df_temp["order_delivered_customer_date"] - df_temp["order_purchase_timestamp"]).dt.days

    cols = ['retard_jours', 'delai_livraison_jours', 'freight_value', 'price', 'product_category_name_english']
    X = df_temp[cols].copy()
    
    X['retard_jours'] = X['retard_jours'].fillna(0)
    X['delai_livraison_jours'] = X['delai_livraison_jours'].fillna(0)
    X['freight_value'] = X['freight_value'].fillna(X['freight_value'].median())
    X['price'] = X['price'].fillna(X['price'].median())
    X['product_category_name_english'] = X['product_category_name_english'].fillna('inconnu')
    
    return X, y


def train_eval_nps_model(X: pd.DataFrame, y: pd.Series, model_type: str = "logistic") -> dict:
    """Entraîne un modèle (Logistic Regression ou HistGradientBoosting) et évalue ses performances.

    Args:
        X (pd.DataFrame): Features explicatives.
        y (pd.Series): Cible binaire (is_detractor).
        model_type (str, optional): "logistic" ou "gb" (HistGradientBoosting).

    Returns:
        dict: Métriques et modèle entraîné.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=VOC["seed"], stratify=y
    )

    num_cols = ["retard_jours", "delai_livraison_jours", "freight_value", "price"]
    cat_cols = ["product_category_name_english"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
        ]
    )

    if model_type == "gb":
        clf = HistGradientBoostingClassifier(random_state=VOC["seed"], max_iter=100)
    else:
        clf = LogisticRegression(max_iter=1000, random_state=VOC["seed"])

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", clf)
    ])
    pipeline.fit(X_train, y_train)

    # 4. Calcul de l'AUC et du taux de détracteurs dans le Top 10%
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_proba)

    # Sélection des 10% des avis avec les plus fortes probabilités prédites
    test_res = pd.DataFrame({"y_true": y_test, "prob": y_proba})
    top_10 = test_res.sort_values("prob", ascending=False).head(int(len(test_res) * 0.10))
    top_10_rate = top_10["y_true"].mean() * 100

    return {
        "model": pipeline,
        "auc": round(auc, 3),
        "top_10_detractor_rate": round(top_10_rate, 2),
        "baseline_detractor_rate": round(y_test.mean() * 100, 2)
    }

