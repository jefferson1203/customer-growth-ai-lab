import pytest
import pandas as pd
from portfolio.business_case import (
    compute_business_case_a,
    compute_business_case_b,
    compute_sensitivity_tables,
)

@pytest.fixture
def sample_rfm_data():
    return pd.DataFrame({
        "CustomerID": [str(i) for i in range(100)],
        "segment": ["À risque"] * 20 + ["Champions"] * 50 + ["Fidèles"] * 30,
        "Monetary": [100.0] * 20 + [500.0] * 50 + [200.0] * 30,
    })

@pytest.fixture
def sample_candidates_data():
    return pd.DataFrame({
        "StockCode": [f"SKU_{i}" for i in range(10)],
        "ca_total": [1000.0] * 10,
    })

def test_compute_business_case_a(sample_rfm_data):
    config = {
        "control_group_pct": 0.10,
        "contact_cost_eur": 2.0,
        "response_rate": 0.10,
        "margin_rate": 0.30,
    }
    res = compute_business_case_a(sample_rfm_data, config=config)
    
    assert res["nb_client"] == 20
    assert res["n_control"] == 2
    assert res["n_treatment"] == 18
    assert res["cost"] == 36.0  # 18 * 2.0
    assert res["panier_moyen"] == 100.0
    assert res["gross_margin"] == 54.0  # 1.8 * 100 * 0.30
    assert res["net_margin"] == 18.0   # 54 - 36
    assert res["roi_pct"] == 50.0      # (18 / 36) * 100

def test_compute_business_case_b(sample_candidates_data):
    config = {
        "cost_per_sku_eur": 500.0,
        "transfer_rate": 0.50,
        "margin_rate": 0.30,
    }
    res = compute_business_case_b(sample_candidates_data, config=config)
    
    assert res["nb_candidates"] == 10
    assert res["ca_at_risk"] == 10000.0
    assert res["saving"] == 5000.0       # 10 * 500
    assert res["lost_margin"] == 1500.0  # 10000 * 0.5 * 0.30
    assert res["net_gain"] == 3500.0     # 5000 - 1500

def test_compute_sensitivity_tables(sample_rfm_data, sample_candidates_data):
    config = {
        "control_group_pct": 0.10,
        "contact_cost_eur": 2.0,
        "cost_per_sku_eur": 500.0,
        "transfer_rate": 0.50,
        "margin_rate": 0.30,
    }
    sens_a, sens_b = compute_sensitivity_tables(sample_rfm_data, sample_candidates_data, config=config)
    assert not sens_a.empty
    assert not sens_b.empty
    assert "30%" in sens_a.columns
    assert "500 €" in sens_b.columns
