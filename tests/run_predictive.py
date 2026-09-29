from dotenv import load_dotenv
load_dotenv()

from config import DATA_RAW
from common.data import load_olist, prepare_voc_data
from voc.predictive import prepare_ml_dataset, train_eval_nps_model


def main():
    print("Chargement des données Olist...")
    data = load_olist(DATA_RAW)
    df = prepare_voc_data(data)
    
    print("Préparation du dataset ML (X, y)...")
    X, y = prepare_ml_dataset(df)
    
    print("\n--- 1. MODÈLE LOGISTIC REGRESSION (Baseline) ---")
    log_metrics = train_eval_nps_model(X, y, model_type="logistic")
    print(f"• AUC-ROC : {log_metrics['auc']}")
    print(f"• Taux détracteurs Top 10% : {log_metrics['top_10_detractor_rate']} %")
    lift_log = round(log_metrics['top_10_detractor_rate'] / log_metrics['baseline_detractor_rate'], 2)
    print(f"• Lift : {lift_log}x")
    
    print("\n--- 2. MODÈLE GRADIENT BOOSTING (HistGradientBoosting) ---")
    gb_metrics = train_eval_nps_model(X, y, model_type="gb")
    print(f"• AUC-ROC : {gb_metrics['auc']}")
    print(f"• Taux détracteurs Top 10% : {gb_metrics['top_10_detractor_rate']} %")
    lift_gb = round(gb_metrics['top_10_detractor_rate'] / gb_metrics['baseline_detractor_rate'], 2)
    print(f"• Lift : {lift_gb}x")


if __name__ == "__main__":
    main()
