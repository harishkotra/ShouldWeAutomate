SCORING_DEFAULTS = {
    "data_quality": {
        "label": "Data Quality",
        "weight": 0.20,
        "questions": [
            {
                "id": "data_completeness",
                "text": "How complete is your data? (0 = mostly missing, 100 = fully complete)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "data_consistency",
                "text": "How consistent is data format across sources?",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "data_structure",
                "text": "How structured is your data? (0 = pure unstructured, 100 = fully structured)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "data_duplicates",
                "text": "How frequent are duplicate records? (0 = rampant, 100 = never)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "data_reliability",
                "text": "How reliable are your data sources? (0 = unreliable, 100 = highly reliable)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
        ],
    },
    "process_stability": {
        "label": "Process Stability",
        "weight": 0.20,
        "questions": [
            {
                "id": "change_frequency",
                "text": "How often does this process change? (0 = constantly, 100 = never changes)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "workflow_variants",
                "text": "How many workflow variants exist? (0 = infinite, 100 = one standard way)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "standardization",
                "text": "How standardized is the process? (0 = ad-hoc, 100 = fully documented)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "documentation",
                "text": "Are procedures well-documented? (0 = tribal knowledge, 100 = fully documented)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "regulatory_churn",
                "text": "How frequently do regulations change? (0 = constant churn, 100 = stable)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
        ],
    },
    "exception_rate": {
        "label": "Exception Rate",
        "weight": 0.15,
        "questions": [
            {
                "id": "exception_frequency",
                "text": "What % of cases need human intervention? (0 = 100% need help, 100 = 0% need help)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "special_cases",
                "text": "How many special case categories exist? (0 = infinite, 100 = none)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "escalations",
                "text": "How often do escalations occur? (0 = constant, 100 = never)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "judgment_calls",
                "text": "How much subjective judgment is required? (0 = completely subjective, 100 = fully objective)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "edge_cases",
                "text": "How many edge conditions exist? (0 = infinite edges, 100 = well-defined)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
        ],
    },
    "decision_complexity": {
        "label": "Decision Complexity",
        "weight": 0.15,
        "questions": [
            {
                "id": "decision_points",
                "text": "How many decision points? (0 = infinite branching, 100 = linear)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "ambiguity",
                "text": "How ambiguous are the decisions? (0 = pure ambiguity, 100 = crystal clear)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "reasoning_depth",
                "text": "How deep is the reasoning required? (0 = PhD-level, 100 = simple rules)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "subjectivity",
                "text": "How subjective are the judgments? (0 = pure opinion, 100 = pure math)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "policy_clarity",
                "text": "How clear are policies/rules? (0 = unwritten, 100 = exhaustive)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
        ],
    },
    "integration_readiness": {
        "label": "Tool Integration",
        "weight": 0.10,
        "questions": [
            {
                "id": "api_availability",
                "text": "How available are APIs? (0 = no APIs, 100 = everything has APIs)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "software_stack",
                "text": "How compatible is existing software? (0 = mainframe, 100 = modern stack)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "data_accessibility",
                "text": "How accessible is the data? (0 = locked down, 100 = easily accessible)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "auth_complexity",
                "text": "How complex is authentication? (0 = nightmare, 100 = seamless SSO)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "vendor_support",
                "text": "How good is vendor support? (0 = hostile, 100 = excellent)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
        ],
    },
    "governance_risk": {
        "label": "Governance Risk",
        "weight": 0.10,
        "questions": [
            {
                "id": "regulatory_exposure",
                "text": "How much regulatory exposure? (0 = extreme, 100 = none)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "compliance_burden",
                "text": "How burdensome is compliance? (0 = unbearable, 100 = trivial)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "financial_impact",
                "text": "What's the financial impact of errors? (0 = catastrophic, 100 = negligible)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "legal_liability",
                "text": "How much legal liability? (0 = lawsuit magnet, 100 = no liability)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "audit_requirements",
                "text": "How demanding are audit requirements? (0 = forensic, 100 = minimal)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
        ],
    },
    "roi_potential": {
        "label": "ROI Potential",
        "weight": 0.10,
        "questions": [
            {
                "id": "time_saved",
                "text": "How much time could be saved? (0 = none, 100 = massive)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "cost_reduction",
                "text": "How much cost could be reduced? (0 = none, 100 = massive)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "error_reduction",
                "text": "How much could errors be reduced? (0 = none, 100 = massive)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "revenue_impact",
                "text": "What's the revenue impact? (0 = none, 100 = transformative)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
            {
                "id": "scalability",
                "text": "How much scalability gain? (0 = none, 100 = 10x)",
                "min": 0,
                "max": 100,
                "default": 50,
            },
        ],
    },
}


def compute_dimension_score(responses, dimension):
    questions = SCORING_DEFAULTS[dimension]["questions"]
    scores = []
    for q in questions:
        val = responses.get(q["id"])
        if val is not None:
            scores.append(float(val))
    if not scores:
        return 50
    return sum(scores) / len(scores)


def compute_overall_score(dimension_scores):
    weights = {
        "data_quality": 0.20,
        "process_stability": 0.20,
        "exception_rate": 0.15,
        "decision_complexity": 0.15,
        "integration_readiness": 0.10,
        "governance_risk": 0.10,
        "roi_potential": 0.10,
    }
    score = 0
    for dim, weight in weights.items():
        score += dimension_scores.get(dim, 50) * weight
    return round(score, 1)


def get_recommendation(overall_score):
    if overall_score < 30:
        return {
            "level": "DO NOT AUTOMATE",
            "color": "#dc3545",
            "reason": "Workflow unsuitable for automation. Foundational operational problems must be resolved first.",
            "architecture": "No automation recommended",
        }
    elif overall_score < 50:
        return {
            "level": "IMPROVE PROCESS FIRST",
            "color": "#fd7e14",
            "reason": "Operational problems must be solved before automation. Focus on data quality, process standardization, and exception reduction.",
            "architecture": "Process improvement initiative",
        }
    elif overall_score < 70:
        return {
            "level": "HUMAN-IN-THE-LOOP AI",
            "color": "#ffc107",
            "reason": "Partial automation with human oversight is appropriate. Use AI to assist, not replace, human decision-makers.",
            "architecture": "Human-in-the-loop AI assistant",
        }
    elif overall_score < 85:
        return {
            "level": "AI ASSISTED AUTOMATION",
            "color": "#20c997",
            "reason": "Strong automation candidate. AI can handle most cases with human exception handling.",
            "architecture": "AI-assisted workflow with human escalation",
        }
    else:
        return {
            "level": "AGENT AUTOMATION READY",
            "color": "#0d6efd",
            "reason": "Suitable for autonomous AI agent workflows. Minimal human oversight required.",
            "architecture": "Autonomous multi-agent system",
        }


RECOMMENDATIONS_BY_SCORE = [
    (0, "DO NOT AUTOMATE"),
    (30, "IMPROVE PROCESS FIRST"),
    (50, "HUMAN-IN-THE-LOOP AI"),
    (70, "AI ASSISTED AUTOMATION"),
    (85, "AGENT AUTOMATION READY"),
]
