import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.analyzer import (
    analyze_workflow,
    identify_risks,
    analyze_failure_modes,
    estimate_roi,
    estimate_implementation,
    suggest_architecture,
    compute_confidence,
    find_red_flags,
    generate_next_steps,
)


HIGH_RESPONSES = {
    "data_completeness": 95,
    "data_consistency": 90,
    "data_structure": 95,
    "data_duplicates": 90,
    "data_reliability": 95,
    "change_frequency": 90,
    "workflow_variants": 85,
    "standardization": 90,
    "documentation": 95,
    "regulatory_churn": 90,
    "exception_frequency": 90,
    "special_cases": 85,
    "escalations": 90,
    "judgment_calls": 85,
    "edge_cases": 88,
    "decision_points": 85,
    "ambiguity": 90,
    "reasoning_depth": 85,
    "subjectivity": 88,
    "policy_clarity": 90,
    "api_availability": 95,
    "software_stack": 90,
    "data_accessibility": 90,
    "auth_complexity": 85,
    "vendor_support": 90,
    "regulatory_exposure": 85,
    "compliance_burden": 80,
    "financial_impact": 85,
    "legal_liability": 80,
    "audit_requirements": 85,
    "time_saved": 90,
    "cost_reduction": 85,
    "error_reduction": 80,
    "revenue_impact": 75,
    "scalability": 95,
}

LOW_RESPONSES = {k: 10 for k in HIGH_RESPONSES}


def test_analyze_workflow_high_score():
    result = analyze_workflow(HIGH_RESPONSES)
    assert result["overall_score"] >= 80
    assert "AGENT AUTOMATION" in result["recommendation"]["level"]
    assert len(result["top_risks"]) == 0
    assert len(result["failure_modes"]) >= 1


def test_analyze_workflow_low_score():
    result = analyze_workflow(LOW_RESPONSES)
    assert result["overall_score"] <= 20
    assert "DO NOT AUTOMATE" in result["recommendation"]["level"]
    assert len(result["top_risks"]) >= 5
    assert len(result["red_flags"]) >= 3


def test_analyze_workflow_returns_all_keys():
    result = analyze_workflow(HIGH_RESPONSES)
    expected_keys = [
        "dimension_scores",
        "radar_values",
        "overall_score",
        "recommendation",
        "top_risks",
        "failure_modes",
        "roi_estimate",
        "implementation",
        "architecture",
        "confidence",
        "red_flags",
        "next_steps",
    ]
    for key in expected_keys:
        assert key in result, f"Missing key: {key}"


def test_identify_risks_high_scores():
    dim_scores = {
        k: 80
        for k in [
            "data_quality",
            "process_stability",
            "exception_rate",
            "decision_complexity",
            "integration_readiness",
            "governance_risk",
            "roi_potential",
        ]
    }
    risks = identify_risks(dim_scores, HIGH_RESPONSES)
    assert len(risks) == 0


def test_identify_risks_low_scores():
    dim_scores = {
        k: 20
        for k in [
            "data_quality",
            "process_stability",
            "exception_rate",
            "decision_complexity",
            "integration_readiness",
            "governance_risk",
            "roi_potential",
        ]
    }
    risks = identify_risks(dim_scores, LOW_RESPONSES)
    assert len(risks) >= 5


def test_analyze_failure_modes():
    dim_scores = {
        "data_quality": 25,
        "integration_readiness": 30,
        "exception_rate": 20,
        "governance_risk": 25,
        "decision_complexity": 20,
        "process_stability": 20,
    }
    modes = analyze_failure_modes(dim_scores, {})
    assert len(modes) >= 4
    severities = [m["severity"] for m in modes]
    assert "Critical" in severities or "High" in severities


def test_estimate_roi_negative():
    result = estimate_roi({"roi_potential": 15})
    assert "Negative" in result["category"]


def test_estimate_roi_exceptional():
    result = estimate_roi({"roi_potential": 90})
    assert "Exceptional" in result["category"]


def test_estimate_implementation():
    impl = estimate_implementation(
        90,
        {k: 80 for k in ["data_quality", "integration_readiness", "governance_risk"]},
    )
    assert impl["effort"] == "Small to Medium"


def test_estimate_implementation_hard():
    impl = estimate_implementation(
        20, {"data_quality": 20, "integration_readiness": 20, "governance_risk": 20}
    )
    assert impl["effort"] == "Enterprise"


def test_suggest_architecture():
    rec = {"level": "AGENT AUTOMATION READY"}
    arch = suggest_architecture(90, rec)
    assert "Multi-Agent" in arch["type"]


def test_suggest_architecture_none():
    rec = {"level": "DO NOT AUTOMATE"}
    arch = suggest_architecture(10, rec)
    assert arch["type"] == "None"


def test_compute_confidence():
    dim_scores = {
        k: 85
        for k in [
            "data_quality",
            "process_stability",
            "exception_rate",
            "decision_complexity",
            "integration_readiness",
            "governance_risk",
            "roi_potential",
        ]
    }
    conf = compute_confidence(dim_scores)
    assert 50 <= conf <= 95


def test_find_red_flags():
    dim_scores = {
        "data_quality": 20,
        "governance_risk": 20,
        "decision_complexity": 20,
        "exception_rate": 15,
        "roi_potential": 15,
        "process_stability": 15,
        "integration_readiness": 50,
    }
    flags = find_red_flags(dim_scores)
    assert len(flags) >= 3


def test_find_red_flags_clean():
    dim_scores = {
        k: 80
        for k in [
            "data_quality",
            "process_stability",
            "exception_rate",
            "decision_complexity",
            "integration_readiness",
            "governance_risk",
            "roi_potential",
        ]
    }
    flags = find_red_flags(dim_scores)
    assert len(flags) == 0


def test_generate_next_steps():
    dim_scores = {
        "data_quality": 30,
        "process_stability": 40,
        "exception_rate": 60,
        "decision_complexity": 70,
        "integration_readiness": 35,
        "governance_risk": 45,
        "roi_potential": 30,
    }
    steps = generate_next_steps(45, dim_scores)
    assert len(steps) >= 4


def test_generate_next_steps_ready():
    dim_scores = {
        k: 80
        for k in [
            "data_quality",
            "process_stability",
            "exception_rate",
            "decision_complexity",
            "integration_readiness",
            "governance_risk",
            "roi_potential",
        ]
    }
    steps = generate_next_steps(90, dim_scores)
    assert len(steps) == 1
    assert "Proceed" in steps[0]
