import pandas as pd

def get_stratified_sample(df : pd.DataFrame, sample_per_score : int, seed : int = 42) -> pd.DataFrame:
    """ stratifier sur les notes et retourner un echantillon """
    
    sample = df.groupby("review_score").sample(n=sample_per_score, random_state=seed)
    return sample.reset_index(drop=True)