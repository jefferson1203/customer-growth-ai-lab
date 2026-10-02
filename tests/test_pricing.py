import pytest
import pandas as pd
import numpy as np

from pricing.data_prep import prepare_weekly_pricing_data
from pricing.pricing_analysis import run_pricing_diagnostic
from pricing.elasticity import compute_sku_elasticity
from pricing.optimization import optimize_sku_prices, round_psychological_price
from config import PRICING

@pytest.fixture
def sample_retail_df():
    """Génère un petit jeu de données factice avec 2 SKUs sur plusieurs semaines."""
    records = []
    start_date = pd.Timestamp("2010-01-04")
    
    skus = [
        ("SKU1", "ELASTIC ITEM", 10.0, -1.5),
        ("SKU2", "INELASTIC ITEM", 20.0, -0.4)
    ]
    
    np.random.seed(42)
    for week_idx in range(45):
        week_date = start_date + pd.Timedelta(weeks=week_idx)
        
        for stock_code, desc, base_price, elast in skus:
            # Variations de prix
            price = round(base_price * (1.0 + np.random.uniform(-0.15, 0.15)), 2)
            log_q = 5.0 + elast * np.log(price) + np.random.normal(0, 0.05)
            qty = max(1, int(np.exp(log_q)))
            
            records.append({
                "StockCode": stock_code,
                "Description": desc,
                "Invoice": f"INV_{week_idx}_{stock_code}",
                "InvoiceDate": week_date,
                "Quantity": qty,
                "Price": price,
                "Revenue": price * qty,
                "CustomerID": f"CUST_{week_idx % 5}"
            })
            
    return pd.DataFrame(records)


def test_prepare_weekly_pricing_data(sample_retail_df):
    df_weekly, sku_stats = prepare_weekly_pricing_data(sample_retail_df, PRICING)
    
    assert "StockCode" in df_weekly.columns
    assert "YearWeek" in df_weekly.columns
    assert "quantity" in df_weekly.columns
    assert "median_price" in df_weekly.columns
    assert len(df_weekly) > 0
    assert len(sku_stats) == 2


def test_run_pricing_diagnostic(sample_retail_df):
    diagnostic = run_pricing_diagnostic(sample_retail_df)
    
    assert "total_skus_analyzed" in diagnostic
    assert "median_price_ratio_max_min" in diagnostic
    assert "pct_skus_high_dispersion" in diagnostic
    assert "discounts_summary" in diagnostic


def test_compute_sku_elasticity(sample_retail_df):
    df_weekly, sku_stats = prepare_weekly_pricing_data(sample_retail_df, PRICING)
    df_elasticity = compute_sku_elasticity(df_weekly, sku_stats)
    
    assert len(df_elasticity) > 0
    assert set(["StockCode", "elasticity", "p_value", "category"]).issubset(df_elasticity.columns)


def test_round_psychological_price():
    assert round_psychological_price(10.20) == 10.49
    assert round_psychological_price(10.85) == 10.99
    assert round_psychological_price(5.00) == 5.49


def test_optimize_sku_prices(sample_retail_df):
    df_weekly, sku_stats = prepare_weekly_pricing_data(sample_retail_df, PRICING)
    df_elasticity = compute_sku_elasticity(df_weekly, sku_stats)
    df_opt = optimize_sku_prices(df_elasticity, config=PRICING, cost_ratio=0.50)
    
    assert set(["rec_price", "rec_revenue", "rec_margin", "margin_gain_gbp"]).issubset(df_opt.columns)
    assert len(df_opt) == len(df_elasticity)
