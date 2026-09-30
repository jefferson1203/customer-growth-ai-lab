import pandas as pd



def compute_rfm(df_clean: pd.DataFrame) -> pd.DataFrame:

    snapshot_date = df_clean["InvoiceDate"].max() + pd.Timedelta(days=1)
    df_only_customers = df_clean[df_clean["CustomerID"].notna()]
    df_rfm = df_only_customers.groupby("CustomerID").agg({
        "InvoiceDate": lambda x: (snapshot_date - x.max()).days,
        "Invoice": "nunique",
        "Revenue": "sum"
    }).reset_index()
    df_rfm.columns = ["CustomerID", "Recency", "Frequency", "Monetary"]

    df_rfm["R_score"] = pd.qcut(df_rfm["Recency"], 5, labels=[5,4,3,2,1])
    df_rfm["F_score"] = pd.qcut(df_rfm["Frequency"].rank(method="first"), 5, duplicates="drop", labels=[1,2,3,4,5])
    df_rfm["M_score"] = pd.qcut(df_rfm["Monetary"], 5,labels=[1,2,3,4,5])

    df_rfm["R_score"] = df_rfm["R_score"].astype(int)
    df_rfm["F_score"] = df_rfm["F_score"].astype(int)
    df_rfm["M_score"] = df_rfm["M_score"].astype(int)

    def get_segment(row):
        r, f = row["R_score"], row["F_score"]
        if r >= 4 and f >= 4:
            return "Champions"
        if r >= 3 and f >= 3:
            return "Fidèles"
        if r >= 4 and f <= 1:
            return "Nouveaux"
        if r >= 3 and f <= 2:
            return "Prometteurs"
        if r <= 2 and f >= 3:
            return "À risque"
        return "En sommeil"

    df_rfm["segment"] = df_rfm.apply(get_segment, axis=1)

    return df_rfm

def compute_rfm_summary(df_rfm: pd.DataFrame) -> pd.DataFrame:
    total_clients = len(df_rfm)
    total_ca = df_rfm["Monetary"].sum()

    summary = df_rfm.groupby("segment").agg(
        nb_clients=("CustomerID", "count"),
        ca_total=("Monetary", "sum"),
        ca_moyen_client=("Monetary", "mean"),
        recence_moyenne=("Recency", "mean"),
        frequence_moyenne=("Frequency", "mean")
    ).round(2).astype({
        "nb_clients": int,
        "ca_total": float,
        "ca_moyen_client": float,
        "recence_moyenne": float,
        "frequence_moyenne": float
    }).reset_index()

    summary["pct_clients"] = (summary["nb_clients"] / total_clients * 100).round(1).astype(float)
    summary["pct_ca"] = (summary["ca_total"] / total_ca * 100).round(1).astype(float)
    
    return summary.sort_values("pct_ca", ascending=False).reset_index(drop=True)

        

def analyse_wholesalers(df_rfm: pd.DataFrame, top_quantile: float = 0.99) -> dict:
    wholesalers_list = df_rfm[ df_rfm["Monetary"] >= df_rfm["Monetary"].quantile(top_quantile)]
    summary = {
        "nb_wholesalers": len(wholesalers_list),
        "wholesalers_ca": float(round(wholesalers_list["Monetary"].sum(), 2)),
        "pct_ca_wholesalers": float(round(wholesalers_list["Monetary"].sum() / df_rfm["Monetary"].sum() * 100, 2))
    }
    return summary