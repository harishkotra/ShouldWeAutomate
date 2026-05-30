import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.scorer import (
    compute_dimension_score,
    compute_overall_score,
    get_recommendation,
    SCORING_DEFAULTS,
)


SAMPLE_RESPONSES = {
    # Data quality: all 80s
    "data_completeness": 80,
    "data_consistency": 75,
    "data_structure": 90,
    "data_duplicates": 85,
    "data_reliability": 80,
    # Process stability
    "change_frequency": 70,
    "workflow_variants": 65,
    "standardization": 75,
    "documentation": 80,
    "regulatory_churn": 85,
    # Exception rate
    "exception_frequency": 70,
    "special_cases": 65,
    "escalations": 75,
    "judgment_calls": 80,
    "edge_cases": 70,
    # Decision complexity
    "decision_points": 75,
    "ambiguity": 80,
    "reasoning_depth": 85,
    "subjectivity": 80,
    "policy_clarity": 75,
    # Integration readiness
    "api_availability": 90,
    "software_stack": 85,
    "data_accessibility": 80,
    "auth_complexity": 75,
    "vendor_support": 85,
    # Governance risk
    "regulatory_exposure": 80,
    "compliance_burden": 75,
    "financial_impact": 70,
    "legal_liability": 75,
    "audit_requirements": 80,
    # ROI
    "time_saved": 85,
    "cost_reduction": 80,
    "error_reduction": 75,
    "revenue_impact": 70,
    "scalability": 90,
}

POOR_RESPONSES = {k: 15 for k in SAMPLE_RESPONSES}


def test_compute_dimension_score():
    score = compute_dimension_score(SAMPLE_RESPONSES, "data_quality")
    assert 75 <= score <= 90, f"Expected ~82, got {score}"


def test_compute_dimension_score_empty():
    score = compute_dimension_score({}, "data_quality")
    assert score == 50, f"Expected 50 for empty, got {score}"


def test_compute_dimension_score_partial():
    score = compute_dimension_score({"data_completeness": 100}, "data_quality")
    assert score == 100


def test_compute_overall_score():
    dim_scores = {
        "data_quality": 82,
        "process_stability": 75,
        "exception_rate": 72,
        "decision_complexity": 79,
        "integration_readiness": 83,
        "governance_risk": 76,
        "roi_potential": 80,
    }
    overall = compute_overall_score(dim_scores)
    assert 75 <= overall <= 85, f"Expected ~78, got {overall}"


def test_compute_overall_score_extremes():
    low_scores = {k: 0 for k in SCORING_DEFAULTS}
    assert compute_overall_score(low_scores) == 0

    high_scores = {k: 100 for k in SCORING_DEFAULTS}
    assert compute_overall_score(high_scores) == 100


def test_get_recommendation_do_not_automate():
    rec = get_recommendation(20)
    assert "DO NOT AUTOMATE" in rec["level"]


def test_get_recommendation_improve_process():
    rec = get_recommendation(40)
    assert "IMPROVE PROCESS FIRST" in rec["level"]


def test_get_recommendation_human_in_the_loop():
    rec = get_recommendation(60)
    assert "HUMAN-IN-THE-LOOP" in rec["level"]


def test_get_recommendation_ai_assisted():
    rec = get_recommendation(75)
    assert "AI ASSISTED" in rec["level"]


def test_get_recommendation_agent_ready():
    rec = get_recommendation(90)
    assert "AGENT AUTOMATION READY" in rec["level"]


def test_get_recommendation_boundaries():
    assert "IMPROVE PROCESS" in get_recommendation(30)["level"]
    assert "HUMAN-IN-THE-LOOP" in get_recommendation(50)["level"]
    assert "AI ASSISTED" in get_recommendation(70)["level"]
    assert "AGENT AUTOMATION" in get_recommendation(85)["level"]


def test_dimension_weights_sum_to_one():
    total_weight = sum(dim["weight"] for dim in SCORING_DEFAULTS.values())
    assert abs(total_weight - 1.0) < 0.001, f"Weights sum to {total_weight}"


def test_each_dimension_has_5_questions():
    for dim_key, dim in SCORING_DEFAULTS.items():
        assert len(dim["questions"]) == 5, (
            f"{dim_key} has {len(dim['questions'])} questions"
        )


def test_all_question_ids_unique():
    ids = []
    for dim in SCORING_DEFAULTS.values():
        for q in dim["questions"]:
            ids.append(q["id"])
    assert len(ids) == len(set(ids)), "Duplicate question IDs found"
