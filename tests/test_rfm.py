import pytest
import pandas as pd
from portfolio.rfm import compute_rfm, compute_rfm_summary, analyse_wholesalers

@pytest.fixture
def sample_retail_data():
    """Crée un petit DataFrame factice avec 3 clients distincts pour les tests."""
    data = {
        "CustomerID": ["1001", "1001", "1002", "1003", "1003", "1003"],
        "Invoice": ["INV1", "INV2", "INV3", "INV4", "INV5", "INV6"],
        "InvoiceDate": pd.to_datetime([
            "2011-12-01", "2011-12-05", "2011-11-01", "2011-01-01", "2011-02-01", "2011-03-01"
        ]),
        "Quantity": [10, 5, 2, 1, 1, 1],
        "Price": [10.0, 20.0, 50.0, 5.0, 5.0, 5.0],
        "Revenue": [100.0, 100.0, 100.0, 5.0, 5.0, 5.0]
    }
    return pd.DataFrame(data)


def test_compute_rfm_structure(sample_retail_data):
    df_rfm = compute_rfm(sample_retail_data)
    assert len(df_rfm) == 3
    assert set(["CustomerID", "Recency", "Frequency", "Monetary", "R_score", "F_score", "M_score", "segment"]).issubset(df_rfm.columns)
    assert df_rfm["segment"].isna().sum() == 0


def test_compute_rfm_summary(sample_retail_data):
    df_rfm = compute_rfm(sample_retail_data)
    summary = compute_rfm_summary(df_rfm)
    assert "segment" in summary.columns
    assert abs(summary["pct_clients"].sum() - 100.0) < 1.0
    assert abs(summary["pct_ca"].sum() - 100.0) < 1.0


def test_analyse_wholesalers(sample_retail_data):
    df_rfm = compute_rfm(sample_retail_data)
    wholesalers = analyse_wholesalers(df_rfm, top_quantile=0.5)
    assert "nb_wholesalers" in wholesalers
    assert "wholesalers_ca" in wholesalers
    assert "pct_ca_wholesalers" in wholesalers
    assert wholesalers["nb_wholesalers"] >= 1
