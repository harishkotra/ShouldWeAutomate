import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.remediation import (
    REMEDIATION_PLAYBOOKS,
    get_remediation_playbook,
    estimate_remediation_timeline,
)


DIM_SCORES = {
    "data_quality": 30,
    "process_stability": 55,
    "exception_rate": 75,
    "decision_complexity": 80,
    "integration_readiness": 25,
    "governance_risk": 45,
    "roi_potential": 60,
}


def test_playbooks_exist_for_all_dims():
    for dim_key in [
        "data_quality",
        "process_stability",
        "exception_rate",
        "decision_complexity",
        "integration_readiness",
        "governance_risk",
        "roi_potential",
    ]:
        assert dim_key in REMEDIATION_PLAYBOOKS, f"Missing playbook for {dim_key}"


def test_each_playbook_has_all_levels():
    for dim_key, playbook in REMEDIATION_PLAYBOOKS.items():
        for level in ["low", "mid", "high"]:
            assert level in playbook, f"{dim_key} missing level {level}"
            phases = playbook[level]
            for phase_key, phase in phases.items():
                assert "name" in phase
                assert "actions" in phase
                assert "effort" in phase
                assert "team" in phase
                assert len(phase["actions"]) >= 2


def test_get_remediation_playbook():
    playbook = get_remediation_playbook(DIM_SCORES)
    assert len(playbook) == len(DIM_SCORES)
    for dim_key in DIM_SCORES:
        assert dim_key in playbook
        assert "phases" in playbook[dim_key]
        assert len(playbook[dim_key]["phases"]) >= 1


def test_playbook_severity():
    playbook = get_remediation_playbook({"data_quality": 25})
    assert playbook["data_quality"]["severity"] == "Critical"

    playbook = get_remediation_playbook({"data_quality": 45})
    assert playbook["data_quality"]["severity"] == "High"

    playbook = get_remediation_playbook({"data_quality": 65})
    assert playbook["data_quality"]["severity"] == "Medium"

    playbook = get_remediation_playbook({"data_quality": 80})
    assert playbook["data_quality"]["severity"] == "Low"


def test_estimate_timeline():
    playbook = get_remediation_playbook(DIM_SCORES)
    timeline = estimate_remediation_timeline(playbook)
    assert "estimated_total_weeks" in timeline
    assert "estimated_months" in timeline
    assert "teams_involved" in timeline
    assert timeline["estimated_total_weeks"] > 0


def test_timeline_teams_involved():
    playbook = get_remediation_playbook(DIM_SCORES)
    timeline = estimate_remediation_timeline(playbook)
    assert len(timeline["teams_involved"]) >= 1


def test_low_score_has_more_phases():
    low_playbook = get_remediation_playbook({"data_quality": 20})
    high_playbook = get_remediation_playbook({"data_quality": 80})
    assert len(low_playbook["data_quality"]["phases"]) >= len(
        high_playbook["data_quality"]["phases"]
    )
