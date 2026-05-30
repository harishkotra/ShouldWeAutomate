import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.explainer import explain_scores, _verdict, _improvement_tip


SCORES = {
    "data_quality": 82,
    "process_stability": 45,
    "exception_rate": 60,
    "decision_complexity": 55,
    "integration_readiness": 35,
    "governance_risk": 25,
    "roi_potential": 70,
}

RESPONSES = {
    "data_completeness": 90,
    "data_consistency": 85,
    "data_structure": 80,
    "data_duplicates": 75,
    "data_reliability": 80,
    "change_frequency": 40,
    "workflow_variants": 45,
    "standardization": 50,
    "documentation": 35,
    "regulatory_churn": 55,
    "exception_frequency": 65,
    "special_cases": 55,
    "escalations": 70,
    "judgment_calls": 45,
    "edge_cases": 65,
    "decision_points": 50,
    "ambiguity": 55,
    "reasoning_depth": 60,
    "subjectivity": 50,
    "policy_clarity": 60,
    "api_availability": 30,
    "software_stack": 35,
    "data_accessibility": 40,
    "auth_complexity": 30,
    "vendor_support": 40,
    "regulatory_exposure": 20,
    "compliance_burden": 25,
    "financial_impact": 30,
    "legal_liability": 20,
    "audit_requirements": 30,
    "time_saved": 75,
    "cost_reduction": 70,
    "error_reduction": 65,
    "revenue_impact": 60,
    "scalability": 80,
}


def test_explain_scores_basic():
    result = explain_scores(SCORES, RESPONSES)
    assert "explanations" in result
    assert "suggestions" in result
    assert "score_summary" in result
    assert len(result["explanations"]) == 7


def test_explain_scores_pulling_up_down():
    result = explain_scores(SCORES, RESPONSES)
    for dim_key, exp in result["explanations"].items():
        assert "pulling_up" in exp
        assert "pulling_down" in exp
        assert "verdict" in exp
        assert "improvement_tip" in exp
        assert "weighted_contribution" in exp


def test_explain_scores_suggestions_priority():
    result = explain_scores(SCORES, RESPONSES)
    if result["suggestions"]:
        for i in range(len(result["suggestions"]) - 1):
            assert (
                result["suggestions"][i]["potential_gain"]
                >= result["suggestions"][i + 1]["potential_gain"]
            )


def test_explain_scores_strongest_weakest():
    result = explain_scores(SCORES, RESPONSES)
    summary = result["score_summary"]
    assert len(summary["strongest_dimensions"]) == 3
    assert len(summary["weakest_dimensions"]) == 3
    assert (
        summary["strongest_dimensions"][0]["score"]
        >= summary["strongest_dimensions"][-1]["score"]
    )
    assert (
        summary["weakest_dimensions"][0]["score"]
        <= summary["weakest_dimensions"][-1]["score"]
    )


def test_verdict():
    assert "Excellent" in _verdict(90, "data_quality")
    assert "Adequate" in _verdict(65, "data_quality")
    assert "Concerning" in _verdict(45, "data_quality")
    assert "Critical" in _verdict(20, "data_quality")


def test_improvement_tip_exists():
    for dim_key in [
        "data_quality",
        "process_stability",
        "exception_rate",
        "decision_complexity",
        "integration_readiness",
        "governance_risk",
        "roi_potential",
    ]:
        tip = _improvement_tip(dim_key, 30)
        assert len(tip) > 10
        tip = _improvement_tip(dim_key, 55)
        assert len(tip) > 10
        tip = _improvement_tip(dim_key, 80)
        assert len(tip) > 10


def test_score_summary():
    result = explain_scores(SCORES, RESPONSES)
    summary = result["score_summary"]
    assert summary["spread"] >= 0
    assert summary["spread"] <= 100
