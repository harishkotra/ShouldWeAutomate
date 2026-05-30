from engine.scorer import (
    compute_dimension_score,
    compute_overall_score,
    get_recommendation,
    SCORING_DEFAULTS,
)
from engine.sub_process import (
    SubProcess,
    decompose_workflow,
    compute_aggregate_scores,
    compute_aggregate_overall,
    find_decomposition_opportunities,
    get_dimensional_breakdown,
)
from engine.explainer import explain_scores
from engine.remediation import get_remediation_playbook, estimate_remediation_timeline
from engine.regulations import get_applicable_regulations, get_regulatory_impact
from engine.similarity import find_similar_in_benchmark


def analyze_workflow(responses):
    use_llm = responses.get("use_llm", False) and _llm_available()
    sub_processes_data = responses.get("sub_processes")
    industry = responses.get("industry", "")

    sub_processes = decompose_workflow(responses, sub_processes_data)

    if len(sub_processes) > 1:
        dimension_scores = compute_aggregate_scores(sub_processes)
        overall = compute_aggregate_overall(sub_processes)
    else:
        dimension_scores = {}
        for dim in SCORING_DEFAULTS:
            score = compute_dimension_score(responses, dim)
            dimension_scores[dim] = round(score, 1)
        overall = compute_overall_score(dimension_scores)

    recommendation = get_recommendation(overall)

    radar_values = {
        SCORING_DEFAULTS[dim]["label"]: dimension_scores.get(dim, 50)
        for dim in SCORING_DEFAULTS
    }

    top_risks = identify_risks(dimension_scores, responses)
    failure_modes = analyze_failure_modes(dimension_scores, responses)
    roi = estimate_roi(dimension_scores)

    params = responses.get("roi_params", {})
    if params:
        from engine.roi_calculator import calculate_roi, classify_roi

        roi_detail = calculate_roi(params)
        roi_classification = classify_roi(roi_detail)
        roi["quantitative"] = roi_detail
        roi["quantitative_classification"] = roi_classification

    impl = estimate_implementation(overall, dimension_scores)
    arch = suggest_architecture(overall, recommendation)

    explanation = explain_scores(dimension_scores, responses)
    remediation = get_remediation_playbook(dimension_scores)
    remediation_timeline = estimate_remediation_timeline(remediation)

    applicable_regs = get_applicable_regulations(industry, dimension_scores)
    regulatory_impact = get_regulatory_impact(applicable_regs)

    result = {
        "dimension_scores": dimension_scores,
        "radar_values": radar_values,
        "overall_score": overall,
        "recommendation": recommendation,
        "top_risks": top_risks,
        "failure_modes": failure_modes,
        "roi_estimate": roi,
        "implementation": impl,
        "architecture": arch,
        "confidence": compute_confidence(dimension_scores),
        "red_flags": find_red_flags(dimension_scores),
        "next_steps": generate_next_steps(overall, dimension_scores),
        "explanation": explanation,
        "remediation": {
            "playbook": {k: v for k, v in remediation.items()},
            "timeline": remediation_timeline,
        },
        "regulatory": regulatory_impact,
        "sub_processes": {
            "count": len(sub_processes),
            "decomposition": get_dimensional_breakdown(sub_processes),
            "opportunities": find_decomposition_opportunities(sub_processes),
        },
        "llm_enriched": False,
        "llm_summary": None,
        "llm_risks": None,
    }

    if use_llm:
        from engine.llm import generate_contextual_risks, generate_executive_summary

        workflow_context = {
            "workflow_name": responses.get("workflow_name", ""),
            "industry": industry,
            "description": responses.get("description", ""),
            "dimension_scores": dimension_scores,
            "overall_score": overall,
            "recommendation": recommendation["level"],
            "sub_processes": get_dimensional_breakdown(sub_processes),
            "failure_modes": failure_modes,
        }
        llm_risks = generate_contextual_risks(workflow_context)
        if llm_risks:
            result["llm_risks"] = llm_risks
        llm_summary = generate_executive_summary(result)
        if llm_summary:
            result["llm_summary"] = llm_summary
        result["llm_enriched"] = bool(llm_risks or llm_summary)

    benchmark_similar = find_similar_in_benchmark(
        dimension_scores, industry=industry, limit=5
    )
    if benchmark_similar:
        result["benchmark_similar"] = benchmark_similar

    return result


def _llm_available():
    from engine.llm import LLM_CONFIG

    return LLM_CONFIG["enabled"]


