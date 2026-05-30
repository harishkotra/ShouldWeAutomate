import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.regulations import (
    REGULATORY_FRAMEWORKS,
    get_applicable_regulations,
    get_regulatory_impact,
)


def test_all_frameworks_have_required_keys():
    for key, framework in REGULATORY_FRAMEWORKS.items():
        assert "name" in framework
        assert "industry" in framework
        assert "jurisdiction" in framework
        assert "key_requirements" in framework
        assert "automation_impact" in framework
        assert "risk_if_automated" in framework
        assert len(framework["key_requirements"]) >= 3


def test_all_automation_impacts_have_keys():
    for key, framework in REGULATORY_FRAMEWORKS.items():
        impact = framework["automation_impact"]
        for field in [
            "data_quality_cap",
            "governance_risk_penalty",
            "approval_required",
            "audit_frequency",
            "human_override_mandatory",
        ]:
            assert field in impact, f"{key} missing {field}"


def test_get_applicable_regulations_healthcare():
    regs = get_applicable_regulations("Healthcare", {"governance_risk": 30})
    assert "HIPAA" in regs


def test_get_applicable_regulations_banking():
    regs = get_applicable_regulations("Banking", {"governance_risk": 50})
    assert "SOX" in regs or "PCI_DSS" in regs or "GDPR" in regs or "CCPA" in regs


def test_get_applicable_regulations_returns_list():
    regs = get_applicable_regulations("Unknown", {"governance_risk": 50})
    assert isinstance(regs, list)
    assert len(regs) >= 1


def test_get_regulatory_impact_basic():
    regs = get_applicable_regulations("Healthcare", {"governance_risk": 30})
    impact = get_regulatory_impact(regs)
    assert "applicable_regulations" in impact
    assert "regulation_details" in impact
    assert "aggregate_governance_penalty" in impact
    assert "effective_data_quality_cap" in impact
    assert impact["aggregate_governance_penalty"] > 0


def test_get_regulatory_impact_approval():
    regs = get_applicable_regulations("Healthcare", {"governance_risk": 30})
    impact = get_regulatory_impact(regs)
    if "HIPAA" in regs:
        assert impact["approval_required"] == True


def test_get_regulatory_impact_details():
    impact = get_regulatory_impact(["HIPAA", "GDPR"])
    assert len(impact["regulation_details"]) == 2
    for detail in impact["regulation_details"]:
        assert "framework" in detail
        assert "governance_penalty" in detail
        assert "risk_statement" in detail
