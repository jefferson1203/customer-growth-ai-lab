import pytest
import pandas as pd
from portfolio.product_analysis import compute_abc_analysis, identify_deletion_candidates
from portfolio.rfm import compute_rfm

@pytest.fixture
def sample_product_data():
    """Crée un jeu de données factice avec des ventes réparties sur 2 ans et des produits distincts."""
    data = {
        "CustomerID": ["1001", "1001", "1002", "1003", "1003"],
        "Invoice": ["INV1", "INV2", "INV3", "INV4", "INV5"],
        "StockCode": ["PROD_A", "PROD_B", "PROD_C", "PROD_C", "PROD_D"],
        "Description": ["Product A", "Product B", "Product C", "Product C", "Product D"],
        "InvoiceDate": pd.to_datetime([
            "2010-01-15", "2010-06-20", "2010-02-10", "2011-05-10", "2010-03-01"
        ]),
        "Quantity": [100, 10, 5, 1, 1],
        "Price": [100.0, 50.0, 10.0, 10.0, 2.0],
        "Revenue": [10000.0, 500.0, 50.0, 10.0, 2.0]
    }
    return pd.DataFrame(data)


def test_compute_abc_analysis(sample_product_data):
    df_prod, summary = compute_abc_analysis(sample_product_data)
    assert len(df_prod) == 4
    assert set(["StockCode", "ca_total", "cum_pct_ca", "categorie_abc"]).issubset(df_prod.columns)
    assert df_prod.iloc[0]["categorie_abc"] in ["A", "B"]
    assert len(summary) >= 1



def test_identify_deletion_candidates(sample_product_data):
    df_rfm = compute_rfm(sample_product_data)
    df_prod, _ = compute_abc_analysis(sample_product_data)
    candidats = identify_deletion_candidates(sample_product_data, df_rfm, df_prod)
    assert isinstance(candidats, pd.DataFrame)
    assert "tendance_pct" in candidats.columns
    assert "pct_champions_fidele" in candidats.columns
