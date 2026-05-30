import os
import json
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from flask import Flask, jsonify, request, render_template
from engine.analyzer import analyze_workflow
from engine.scorer import SCORING_DEFAULTS
from engine.what_if import run_what_if, sensitivity_analysis, WHAT_IF_PRESETS
from engine.roi_calculator import calculate_roi, classify_roi, ROI_INPUT_FIELDS
from engine.similarity import find_similar_in_benchmark, get_industry_benchmark_summary
from engine.explainer import explain_scores
from engine.regulations import (
    REGULATORY_FRAMEWORKS,
    get_applicable_regulations,
    get_regulatory_impact,
)
from engine.remediation import get_remediation_playbook, estimate_remediation_timeline
from engine.sub_process import (
    SubProcess,
    decompose_workflow,
    compute_aggregate_scores,
    compute_aggregate_overall,
    find_decomposition_opportunities,
)
from engine.llm import get_status as llm_status, infer_workflow, LLM_CONFIG
from data.benchmark_dataset import (
    get_workflows,
    get_stats,
    get_industries,
    get_categories,
    get_by_industry,
    get_by_category,
    get_by_score_range,
    search,
)
from data.benchmark_generator import compute_overall_score, generate_benchmark

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/dimensions")
def get_dimensions():
    return jsonify(SCORING_DEFAULTS)


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    result = analyze_workflow(data)
    return jsonify(result)


@app.route("/api/what-if", methods=["POST"])
def what_if():
    data = request.get_json()
    if not data or "base_scores" not in data:
        return jsonify({"error": "base_scores required"}), 400
    adjustments = data.get("adjustments", {})
    result = run_what_if(data["base_scores"], adjustments)
    return jsonify(result)


@app.route("/api/sensitivity", methods=["POST"])
def sensitivity():
    data = request.get_json()
    if not data or "base_scores" not in data:
        return jsonify({"error": "base_scores required"}), 400
    result = sensitivity_analysis(data["base_scores"])
    return jsonify(result)


@app.route("/api/what-if/presets")
def what_if_presets():
    return jsonify(WHAT_IF_PRESETS)


@app.route("/api/roi/calculate", methods=["POST"])
def roi_calculate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    result = calculate_roi(data)
    classification = classify_roi(result)
    result["classification"] = classification
    return jsonify(result)


@app.route("/api/roi/fields")
def roi_fields():
    return jsonify(ROI_INPUT_FIELDS)


@app.route("/api/explain", methods=["POST"])
def explain():
    data = request.get_json()
    if not data or "dimension_scores" not in data:
        return jsonify({"error": "dimension_scores required"}), 400
    responses = data.get("responses", {})
    result = explain_scores(data["dimension_scores"], responses)
    return jsonify(result)


@app.route("/api/regulations")
def get_regulations():
    framework = request.args.get("framework")
    if framework:
        fw = REGULATORY_FRAMEWORKS.get(framework)
        if fw:
            return jsonify({framework: fw})
        return jsonify({"error": "Framework not found"}), 404
    return jsonify(
        {
            k: {
                "name": v["name"],
                "industry": v["industry"],
                "jurisdiction": v["jurisdiction"],
            }
            for k, v in REGULATORY_FRAMEWORKS.items()
        }
    )


@app.route("/api/regulations/analyze", methods=["POST"])
def analyze_regulations():
    data = request.get_json()
    industry = data.get("industry", "") if data else ""
    dimension_scores = data.get("dimension_scores", {}) if data else {}
    applicable = get_applicable_regulations(industry, dimension_scores)
    impact = get_regulatory_impact(applicable)
    return jsonify(impact)


@app.route("/api/llm/status")
def llm_check():
    return jsonify(llm_status())


@app.route("/api/llm/infer-workflow", methods=["POST"])
def llm_infer():
    data = request.get_json()
    if not data or "description" not in data:
        return jsonify({"error": "description required"}), 400
    if not LLM_CONFIG["enabled"]:
        return jsonify({"error": "LLM not configured", "available": False}), 503
    result = infer_workflow(data["description"], data.get("industry", ""))
    if result is None:
        return jsonify(
            {"error": "LLM inference failed. Is LM Studio running?", "available": False}
        ), 502
    return jsonify(result)


@app.route("/api/remediation", methods=["POST"])
def remediation():
    data = request.get_json()
    if not data or "dimension_scores" not in data:
        return jsonify({"error": "dimension_scores required"}), 400
    playbook = get_remediation_playbook(data["dimension_scores"])
    timeline = estimate_remediation_timeline(playbook)
    return jsonify({"playbook": playbook, "timeline": timeline})


@app.route("/api/benchmark/similar-by-scores", methods=["POST"])
def benchmark_similar_by_scores():
    data = request.get_json()
    if not data or "scores" not in data:
        return jsonify({"error": "scores required"}), 400
    industry = data.get("industry")
    limit = data.get("limit", 5)
    similar = find_similar_in_benchmark(data["scores"], industry=industry, limit=limit)
    return jsonify(similar)


@app.route("/api/benchmark/industry-summary")
def industry_summary():
    industry = request.args.get("industry")
    if not industry:
        return jsonify({"error": "industry required"}), 400
    summary = get_industry_benchmark_summary(industry)
    if not summary:
        return jsonify({"error": "Industry not found"}), 404
    return jsonify(summary)


@app.route("/api/benchmark")
def get_benchmark():
    industry = request.args.get("industry")
    category = request.args.get("category")
    min_score = request.args.get("min_score")
    max_score = request.args.get("max_score")
    q = request.args.get("q")
    limit = request.args.get("limit", 50, type=int)

    wfs = get_workflows()
    if industry:
        wfs = [w for w in wfs if w["industry"] == industry]
    if category:
        wfs = [w for w in wfs if w["category"] == category]
    if min_score:
        wfs = [
            w for w in wfs if w["scores"].get("overall_score", 50) >= float(min_score)
        ]
    if max_score:
        wfs = [
            w for w in wfs if w["scores"].get("overall_score", 50) <= float(max_score)
        ]
    if q:
        ql = q.lower()
        wfs = [
            w
            for w in wfs
            if ql in w["workflow_name"].lower()
            or ql in w["industry"].lower()
            or ql in w["description"].lower()
        ]

    wfs.sort(key=lambda w: w["scores"].get("overall_score", 0), reverse=True)
    return jsonify(wfs[:limit])


@app.route("/api/benchmark/stats")
def benchmark_stats():
    return jsonify(get_stats())


@app.route("/api/benchmark/industries")
def benchmark_industries():
    return jsonify(get_industries())


@app.route("/api/benchmark/categories")
def benchmark_categories():
    return jsonify(get_categories())


@app.route("/api/regenerate", methods=["POST"])
def regenerate():
    count = request.get_json().get("count", 600) if request.get_json() else 600
    import data.benchmark_dataset as bd

    bd._workflows = None
    bd._stats = None
    wfs = generate_benchmark(count)
    for w in wfs:
        w["scores"]["overall_score"] = compute_overall_score(w["scores"])
    with open(bd.BENCHMARK_PATH, "w") as f:
        json.dump(wfs, f)
    stats = get_stats()
    return jsonify({"count": len(wfs), "stats": stats})


def find_free_port(start=8080, max_attempts=20):
    import socket

    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start


if __name__ == "__main__":
    print("Generating benchmark dataset...")
    wfs = get_workflows()
    print(
        f"Loaded {len(wfs)} synthetic workflows across {len(get_industries())} industries"
    )
    port = find_free_port()
    print(f"\n  → Open http://127.0.0.1:{port} in your browser\n")
    app.run(debug=True, port=port)
