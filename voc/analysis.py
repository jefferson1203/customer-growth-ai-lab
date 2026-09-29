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

def compute_prioritization_matrix(classified_df :pd.DataFrame, full_df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la matrice de priorisation à partir du dataframe classifié.

    Args:
        classified_df (pd.DataFrame): DataFrame contenant les données classifiées.
        full_df (pd.DataFrame): DataFrame contenant les données complètes.

    Returns:
        pd.DataFrame: Matrice de priorisation.
    """
    irritants_list = classified_df["irritants"].explode().unique()

    irritants_list = irritants_list[(irritants_list != "POSITIF") & (irritants_list != "")].tolist()

    neg_df = classified_df[classified_df["review_score"] <= 3]

    records = []
    total_neg = len(neg_df)

    for irr in irritants_list:
        # Filtres booléens
        has_irr = classified_df["irritants"].apply(lambda x: irr in x if isinstance(x, list) else False)
        has_irr_neg = neg_df["irritants"].apply(lambda x: irr in x if isinstance(x, list) else False)
        
        freq = (has_irr_neg.sum() / total_neg) * 100 if total_neg > 0 else 0
        note_moy = classified_df[has_irr]["review_score"].mean()
        
        records.append({
            "irritant": irr,
            "frequence": round(freq, 2),
            "note_moyenne": round(note_moy, 2),
            "nb_avis": has_irr.sum()
        })

    return pd.DataFrame(records).sort_values(by="frequence", ascending=False)
 
                  

def analyze_delay_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Analyse l'impact du délai de réponse sur la note moyenne.

    Args:
        df (pd.DataFrame): DataFrame contenant les données.

    Returns:
        pd.DataFrame: Tableau récapitulatif de l'impact du délai de réponse.
    """
    bins = [-float("inf"), 0, 3, 10, float("inf")]
    labels = [
        "1. À l'heure ou avance",
        "2. Retard 1-3j",
        "3. Retard 4-10j",
        "4. Retard >10j"
    ]

    temp_df = df.copy()
    temp_df["tranche_retard"] = pd.cut(temp_df["retard_jours"], bins=bins, labels=labels)

    return temp_df.groupby("tranche_retard", observed=False).agg(
        nb_commandes=("review_id", "count"),
        note_moyenne=("review_score", lambda s: round(s.mean(), 2)),
        pct_detracteurs=("review_score", lambda s: round((s <= 3).mean() * 100, 2))
    ).reset_index()

    
    