def identify_risks(dim_scores, responses):
    risks = []
    if dim_scores.get("data_quality", 50) < 40:
        risks.append(
            {
                "risk": "Poor data quality will cause automation to fail or produce unreliable outputs",
                "severity": "High",
                "mitigation": "Invest in data cleansing pipelines before any automation effort",
            }
        )
    if dim_scores.get("governance_risk", 50) < 40:
        risks.append(
            {
                "risk": "High governance exposure - automated errors could trigger regulatory penalties or lawsuits",
                "severity": "Critical",
                "mitigation": "Implement mandatory human approval gates for all decisions with regulatory impact",
            }
        )
    if dim_scores.get("exception_rate", 50) < 30:
        risks.append(
            {
                "risk": "Exception-heavy process - automation will only cover a minority of cases",
                "severity": "High",
                "mitigation": "Focus automation on the most standardized subset of cases first",
            }
        )
    if dim_scores.get("integration_readiness", 50) < 30:
        risks.append(
            {
                "risk": "Poor tool integration will inflate implementation costs 3-5x",
                "severity": "Medium",
                "mitigation": "Evaluate middleware or API gateway solutions before building automation",
            }
        )
    if dim_scores.get("decision_complexity", 50) < 30:
        risks.append(
            {
                "risk": "High decision complexity means AI will produce plausible-sounding but wrong outputs",
                "severity": "High",
                "mitigation": "Restrict AI to information gathering; keep all decisions human-controlled",
            }
        )
    if dim_scores.get("process_stability", 50) < 30:
        risks.append(
            {
                "risk": "Process changes too frequently - automation will require constant maintenance",
                "severity": "High",
                "mitigation": "Stabilize and document the process before automating",
            }
        )
    if dim_scores.get("roi_potential", 50) < 30:
        risks.append(
            {
                "risk": "ROI is unlikely to justify the automation investment",
                "severity": "Medium",
                "mitigation": "Re-evaluate: consider no automation or lightweight RPA for a single sub-task",
            }
        )
    return risks


def analyze_failure_modes(dim_scores, responses):
    candidates = []
    if dim_scores.get("data_quality", 50) < 50:
        candidates.append(
            {
                "mode": "Hallucination / data fabrication",
                "description": "AI may invent missing data points or hallucinate relationships in incomplete datasets",
                "likelihood": "High" if dim_scores["data_quality"] < 30 else "Medium",
                "severity": "High",
                "detectability": "Medium",
            }
        )
        candidates.append(
            {
                "mode": "Data quality cascade failure",
                "description": "Bad input data propagates through automated pipelines, corrupting downstream outputs",
                "likelihood": "High",
                "severity": "Critical",
                "detectability": "Low",
            }
        )
    if dim_scores.get("integration_readiness", 50) < 40:
        candidates.append(
            {
                "mode": "Tool / API integration failure",
                "description": "APIs may change without notice, credentials expire, or rate limits throttle automation",
                "likelihood": "High",
                "severity": "High",
                "detectability": "Medium",
            }
        )
    if dim_scores.get("exception_rate", 50) < 40:
        candidates.append(
            {
                "mode": "Approval bottleneck",
                "description": "Too many exceptions require human approval, negating automation benefits",
                "likelihood": "High",
                "severity": "Medium",
                "detectability": "High",
            }
        )
    if dim_scores.get("governance_risk", 50) < 40:
        candidates.append(
            {
                "mode": "Governance / compliance violation",
                "description": "Automated actions may inadvertently violate regulatory requirements",
                "likelihood": "Medium",
                "severity": "Critical",
                "detectability": "Low",
            }
        )
    if dim_scores.get("decision_complexity", 50) < 30:
        candidates.append(
            {
                "mode": "Unexpected edge case failure",
                "description": "Novel scenarios not covered by training data cause unpredictable behavior",
                "likelihood": "High",
                "severity": "High",
                "detectability": "Low",
            }
        )
    if dim_scores.get("process_stability", 50) < 35:
        candidates.append(
            {
                "mode": "Process drift obsolescence",
                "description": "Frequent process changes make automation logic obsolete within weeks",
                "likelihood": "High",
                "severity": "Medium",
                "detectability": "Medium",
            }
        )
    if not candidates:
        candidates.append(
            {
                "mode": "Over-automation creep",
                "description": "Tendency to expand automation scope beyond safe boundaries over time",
                "likelihood": "Medium",
                "severity": "Medium",
                "detectability": "Medium",
            }
        )
    sev_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    return sorted(candidates, key=lambda x: sev_order.get(x["severity"], 99))


def estimate_roi(dim_scores):
    roi_score = dim_scores.get("roi_potential", 50)
    if roi_score < 25:
        return {
            "category": "Negative ROI",
            "description": "Automation costs will exceed benefits. Do not proceed.",
            "time_saved": "Minimal",
            "cost_reduction": "0-10%",
            "error_reduction": "Unlikely",
            "payback_period": "Never",
        }
    elif roi_score < 50:
        return {
            "category": "Modest ROI",
            "description": "Some gains possible but payback period is long. Consider targeted partial automation.",
            "time_saved": "5-15%",
            "cost_reduction": "10-20%",
            "error_reduction": "Low",
            "payback_period": "18-36 months",
        }
    elif roi_score < 75:
        return {
            "category": "Good ROI",
            "description": "Solid returns achievable with focused implementation. Prioritize high-value sub-processes.",
            "time_saved": "20-40%",
            "cost_reduction": "20-40%",
            "error_reduction": "Moderate",
            "payback_period": "6-18 months",
        }
    else:
        return {
            "category": "Exceptional ROI",
            "description": "Strong automation candidate with rapid payback. High strategic value.",
            "time_saved": "50-80%",
            "cost_reduction": "40-70%",
            "error_reduction": "Significant",
            "payback_period": "3-9 months",
        }


