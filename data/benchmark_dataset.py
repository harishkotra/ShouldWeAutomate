import json
import os
from data.benchmark_generator import (
    generate_benchmark,
    get_benchmark_stats,
    compute_overall_score,
)


BENCHMARK_PATH = os.path.join(os.path.dirname(__file__), "benchmark_workflows.json")
STATS_PATH = os.path.join(os.path.dirname(__file__), "benchmark_stats.json")

_workflows = None
_stats = None


def load_or_generate(force=False):
    global _workflows, _stats
    if _workflows is not None and not force:
        return _workflows

    if os.path.exists(BENCHMARK_PATH) and not force:
        try:
            with open(BENCHMARK_PATH, "r") as f:
                _workflows = json.load(f)
            if os.path.exists(STATS_PATH):
                with open(STATS_PATH, "r") as f:
                    _stats = json.load(f)
            else:
                _stats = get_benchmark_stats(_workflows)
                with open(STATS_PATH, "w") as f:
                    json.dump(_stats, f)
            return _workflows
        except Exception:
            pass

    _workflows = generate_benchmark(600)

    for w in _workflows:
        w["scores"]["overall_score"] = compute_overall_score(w["scores"])

    _stats = get_benchmark_stats(_workflows)

    with open(BENCHMARK_PATH, "w") as f:
        json.dump(_workflows, f)
    with open(STATS_PATH, "w") as f:
        json.dump(_stats, f)

    return _workflows


def get_workflows():
    load_or_generate()
    return _workflows


def get_stats():
    load_or_generate()
    return _stats


def get_industries():
    return sorted(set(w["industry"] for w in get_workflows()))


def get_categories():
    return [
        "AGENT AUTOMATION READY",
        "AI ASSISTED AUTOMATION",
        "HUMAN-IN-THE-LOOP AI",
        "IMPROVE PROCESS FIRST",
        "DO NOT AUTOMATE",
    ]


def find_similar(industry, workflow_name, limit=6):
    wfs = get_workflows()
    candidates = [
        w
        for w in wfs
        if w["industry"] == industry and w["workflow_name"] != workflow_name
    ]
    return candidates[:limit]


def get_by_industry(industry):
    return [w for w in get_workflows() if w["industry"] == industry]


def get_by_category(category):
    return [w for w in get_workflows() if w["category"] == category]


def get_by_score_range(min_score, max_score):
    return [
        w
        for w in get_workflows()
        if min_score <= w["scores"].get("overall_score", 50) <= max_score
    ]


def search(query):
    q = query.lower()
    return [
        w
        for w in get_workflows()
        if q in w["workflow_name"].lower()
        or q in w["industry"].lower()
        or q in w["description"].lower()
        or any(q in f.lower() for f in w["failures"])
    ]
