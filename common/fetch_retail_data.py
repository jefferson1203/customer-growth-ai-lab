"""
common/fetch_retail_data.py - Téléchargement autonome du dataset Online Retail II.
"""

import os
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
ZIP_PATH = DATA_RAW / "online_retail_ii.zip"
URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"


def download_and_extract_retail_data() -> Path:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    
    # Vérification si le fichier Excel extrait existe déjà
    excel_path = DATA_RAW / "online_retail_II.xlsx"
    if excel_path.exists():
        print(f"Le fichier Online Retail II existe déjà à {excel_path}")
        return excel_path

    print(f"Téléchargement du dataset Online Retail II depuis {URL}...")
    urllib.request.urlretrieve(URL, ZIP_PATH)
    print("Téléchargement terminé. Extraction de l'archive ZIP...")

    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(DATA_RAW)

    print(f"Extraction réussie dans {DATA_RAW}")
    return excel_path


if __name__ == "__main__":
    download_and_extract_retail_data()
