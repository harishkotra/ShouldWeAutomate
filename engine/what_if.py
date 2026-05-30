from engine.scorer import SCORING_DEFAULTS, get_recommendation
from engine.sub_process import compute_overall_score as aggregate_overall


def run_what_if(base_dimension_scores, adjustments):
    adjusted = dict(base_dimension_scores)
    for dim, delta in adjustments.items():
        if dim in adjusted:
            adjusted[dim] = max(0, min(100, adjusted[dim] + delta))
    overall = aggregate_overall(adjusted)
    rec = get_recommendation(overall)
    return {
        "adjusted_scores": adjusted,
        "overall_score": round(overall, 1),
        "recommendation": rec,
        "deltas": {
            dim: round(adjusted[dim] - base_dimension_scores.get(dim, 0), 1)
            for dim in adjusted
        },
    }


def sensitivity_analysis(base_dimension_scores):
    base_overall = aggregate_overall(base_dimension_scores)
    impacts = {}
    for dim in SCORING_DEFAULTS:
        test_scores = dict(base_dimension_scores)
        original = test_scores[dim]
        test_scores[dim] = max(0, min(100, original + 10))
        new_overall = aggregate_overall(test_scores)
        impacts[dim] = {
            "impact_per_10_pts": round(new_overall - base_overall, 2),
            "label": SCORING_DEFAULTS[dim]["label"],
            "weight": SCORING_DEFAULTS[dim]["weight"],
            "current_score": base_dimension_scores.get(dim, 50),
            "improvement_potential": round(100 - base_dimension_scores.get(dim, 50), 1),
        }

    ranked = sorted(
        impacts.items(), key=lambda x: x[1]["impact_per_10_pts"], reverse=True
    )

    return {
        "base_overall": round(base_overall, 1),
        "impacts": impacts,
        "highest_leverage": ranked[0] if ranked else None,
        "ranked_dimensions": [{"dim": dim, **info} for dim, info in ranked],
    }


WHAT_IF_PRESETS = [
    {"name": "Fix Data Quality", "adjustments": {"data_quality": 30}},
    {"name": "Stabilize Process", "adjustments": {"process_stability": 25}},
    {"name": "Reduce Exceptions", "adjustments": {"exception_rate": 20}},
    {"name": "Resolve Governance Risk", "adjustments": {"governance_risk": 35}},
    {
        "name": "Improve All Weak Dimensions",
        "adjustments": {
            "data_quality": 20,
            "process_stability": 15,
            "governance_risk": 15,
        },
    },
    {
        "name": "Maximize Everything",
        "adjustments": {
            "data_quality": 40,
            "process_stability": 30,
            "exception_rate": 20,
            "decision_complexity": 15,
            "integration_readiness": 20,
            "governance_risk": 30,
            "roi_potential": 10,
        },
    },
]
