import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.what_if import run_what_if, sensitivity_analysis, WHAT_IF_PRESETS
from engine.scorer import SCORING_DEFAULTS


BASE_DIMS = {
    "data_quality": 40,
    "process_stability": 45,
    "exception_rate": 50,
    "decision_complexity": 55,
    "integration_readiness": 35,
    "governance_risk": 30,
    "roi_potential": 60,
}

HIGH_DIMS = {k: 85 for k in BASE_DIMS}
LOW_DIMS = {k: 15 for k in BASE_DIMS}


def test_run_what_if_basic():
    result = run_what_if(BASE_DIMS, {"data_quality": 30, "governance_risk": 35})
    assert result["adjusted_scores"]["data_quality"] == 70
    assert result["adjusted_scores"]["governance_risk"] == 65
    assert result["overall_score"] > 0
    assert "recommendation" in result


def test_run_what_if_no_improvement():
    result = run_what_if(HIGH_DIMS, {"data_quality": -50})
    assert result["adjusted_scores"]["data_quality"] == 35


def test_run_what_if_clamps():
    result = run_what_if(BASE_DIMS, {"data_quality": 200})
    assert result["adjusted_scores"]["data_quality"] == 100
    result = run_what_if(BASE_DIMS, {"data_quality": -200})
    assert result["adjusted_scores"]["data_quality"] == 0


def test_run_what_if_deltas():
    result = run_what_if(BASE_DIMS, {"data_quality": 20})
    assert abs(result["deltas"]["data_quality"] - 20) < 0.1


def test_sensitivity_analysis():
    result = sensitivity_analysis(BASE_DIMS)
    assert result["base_overall"] > 0
    assert len(result["impacts"]) == len(SCORING_DEFAULTS)
    assert result["highest_leverage"] is not None


def test_sensitivity_analysis_ranked():
    result = sensitivity_analysis(BASE_DIMS)
    assert len(result["ranked_dimensions"]) == len(SCORING_DEFAULTS)
    for i in range(len(result["ranked_dimensions"]) - 1):
        assert (
            result["ranked_dimensions"][i]["impact_per_10_pts"]
            >= result["ranked_dimensions"][i + 1]["impact_per_10_pts"]
        )


def test_sensitivity_weight_correlation():
    result = sensitivity_analysis(BASE_DIMS)
    for dim_info in result["ranked_dimensions"]:
        expected_impact = 10 * SCORING_DEFAULTS[dim_info["dim"]]["weight"]
        assert abs(dim_info["impact_per_10_pts"] - expected_impact) < 0.2


def test_what_if_presets():
    assert len(WHAT_IF_PRESETS) >= 5
    for preset in WHAT_IF_PRESETS:
        assert "name" in preset
        assert "adjustments" in preset


def test_run_what_if_preset():
    preset = WHAT_IF_PRESETS[0]
    result = run_what_if(BASE_DIMS, preset["adjustments"])
    assert result["overall_score"] > run_what_if(BASE_DIMS, {})["overall_score"]


def test_run_what_if_highest_preset():
    max_preset = WHAT_IF_PRESETS[-1]
    result = run_what_if(LOW_DIMS, max_preset["adjustments"])
    assert result["overall_score"] > result["adjusted_scores"]["integration_readiness"]
