import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.sub_process import (
    SubProcess,
    decompose_workflow,
    compute_aggregate_scores,
    compute_aggregate_overall,
    find_decomposition_opportunities,
    get_dimensional_breakdown,
)
from engine.scorer import SCORING_DEFAULTS


GOOD_RESPONSES = {
    k: 85
    for k in [
        "data_completeness",
        "data_consistency",
        "data_structure",
        "data_duplicates",
        "data_reliability",
        "change_frequency",
        "workflow_variants",
        "standardization",
        "documentation",
        "regulatory_churn",
        "exception_frequency",
        "special_cases",
        "escalations",
        "judgment_calls",
        "edge_cases",
        "decision_points",
        "ambiguity",
        "reasoning_depth",
        "subjectivity",
        "policy_clarity",
        "api_availability",
        "software_stack",
        "data_accessibility",
        "auth_complexity",
        "vendor_support",
        "regulatory_exposure",
        "compliance_burden",
        "financial_impact",
        "legal_liability",
        "audit_requirements",
        "time_saved",
        "cost_reduction",
        "error_reduction",
        "revenue_impact",
        "scalability",
    ]
}

POOR_RESPONSES = {k: 15 for k in GOOD_RESPONSES}


def test_sub_process_creation():
    sp = SubProcess("Test", "A test sub-process", weight=1.5, responses=GOOD_RESPONSES)
    assert sp.name == "Test"
    assert sp.description == "A test sub-process"
    assert sp.weight == 1.5


def test_sub_process_to_from_dict():
    sp = SubProcess("Test", "Desc", weight=2.0, responses=GOOD_RESPONSES)
    d = sp.to_dict()
    sp2 = SubProcess.from_dict(d)
    assert sp2.name == "Test"
    assert sp2.weight == 2.0


def test_sub_process_get_dimension_scores():
    sp = SubProcess("Test", weight=1.0, responses=GOOD_RESPONSES)
    scores = sp.get_dimension_scores()
    for dim in SCORING_DEFAULTS:
        assert dim in scores
        assert 75 <= scores[dim] <= 100


def test_sub_process_get_overall_score():
    sp = SubProcess("Test", weight=1.0, responses=GOOD_RESPONSES)
    score = sp.get_overall_score()
    assert 75 <= score <= 100


def test_decompose_workflow_no_subprocesses():
    result = decompose_workflow(GOOD_RESPONSES, None)
    assert len(result) == 1
    assert result[0].name == "Main Process"


def test_decompose_workflow_with_subprocesses():
    sps = [
        SubProcess("Step 1", weight=1.0, responses=GOOD_RESPONSES).to_dict(),
        SubProcess("Step 2", weight=2.0, responses=POOR_RESPONSES).to_dict(),
    ]
    result = decompose_workflow(GOOD_RESPONSES, sps)
    assert len(result) == 2
    assert result[0].name == "Step 1"
    assert result[1].weight == 2.0


def test_compute_aggregate_scores():
    sps = [
        SubProcess("Good", weight=1.0, responses=GOOD_RESPONSES),
        SubProcess("Poor", weight=1.0, responses=POOR_RESPONSES),
    ]
    agg = compute_aggregate_scores(sps)
    for dim in SCORING_DEFAULTS:
        assert dim in agg
        assert 0 <= agg[dim] <= 100


def test_compute_aggregate_scores_weighted():
    sps = [
        SubProcess("Good", weight=3.0, responses=GOOD_RESPONSES),
        SubProcess("Poor", weight=1.0, responses=POOR_RESPONSES),
    ]
    agg = compute_aggregate_scores(sps)
    for dim in SCORING_DEFAULTS:
        assert agg[dim] >= 50


def test_compute_aggregate_overall():
    sps = [
        SubProcess("Good", weight=1.0, responses=GOOD_RESPONSES),
        SubProcess("Poor", weight=1.0, responses=POOR_RESPONSES),
    ]
    overall = compute_aggregate_overall(sps)
    assert 30 <= overall <= 70


def test_find_decomposition_opportunities():
    sps = [
        SubProcess("Ready", weight=1.0, responses=GOOD_RESPONSES),
        SubProcess("Not Ready", weight=1.0, responses=POOR_RESPONSES),
    ]
    opps = find_decomposition_opportunities(sps)
    assert len(opps) == 2
    ready_opp = next(o for o in opps if o["sub_process"] == "Ready")
    assert ready_opp["readiness"] == "Ready"


def test_get_dimensional_breakdown():
    sps = [
        SubProcess("A", weight=1.0, responses=GOOD_RESPONSES),
        SubProcess("B", weight=1.0, responses=POOR_RESPONSES),
    ]
    breakdown = get_dimensional_breakdown(sps)
    assert "A" in breakdown
    assert "B" in breakdown