def estimate_implementation(overall, dim_scores):
    complex_factors = sum(
        1
        for dim in ["data_quality", "integration_readiness", "governance_risk"]
        if dim_scores.get(dim, 50) < 40
    )
    if overall < 30 or complex_factors >= 3:
        effort, timeline = "Enterprise", "12-24+ months"
    elif overall < 50 or complex_factors >= 2:
        effort, timeline = "Large", "6-12 months"
    elif overall < 70:
        effort, timeline = "Medium", "2-6 months"
    else:
        effort, timeline = "Small to Medium", "1-3 months"
    if dim_scores.get("integration_readiness", 50) > 70 and overall > 60:
        maintenance = "Low ($5-15K/year)"
    elif overall > 70:
        maintenance = "Medium ($15-40K/year)"
    else:
        maintenance = "High ($40-100K+/year)"
    if overall > 80:
        oversight = "Minimal - periodic audit"
    elif overall > 60:
        oversight = "Moderate - daily supervision"
    elif overall > 40:
        oversight = "High - dedicated human operator"
    else:
        oversight = "Full-time human execution. Automation not recommended."
    return {
        "effort": effort,
        "timeline": timeline,
        "maintenance_cost": maintenance,
        "human_oversight": oversight,
    }


def suggest_architecture(overall, recommendation):
    level = recommendation["level"]
    if level == "DO NOT AUTOMATE":
        return {
            "type": "None",
            "description": "Process requires fundamental improvement before any automation is viable",
            "components": [],
        }
    elif level == "IMPROVE PROCESS FIRST":
        return {
            "type": "Process Improvement",
            "description": "Standardize, document, and clean data before considering automation",
            "components": [
                "Process mapping",
                "Data cleansing pipeline",
                "Documentation overhaul",
            ],
        }
    elif level == "HUMAN-IN-THE-LOOP AI":
        return {
            "type": "LLM Assistant + Human Approval",
            "description": "AI generates recommendations; humans make final decisions",
            "components": [
                "LLM for analysis/summary",
                "Human review dashboard",
                "Escalation queue",
                "Audit logging",
            ],
        }
    elif level == "AI ASSISTED AUTOMATION":
        return {
            "type": "AI-Assisted Workflow Engine",
            "description": "AI handles routine cases; exceptions routed to humans",
            "components": [
                "Workflow engine",
                "LLM for decision support",
                "RPA for data entry",
                "Human exception handler",
                "Monitoring dashboard",
            ],
        }
    else:
        return {
            "type": "Multi-Agent System",
            "description": "Autonomous AI agents orchestrate end-to-end with minimal oversight",
            "components": [
                "Orchestrator agent",
                "Specialized sub-agents",
                "Knowledge base",
                "Monitoring + alerting",
                "Human override console",
            ],
        }


def compute_confidence(dim_scores):
    scores = list(dim_scores.values())
    variance = sum((s - 50) ** 2 for s in scores) / len(scores)
    return round(min(95, 50 + variance / 25), 1)


def find_red_flags(dim_scores):
    flags = []
    if dim_scores.get("governance_risk", 50) < 30:
        flags.append(
            "HIGH GOVERNANCE RISK - Autonomous agents could create legal liability"
        )
    if dim_scores.get("data_quality", 50) < 25:
        flags.append("CRITICAL DATA QUALITY - Automation will amplify garbage data")
    if (
        dim_scores.get("decision_complexity", 50) < 25
        and dim_scores.get("governance_risk", 50) < 50
    ):
        flags.append(
            "COMPLEX DECISIONS + GOVERNANCE RISK - Dangerous combination for AI autonomy"
        )
    if dim_scores.get("exception_rate", 50) < 20:
        flags.append("EXCEPTIONS DOMINATE - Process is not ready for any automation")
    if dim_scores.get("roi_potential", 50) < 20:
        flags.append("NEGATIVE ROI - Resources better spent elsewhere")
    if dim_scores.get("process_stability", 50) < 20:
        flags.append("CHURNING PROCESS - Automation will require constant rework")
    return flags


def generate_next_steps(overall, dim_scores):
    steps = []
    if dim_scores.get("data_quality", 50) < 50:
        steps.append("Implement data quality monitoring and cleansing pipeline")
    if dim_scores.get("process_stability", 50) < 50:
        steps.append("Document and standardize the process workflow")
    if dim_scores.get("exception_rate", 50) < 50:
        steps.append("Analyze exception patterns to identify root causes")
    if dim_scores.get("integration_readiness", 50) < 50:
        steps.append("Audit existing tool APIs and integration capabilities")
    if dim_scores.get("governance_risk", 50) < 50:
        steps.append("Consult compliance team to define automation guardrails")
    if dim_scores.get("decision_complexity", 50) < 50:
        steps.append("Map decision trees and identify rules vs. judgment calls")
    if dim_scores.get("roi_potential", 50) < 50:
        steps.append("Build detailed cost-benefit model before proceeding")
    if not steps:
        steps.append("Proceed with automation pilot on a low-risk sub-process")
    return steps
