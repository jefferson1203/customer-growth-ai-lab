import pandas as pd

def calculate_nps_proxy(df: pd.DataFrame) -> float:
    """Calcule le NPS proxy à partir du dataframe.

    Args:
        df (pd.DataFrame): DataFrame contenant les données.

    Returns:
        float: Valeur du NPS proxy.
    """
    promoteur = (df["review_score"] == 5).mean() * 100
    detracteur = (df["review_score"] <= 3).mean() * 100

    return promoteur - detracteur

def compute_prioritization_matrix(classified_df: pd.DataFrame, full_df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la matrice de priorisation avec redressement des poids réels des notes (1-3 stars)."""
    irritants_list = classified_df["irritants"].explode().unique()
    irritants_list = [i for i in irritants_list if i and i != "POSITIF" and isinstance(i, str)]

    neg_df = classified_df[classified_df["review_score"] <= 3].copy()
    
    # Calcul des poids de redressement selon la distribution réelle Olist des avis négatifs
    # Distribution réelle Olist (1-3 stars) : 1★: 60.5%, 2★: 14.8%, 3★: 24.7%
    real_dist = {1: 0.605, 2: 0.148, 3: 0.247}
    sample_counts = neg_df["review_score"].value_counts()
    sample_dist = sample_counts / len(neg_df)
    
    weights_map = {score: real_dist[score] / sample_dist[score] for score in [1, 2, 3] if score in sample_dist}
    neg_df["weight"] = neg_df["review_score"].map(weights_map).fillna(1.0)
    classified_df_copy = classified_df.copy()
    classified_df_copy["weight"] = classified_df_copy["review_score"].map(weights_map).fillna(1.0)

    records = []
    total_weighted_neg = neg_df["weight"].sum()

    for irr in irritants_list:
        has_irr_neg = neg_df["irritants"].apply(lambda x: irr in x if isinstance(x, list) else False)
        has_irr_all = classified_df_copy["irritants"].apply(lambda x: irr in x if isinstance(x, list) else False)
        
        weighted_freq = (neg_df[has_irr_neg]["weight"].sum() / total_weighted_neg) * 100 if total_weighted_neg > 0 else 0
        unweighted_freq = (has_irr_neg.sum() / len(neg_df)) * 100 if len(neg_df) > 0 else 0
        
        weighted_note_moy = (classified_df_copy[has_irr_all]["review_score"] * classified_df_copy[has_irr_all]["weight"]).sum() / classified_df_copy[has_irr_all]["weight"].sum() if has_irr_all.sum() > 0 else 0
        
        records.append({
            "irritant": irr,
            "frequence_redressee": round(weighted_freq, 2),
            "frequence_brute": round(unweighted_freq, 2),
            "note_moyenne_redressee": round(weighted_note_moy, 2),
            "nb_avis": int(has_irr_all.sum())
        })

    res = pd.DataFrame(records).sort_values(by="frequence_redressee", ascending=False)
    res = res.rename(columns={"frequence_redressee": "frequence", "note_moyenne_redressee": "note_moyenne"})
    return res


def analyze_delay_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Analyse l'impact du délai et inclut explicitement la tranche 'Non livrée'."""
    temp_df = df.copy()
    
    # Identifier les commandes non livrées (date de livraison manquante)
    non_livrees = temp_df["order_delivered_customer_date"].isna() | temp_df["retard_jours"].isna()
    
    bins = [-float("inf"), 0, 3, 10, float("inf")]
    labels = [
        "1. À l'heure ou avance",
        "2. Retard 1-3j",
        "3. Retard 4-10j",
        "4. Retard >10j"
    ]

    temp_df["tranche_retard"] = pd.cut(temp_df["retard_jours"], bins=bins, labels=labels).astype(str)
    temp_df.loc[non_livrees, "tranche_retard"] = "0. Non livrée (Commande perdue/annulée)"

    res = temp_df.groupby("tranche_retard", observed=False).agg(
        nb_commandes=("review_id", "count"),
        note_moyenne=("review_score", lambda s: round(s.mean(), 2)),
        pct_detracteurs=("review_score", lambda s: round((s <= 3).mean() * 100, 2))
    ).reset_index()

    return res.sort_values(by="tranche_retard")

    
    