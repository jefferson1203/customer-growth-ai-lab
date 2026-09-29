from pathlib import Path
import pandas as pd
from config import VOC, OUTPUTS
import json


def generate_validation_sample(
    sample_df: pd.DataFrame, 
    classified_df: pd.DataFrame = None, 
    n: int = VOC["manual_labels"]
) -> pd.DataFrame:
    """Génère un échantillon aléatoire d'avis pour l'annotation manuelle.

    Args:
        sample_df (pd.DataFrame): DataFrame contenant les avis bruts.
        classified_df (pd.DataFrame, optional): DataFrame des classifications LLM (avec resume_fr).
        n (int, optional): Nombre d'avis à extraire pour la validation.

    Returns:
        pd.DataFrame: DataFrame de l'échantillon de validation exporté au format CSV.
    """
    df_to_sample = sample_df.copy()
    
    # Si les prédictions LLM sont fournies, on rattache le résumé en français
    if classified_df is not None and "resume_fr" in classified_df.columns:
        df_to_sample = df_to_sample.merge(classified_df[["review_id", "resume_fr"]], on="review_id", how="inner")
    
    val_df = df_to_sample.sample(n=n, random_state=VOC["seed"]).copy()
    
    cols = ["review_id", "review_comment_message"]
    if "resume_fr" in val_df.columns:
        cols.append("resume_fr")
        
    val_df = val_df[cols].copy()
    val_df["manual_irritants"] = ""
    
    cache_path = OUTPUTS / "voc" 
    cache_path.mkdir(parents=True, exist_ok=True)
    file_path = cache_path / f"validation_sample_{n}.csv"
    val_df.to_csv(file_path, index=False)
    print(f"Validation sample généré ({len(val_df)} avis) -> {file_path}")
    return val_df


def evaluate_classification(manual_path: Path, llm_cache_path: Path) -> pd.DataFrame:
    """Calcule les métriques de performance de classification (TP, FP, FN, Précision, Rappel, F1-score) par irritant.

    Args:
        manual_path (Path): Chemin vers le fichier CSV annoté manuellement.
        llm_cache_path (Path): Chemin vers le cache JSONL des classifications LLM.

    Returns:
        pd.DataFrame: Tableau récapitulatif des métriques par irritant.
    """
    manual_df = pd.read_csv(manual_path)
    
    from common.llm import load_labels
    from voc.schema import ReviewLabel
    
    llm_df = load_labels(llm_cache_path, ReviewLabel)
    llm_df["review_id"] = llm_df["review_id"].astype(str)
    manual_df["review_id"] = manual_df["review_id"].astype(str)


    irritants_list  = llm_df['irritants'].explode().unique().tolist()
    
    merged_df = manual_df.merge(llm_df, on="review_id", how="inner")

    metrics = []

    for irr in irritants_list:
        tp, fp, fn = 0, 0, 0
        
        for _, row in merged_df.iterrows():
            manual_list = [x.strip() for x in str(row["manual_irritants"]).split(",") if x.strip()]
            llm_list = row["irritants"] if isinstance(row["irritants"], list) else []

            in_manual = irr in manual_list
            in_llm = irr in llm_list

            if in_manual and in_llm:
                tp += 1
            elif in_manual and not in_llm:
                fn += 1
            elif not in_manual and in_llm:
                fp += 1
            
            
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics.append({
            "irritant": irr,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
        })
    return pd.DataFrame(metrics)

    