"""
copilot/tests/test_business_rules.py - Suite d'évaluation des 15 règles métier déterministes de l'API REST.
"""

import csv
from pathlib import Path
from fastapi.testclient import TestClient

from copilot.api.main import app

client = TestClient(app)
API_KEY_HEADER = {"X-API-Key": "dev-secret-key"}


def test_run_15_evaluation_scenarios():
    """Charge et exécute les 15 scénarios d'évaluation déterministes."""
    csv_path = Path(__file__).parent / "scenarios.csv"
    assert csv_path.exists(), f"Fichier scénarios introuvable : {csv_path}"

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        scenarios = list(reader)

    assert len(scenarios) == 15, f"Attendu 15 scénarios, trouvé {len(scenarios)}"

    passed_count = 0

    for sc in scenarios:
        sid = sc["scenario_id"]
        expected = sc["expected_status"]

        if sid == "S01":
            res = client.get("/sante")
            assert res.status_code == 200
            assert res.json()["status"] == "ok"
            passed_count += 1

        elif sid in ["S02", "S03", "S04", "S05", "S06", "S07", "S08", "S13", "S14", "S15"]:
            payload = {
                "customer_id": sc["customer_id"],
                "stock_code": sc["stock_code"],
                "proposed_discount_pct": float(sc["proposed_discount_pct"])
            }
            res = client.post("/offres/verifier", json=payload, headers=API_KEY_HEADER)
            assert res.status_code == 200
            data = res.json()
            assert expected.split(" ")[0] in data["status"], f"Échec {sid}: {data['status']} != {expected}"
            passed_count += 1

        elif sid == "S09":
            res = client.get(f"/produits/{sc['stock_code']}/prix", headers=API_KEY_HEADER)
            assert res.status_code == 200
            passed_count += 1

        elif sid == "S10":
            res = client.get(f"/produits/{sc['stock_code']}/prix", headers=API_KEY_HEADER)
            assert res.status_code == 404
            passed_count += 1

        elif sid == "S11":
            res = client.get("/politique-commerciale", headers=API_KEY_HEADER)
            assert res.status_code == 200
            passed_count += 1

        elif sid == "S12":
            res = client.get(f"/clients/{sc['customer_id']}/opportunites", headers=API_KEY_HEADER)
            assert res.status_code == 200
            passed_count += 1

    assert passed_count == 15
