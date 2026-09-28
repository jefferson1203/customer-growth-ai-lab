from pathlib import Path
import pandas as pd

def load_olist(raw_dir: Path) -> dict[str, pd.DataFrame]:
    """Fichiers Olist utiles, dates converties."""

def load_retail(raw_dir: Path, with_customer_only: bool = False) -> pd.DataFrame:
    """Online Retail II nettoyé (règles du projet 2), colonne Revenue ajoutée.
    Renvoie aussi le tableau des lignes retirées par règle."""