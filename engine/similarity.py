import math
from data.benchmark_dataset import get_workflows


def compute_similarity(scores_a, scores_b):
    dims = [
        "data_quality",
        "process_stability",
        "exception_rate",
        "decision_complexity",
        "integration_readiness",
        "governance_risk",
        "roi_potential",
    ]

    squared_diffs = 0
    for dim in dims:
        a = scores_a.get(dim, 50)
        b = scores_b.get(dim, 50)
        squared_diffs += (a - b) ** 2

    distance = math.sqrt(squared_diffs)
    max_distance = math.sqrt(len(dims) * 100**2)
    similarity = max(0, (1 - distance / max_distance)) * 100
    return round(similarity, 1)


def find_similar_in_benchmark(user_dimension_scores, industry=None, limit=5):
    wfs = get_workflows()
    scored = []

    for w in wfs:
        if industry and w["industry"] != industry:
            continue
        sim = compute_similarity(user_dimension_scores, w["scores"])
        scored.append(
            {
                "id": w["id"],
                "workflow_name": w["workflow_name"],
                "industry": w["industry"],
                "similarity": sim,
                "overall_score": w["scores"].get("overall_score", 50),
                "category": w["category"],
                "failures": w["failures"],
                "metadata": w["metadata"],
            }
        )

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:limit]


def get_industry_benchmark_summary(industry):
    wfs = get_workflows()
    industry_wfs = [w for w in wfs if w["industry"] == industry]

    if not industry_wfs:
        return None

    scores = [w["scores"].get("overall_score", 50) for w in industry_wfs]
    cats = {}
    for w in industry_wfs:
        cats[w["category"]] = cats.get(w["category"], 0) + 1

    top_performers = sorted(
        industry_wfs, key=lambda w: w["scores"].get("overall_score", 0), reverse=True
    )[:5]
    bottom_performers = sorted(
        industry_wfs, key=lambda w: w["scores"].get("overall_score", 0)
    )[:5]

    return {
        "industry": industry,
        "count": len(industry_wfs),
        "avg_score": round(sum(scores) / len(scores), 1),
        "min_score": min(scores),
        "max_score": max(scores),
        "category_distribution": cats,
        "top_workflows": [
            {
                "name": w["workflow_name"],
                "score": w["scores"].get("overall_score", 0),
                "category": w["category"],
            }
            for w in top_performers
        ],
        "bottom_workflows": [
            {
                "name": w["workflow_name"],
                "score": w["scores"].get("overall_score", 0),
                "category": w["category"],
            }
            for w in bottom_performers
        ],
    }
