import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.roi_calculator import calculate_roi, classify_roi, ROI_INPUT_FIELDS


BASE_PARAMS = {
    "headcount": 10,
    "avg_annual_salary": 75000,
    "annual_volume": 50000,
    "hours_per_unit_current": 0.5,
    "hours_per_unit_automated": 0.05,
    "error_rate_current_pct": 5.0,
    "error_rate_automated_pct": 0.5,
    "avg_cost_per_error": 100,
    "automation_budget": 300000,
}


def test_calculate_roi_basic():
    result = calculate_roi(BASE_PARAMS)
    assert result["annual_savings"] > 0
    assert result["payback_years"] is not None and result["payback_years"] > 0
    assert result["roi_3yr_pct"] > 0
    assert result["ftes_redeployed"] > 0
    assert result["labor_savings"] > 0
    assert result["error_savings"] > 0


def test_calculate_roi_negative():
    params = dict(BASE_PARAMS)
    params["hours_per_unit_automated"] = 0.8
    params["automation_budget"] = 5000000
    params["error_rate_automated_pct"] = 10
    result = calculate_roi(params)
    assert (
        result["annual_savings"] < 0
        or result["payback_years"] is None
        or result["payback_years"] > 10
    )


def test_calculate_roi_zero_budget():
    params = dict(BASE_PARAMS)
    params["automation_budget"] = 0
    result = calculate_roi(params)
    assert result["payback_years"] is None


def test_calculate_roi_with_defaults():
    result = calculate_roi({})
    assert result["annual_savings"] == 0


def test_classify_roi_negative():
    result = classify_roi(
        {"annual_savings": -1000, "payback_years": None, "roi_3yr_pct": -50}
    )
    assert "NEGATIVE" in result["category"]


def test_classify_roi_exceptional():
    result = classify_roi(
        {"annual_savings": 500000, "payback_years": 0.5, "roi_3yr_pct": 400}
    )
    assert "EXCEPTIONAL" in result["category"]


def test_classify_roi_good():
    result = classify_roi(
        {"annual_savings": 150000, "payback_years": 2, "roi_3yr_pct": 50}
    )
    assert "GOOD" in result["category"]


def test_classify_roi_modest():
    result = classify_roi(
        {"annual_savings": 80000, "payback_years": 4, "roi_3yr_pct": 20}
    )
    assert "MODEST" in result["category"]


def test_classify_roi_poor():
    result = classify_roi(
        {"annual_savings": 10000, "payback_years": 8, "roi_3yr_pct": 5}
    )
    assert "POOR" in result["category"]


def test_roi_input_fields_completeness():
    assert len(ROI_INPUT_FIELDS) == 9
    for field in ROI_INPUT_FIELDS:
        assert "id" in field
        assert "label" in field
        assert "type" in field
        assert "default" in field


def test_calculate_roi_redeployment():
    result = calculate_roi(BASE_PARAMS)
    assert result["ftes_redeployed"] <= BASE_PARAMS["headcount"]
    assert result["ftes_redeployed"] >= 0


def test_calculate_roi_error_reduction():
    result = calculate_roi(BASE_PARAMS)
    assert result["errors_current_annual"] > result["errors_automated_annual"]


def test_npv_calculation():
    result = calculate_roi(BASE_PARAMS)
    if result["npv_3yr"] != 0:
        assert result["annual_savings"] > 0


def test_maintenance_default():
    result = calculate_roi(BASE_PARAMS)
    assert result["maintenance_yearly"] > 0
