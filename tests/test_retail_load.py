"""
tests/test_retail_load.py - Inspection du chargement Online Retail II
"""

import time
from config import DATA_RAW
from common.data import load_retail

def test_load():
    start = time.time()
    print("Test de la fonction load_retail()...")
    df_clean, audit_df = load_retail(DATA_RAW, with_customer_only=False)
    duration = time.time() - start

    print(f"\nChargement et nettoyage effectués en {duration:.2f} secondes.")
    print(f"\n--- TABLEAU D'AUDIT DU NETTOYAGE ---")
    print(audit_df.to_string(index=False))

    print(f"\n--- APERÇU DES TRANSACTIONS NETTOYÉES ---")
    print(f"Total Chiffre d'Affaires : {df_clean['Revenue'].sum():,.2f} £")
    print(f"Nombre de factures distinctes : {df_clean['Invoice'].nunique():,}")
    print(f"Nombre de références produits : {df_clean['StockCode'].nunique():,}")
    print(f"Nombre de clients identifiés : {df_clean['CustomerID'].dropna().nunique():,}")

if __name__ == "__main__":
    test_load()
