REGULATORY_FRAMEWORKS = {
    "HIPAA": {
        "name": "Health Insurance Portability and Accountability Act",
        "industry": "Healthcare",
        "jurisdiction": "US",
        "key_requirements": [
            "Protected Health Information (PHI) must be encrypted at rest and in transit",
            "Access controls with unique user IDs and automatic logoff",
            "Audit logs of all PHI access for minimum 6 years",
            "Business Associate Agreements with all vendors",
            "Breach notification within 60 days",
            "Minimum necessary standard — only access PHI needed for the task",
        ],
        "automation_impact": {
            "data_quality_cap": 85,
            "governance_risk_penalty": 20,
            "approval_required": True,
            "audit_frequency": "Continuous",
            "human_override_mandatory": True,
        },
        "risk_if_automated": "HIPAA violations carry fines up to $1.5M per violation category per year. Automated systems that mishandle PHI can trigger cascading compliance failures.",
    },
    "GDPR": {
        "name": "General Data Protection Regulation",
        "industry": "Any (EU data subjects)",
        "jurisdiction": "EU/EEA",
        "key_requirements": [
            "Explicit consent for data processing",
            "Right to erasure ('right to be forgotten')",
            "Data portability in machine-readable format",
            "Data Protection Impact Assessment (DPIA) for high-risk processing",
            "72-hour breach notification",
            "Data Protection Officer appointment for certain organizations",
        ],
        "automation_impact": {
            "data_quality_cap": 80,
            "governance_risk_penalty": 25,
            "approval_required": True,
            "audit_frequency": "Continuous",
            "human_override_mandatory": False,
        },
        "risk_if_automated": "GDPR fines up to 4% of annual global turnover or EUR 20M, whichever is higher. Automated decisions without human review violate Article 22.",
    },
    "SOX": {
        "name": "Sarbanes-Oxley Act",
        "industry": "Finance/Public Companies",
        "jurisdiction": "US",
        "key_requirements": [
            "Internal controls over financial reporting (ICFR)",
            "Management and auditor assessment of controls",
            "Documentation and testing of all controls",
            "Segregation of duties",
            "Whistleblower protection",
            "Criminal penalties for certification of false statements",
        ],
        "automation_impact": {
            "data_quality_cap": 90,
            "governance_risk_penalty": 30,
            "approval_required": True,
            "audit_frequency": "Quarterly",
            "human_override_mandatory": True,
        },
        "risk_if_automated": "SOX violations carry criminal penalties including fines and imprisonment. Automated financial controls must have manual review and sign-off to be audit-compliant.",
    },
    "PCI_DSS": {
        "name": "Payment Card Industry Data Security Standard",
        "industry": "Finance/Retail",
        "jurisdiction": "Global",
        "key_requirements": [
            "Cardholder data must be encrypted",
            "Access to cardholder data restricted on a need-to-know basis",
            "Regular security testing and monitoring",
            "Vulnerability management program",
            "Strong access control measures",
            "Network segmentation",
        ],
        "automation_impact": {
            "data_quality_cap": 85,
            "governance_risk_penalty": 25,
            "approval_required": False,
            "audit_frequency": "Annual + Quarterly scans",
            "human_override_mandatory": False,
        },
        "risk_if_automated": "PCI non-compliance can result in fines of $5K-100K/month and loss of payment processing capability. Automated systems handling card data must be in scope for QSA audits.",
    },
    "SOC2": {
        "name": "Service Organization Control 2",
        "industry": "SaaS/Technology",
        "jurisdiction": "US (but globally recognized)",
        "key_requirements": [
            "Security controls (firewall, intrusion detection, access control)",
            "Availability controls (monitoring, incident response)",
            "Processing integrity (data validation, error handling)",
            "Confidentiality controls (encryption, access controls)",
            "Privacy controls (notice, choice, consent)",
        ],
        "automation_impact": {
            "data_quality_cap": 90,
            "governance_risk_penalty": 10,
            "approval_required": False,
            "audit_frequency": "Annual",
            "human_override_mandatory": False,
        },
        "risk_if_automated": "SOC2 is less punitive but automated controls must be documented and tested annually. Failed audits can lose enterprise customers.",
    },
    "CCPA": {
        "name": "California Consumer Privacy Act",
        "industry": "Any (California residents)",
        "jurisdiction": "US (California)",
        "key_requirements": [
            "Right to know what personal data is collected",
            "Right to delete personal data",
            "Right to opt-out of sale of personal data",
            "Non-discrimination for exercising rights",
            "Data inventory and mapping",
        ],
        "automation_impact": {
            "data_quality_cap": 80,
            "governance_risk_penalty": 15,
            "approval_required": False,
            "audit_frequency": "Annual",
            "human_override_mandatory": False,
        },
        "risk_if_automated": "CCPA fines of $2,500 per unintentional violation and $7,500 per intentional violation. Automated data deletion requests must be tracked and verified.",
    },
}


def get_applicable_regulations(industry, scores):
    applicable = []
    for key, framework in REGULATORY_FRAMEWORKS.items():
        if (
            framework["industry"] == industry
            or framework["industry"] == "Any (EU data subjects)"
        ):
            applicable.append(key)
        elif "Any" in framework["industry"] and scores.get("governance_risk", 50) < 70:
            applicable.append(key)

    if not applicable:
        default_matches = []
        for key, framework in REGULATORY_FRAMEWORKS.items():
            if "Any" in framework["industry"]:
                default_matches.append(key)
        applicable = default_matches

    return list(set(applicable))


def get_regulatory_impact(applicable_regs):
    impacts = []
    total_penalty = 0
    max_cap = 100
    approval_needed = False

    for reg_key in applicable_regs:
        framework = REGULATORY_FRAMEWORKS.get(reg_key)
        if not framework:
            continue
        impact = framework["automation_impact"]
        total_penalty += impact.get("governance_risk_penalty", 0)
        if impact.get("data_quality_cap", 100) < max_cap:
            max_cap = impact.get("data_quality_cap", 100)
        if impact.get("approval_required", False):
            approval_needed = True

        impacts.append(
            {
                "framework": framework["name"],
                "key": reg_key,
                "jurisdiction": framework["jurisdiction"],
                "governance_penalty": impact.get("governance_risk_penalty", 0),
                "data_quality_cap": impact.get("data_quality_cap", 100),
                "approval_required": impact.get("approval_required", False),
                "audit_frequency": impact.get("audit_frequency", "Unknown"),
                "human_override_mandatory": impact.get(
                    "human_override_mandatory", False
                ),
                "risk_statement": framework["risk_if_automated"],
            }
        )

    return {
        "applicable_regulations": [r["key"] for r in impacts],
        "regulation_details": impacts,
        "aggregate_governance_penalty": min(total_penalty, 60),
        "effective_data_quality_cap": max_cap,
        "approval_required": approval_needed,
        "human_override_mandatory": any(
            r.get("human_override_mandatory", False) for r in impacts
        ),
    }
