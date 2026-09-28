from numpy import result_type
from common.llm import LLMClient, ReviewLabel
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd
import time
from config import LLM, OUTPUTS

def classify_reviews(text :str, review_id: str , client: LLMClient) -> ReviewLabel:
    variables = {
        "review_text": text,
        "review_id": review_id,
    }
    return client.complete_json("voc_classification", variables, ReviewLabel, review_id)
    
def classify_batch(df: pd.DataFrame, cache_path: Path) -> pd.DataFrame:
    client = LLMClient(OUTPUTS)
    results = []
    for index, row in df.iterrows():
        review_text = row["review_comment_message"]
        review_id = row["review_id"]
        label = classify_reviews(review_text, review_id, client)
        time.sleep(LLM["delay_seconds"])
         
        results.append({
            "review_id": review_id,
            "irritants": label.irritants,
            "sentiment": label.sentiment,
            "urgence": label.urgence,
            "resume_fr": label.resume_fr
})
    
    results_df = pd.DataFrame(results)
    df = df.merge(results_df, on="review_id", how="left")
    return df
    
        
        