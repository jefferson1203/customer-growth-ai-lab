from dotenv import load_dotenv
load_dotenv()

from config import DATA_RAW
from common.data import load_olist, prepare_voc_data
from voc.predictive import prepare_ml_dataset


def inspect_predictive_features():
    """Inspecte les colonnes et types de variables pour le modèle prédictif."""
    data = load_olist(DATA_RAW)
    df = prepare_voc_data(data)
    
    print("=== APERÇU DU DATAFRAME COMPLET ===")
    print(f"Nombre total de lignes : {len(df)}")
    
    X, y = prepare_ml_dataset(df)
    
    print("\n=== DISTRIBUTION DE LA CIBLE (y) ===")
    print(y.value_counts(normalize=True).rename({0: "Non-Détracteur (4-5)", 1: "Détracteur (1-3)"}))
    
    print("\n=== TYPES ET VALEURS MANQUANTES (X) ===")
    print(X.info())
    print("\nNombre de valeurs manquantes par colonne :")
    print(X.isna().sum())
    
    print("\n=== STATISTIQUES NUMÉRIQUES ===")
    print(X.describe())
    
    print("\n=== CARDINALITÉ DES CATEGORIELLES ===")
    for col in X.select_dtypes(include=['object', 'category']).columns:
        print(f"{col} : {X[col].nunique()} valeurs uniques")


if __name__ == "__main__":
    inspect_predictive_features()
