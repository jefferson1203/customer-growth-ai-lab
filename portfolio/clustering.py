from _pytest import monkeypatch
from sklearn.preprocessing import FunctionTransformer
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
import numpy as np


def train_kmeans(df_rfm: pd.DataFrame, n_clusters: int = 5) -> tuple[pd.DataFrame, float, dict]:
    df_res = df_rfm.copy()
    X = df_res[["Recency", "Frequency", "Monetary"]]

    processor = Pipeline([
        ("log1p", FunctionTransformer(np.log1p)),
        ("scaler", StandardScaler())
    ])
    
    X_scaled = processor.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_res["cluster_kmeans"] = kmeans.fit_predict(X_scaled)
    
    silhouette = silhouette_score(X_scaled, df_res["cluster_kmeans"])

    

    return df_res, silhouette
    
    
    

def compare_rfm_vs_kmeans(df_rfm: pd.DataFrame) -> pd.DataFrame:
    
    cross_matrix = pd.crosstab(df_rfm["segment"], df_rfm["cluster_kmeans"], margins=False)
    
    return cross_matrix