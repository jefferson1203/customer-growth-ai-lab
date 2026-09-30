import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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
    
    df_rfm_copy = df_rfm.copy()
    df_rfm_copy["CustomerID"] = df_rfm_copy["CustomerID"].astype(str)
    
    df_transactions_rfm = df_valid_cust.merge(
        df_rfm_copy[["CustomerID", "segment"]], on="CustomerID", how="left"
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


def plot_pareto_curve(df_prod: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    
    # Courbe Pareto du % cumulé
    fig.add_trace(go.Scatter(
        x=list(range(1, len(df_prod) + 1)),
        y=df_prod["cum_pct_ca"] * 100,
        mode="lines",
        name="CA Cumulé (%)",
        line=dict(color="#1f77b4", width=3)
    ))
    
    # Lignes de démarcation ABC (80% et 95%)
    fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Seuil A (80%)")
    fig.add_hline(y=95, line_dash="dash", line_color="orange", annotation_text="Seuil B (95%)")
    
    fig.update_layout(
        title="Courbe de Pareto (Analyse ABC du Catalogue Produit)",
        xaxis_title="Nombre de références triées par CA",
        yaxis_title="% Cumulé du Chiffre d'Affaires",
        template="plotly_white"
    )
    return fig


def plot_long_tail_scatter(df_candidates: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df_candidates,
        x="nb_client",
        y="tendance_pct",
        size="ca_total",
        color="pct_champions_fidele",
        hover_data=["StockCode", "Description", "ca_total"],
        title="Diagnostic des Références C (Tendance vs Nombre d'Acheteurs)",
        labels={
            "nb_client": "Nombre d'acheteurs uniques",
            "tendance_pct": "Tendance Année 2 vs Année 1 (%)",
            "pct_champions_fidele": "% Acheteurs VIP"
        },
        template="plotly_white"
    )
    fig.add_hline(y=0, line_dash="dot", line_color="red")
    return fig

