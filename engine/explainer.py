from engine.scorer import SCORING_DEFAULTS


def explain_scores(dimension_scores, responses):
    explanations = {}
    suggestions = []

    for dim_key, dim in SCORING_DEFAULTS.items():
        score = dimension_scores.get(dim_key, 50)
        questions = dim["questions"]
        question_scores = []
        for q in questions:
            val = responses.get(q["id"])
            if val is not None:
                question_scores.append({"id": q["id"], "text": q["text"], "score": val})

        avg_question = (
            sum(qs["score"] for qs in question_scores) / len(question_scores)
            if question_scores
            else 50
        )
        pulling_up = [qs for qs in question_scores if qs["score"] >= avg_question + 10]
        pulling_down = [
            qs for qs in question_scores if qs["score"] <= avg_question - 10
        ]

        explanation = {
            "dimension": dim["label"],
            "score": score,
            "weight": dim["weight"],
            "weighted_contribution": round(score * dim["weight"], 1),
            "question_count": len(questions),
            "pulling_up": [
                {"text": q["text"], "score": q["score"]} for q in pulling_up
            ],
            "pulling_down": [
                {"text": q["text"], "score": q["score"]} for q in pulling_down
            ],
            "verdict": _verdict(score, dim_key),
            "improvement_tip": _improvement_tip(dim_key, score),
        }
        explanations[dim_key] = explanation

        if score < 50:
            suggestions.append(
                {
                    "dimension": dim["label"],
                    "current_score": score,
                    "suggestion": _improvement_tip(dim_key, score),
                    "potential_gain": round((60 - score) * dim["weight"], 1),
                }
            )

    suggestions.sort(key=lambda x: x["potential_gain"], reverse=True)

    return {
        "explanations": explanations,
        "suggestions": suggestions,
        "score_summary": _score_summary(dimension_scores),
    }


def _verdict(score, dim_key):
    if score >= 80:
        return "Excellent — no immediate concern"
    if score >= 60:
        return "Adequate — some room for improvement"
    if score >= 40:
        return "Concerning — should be addressed before automation"
    return "Critical blocker — must be resolved first"


def _improvement_tip(dim_key, score):
    tips = {
        "data_quality": {
            "low": "Implement automated data validation rules. Add mandatory fields. Run periodic data quality audits.",
            "mid": "Strengthen data governance policies. Implement data lineage tracking.",
            "high": "Maintain current practices. Consider real-time data quality monitoring.",
        },
        "process_stability": {
            "low": "Document the process end-to-end. Freeze process changes for 90 days. Map all variants.",
            "mid": "Standardize workflow variants. Implement change control procedures.",
            "high": "Maintain documentation discipline. Monitor for process drift.",
        },
        "exception_rate": {
            "low": "Root-cause analyze top 10 exception types. Build decision trees for common exceptions.",
            "mid": "Create exception handling playbooks. Reduce approval chain length.",
            "high": "Monitor exception trends. Proactively address emerging exception patterns.",
        },
        "decision_complexity": {
            "low": "Decompose decisions into rule-based and judgment-based. Create clear decision criteria.",
            "mid": "Build decision support tools. Capture expert decision patterns.",
            "high": "Document edge case handling. Regularly review decision outcomes.",
        },
        "integration_readiness": {
            "low": "Audit API availability across all tools. Evaluate middleware/platform solutions.",
            "mid": "Implement API gateway. Standardize authentication patterns.",
            "high": "Explore advanced integrations. Consider event-driven architecture.",
        },
        "governance_risk": {
            "low": "Map regulatory requirements to process steps. Engage compliance team.",
            "mid": "Implement automated compliance checks. Strengthen audit trails.",
            "high": "Maintain compliance monitoring. Prepare for regulatory changes.",
        },
        "roi_potential": {
            "low": "Build detailed cost model. Identify lowest-effort, highest-value sub-process.",
            "mid": "Pilot automation on one sub-process to validate ROI projections.",
            "high": "Scale automation to adjacent processes. Measure and report realized ROI.",
        },
    }

    if score < 40:
        category = "low"
    elif score < 70:
        category = "mid"
    else:
        category = "high"

    return tips.get(dim_key, {}).get(category, "Review and improve this dimension.")


def _score_summary(dimension_scores):
    sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1])
    worst = sorted_dims[:3] if len(sorted_dims) >= 3 else sorted_dims
    best = sorted_dims[-3:] if len(sorted_dims) >= 3 else sorted_dims

    return {
        "strongest_dimensions": [
            {"dim": d, "score": s, "label": SCORING_DEFAULTS[d]["label"]}
            for d, s in reversed(best)
        ],
        "weakest_dimensions": [
            {"dim": d, "score": s, "label": SCORING_DEFAULTS[d]["label"]}
            for d, s in worst
        ],
        "spread": max(v for v in dimension_scores.values())
        - min(v for v in dimension_scores.values()),
    }
