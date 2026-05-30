# Building ShouldWeAutomate: A Decision Intelligence Platform for Workflow Automation

*How we built an open-source platform that tells you whether your business process is ready for AI automation — with deterministic scoring, gamified UX, and optional LLM inference.*

---

## The Problem

Every week, someone asks: *"Can we automate this workflow?"* The answer is never simple. It depends on data quality, process stability, regulatory exposure, exception rates, integration readiness, decision complexity, and ROI potential — seven dimensions that interact in non-obvious ways.

Most automation decisions are made on gut feel. Teams spend months building automation only to discover the process changes too frequently, the data is too messy, or the compliance team blocks it.

We wanted to build a tool that makes this evaluation **systematic, data-driven, and interactive** — something a team can open in a browser, describe their workflow, and get a defensible answer in seconds.

## The Architecture

### Frontend

Single-page Flask application rendered server-side with Jinja2 templates. The frontend is vanilla JavaScript with Chart.js for the radar visualization and a custom SVG gauge for the overall score.

**Key design decisions:**

- **No build step.** No webpack, no React, no npm. Pure HTML/CSS/JS. Zero friction for contributors.
- **Gamified sliders.** Instead of 35 individual range inputs (5 questions × 7 dimensions), we show 7 aggregate dimension sliders with tier badges — Critical → Bronze → Silver → Gold → Mythic. Click "Fine-tune" to expand the 5 sub-questions.
- **Live preview.** A mini gauge and recommendation badge update in real-time as sliders move. Users see their score change before they click "Analyze."

```javascript
// Core rendering — dimension cards with aggregate + fine-tune
function createDimSection(key, dim, prefix) {
  const aggDefault = Math.round(
    dim.questions.reduce((s, q) => s + q.default, 0) / dim.questions.length
  );
  const tier = getTier(aggDefault);
  // ... builds the HTML with aggregate slider + expandable sub-sliders
}

// Live preview — recompute overall on every slider change
function updateLivePreview() {
  const weights = [0.20, 0.20, 0.15, 0.15, 0.10, 0.10, 0.10];
  dimKeys.forEach((key, i) => total += getAggregateValue(key) * weights[i]);
  // Update gauge SVG dashoffset, tier badge, recommendation text
}
```

### Backend

Flask acts as both the web server and the decision engine. The architecture follows a modular design:

```
engine/
├── scorer.py          # Dimension scoring logic, defaults, recommendations
├── analyzer.py        # Orchestrator — ties all modules together
├── explainer.py       # Score breakdown with pull-up/pull-down analysis
├── what_if.py         # What-if simulation and sensitivity analysis
├── roi_calculator.py  # Quantitative ROI with NPV, payback, FTE impact
├── remediation.py     # Remediation playbooks per dimension
├── regulations.py     # Regulatory framework mapping (HIPAA, GDPR, SOX, etc.)
├── similarity.py      # Benchmark similarity search
├── sub_process.py     # Multi-process decomposition and aggregation
└── llm.py             # OpenAI-compatible LLM gateway
```

### The Scoring Engine

The core scoring logic in `scorer.py` defines 7 dimensions, each with 5 weighted sub-questions:

```python
SCORING_DEFAULTS = {
    "data_quality": {
        "label": "Data Quality",
        "weight": 0.20,
        "questions": [
            {"id": "data_completeness", "text": "How complete is your data?", ...},
            {"id": "data_consistency", "text": "How consistent is data format?", ...},
            # ... 5 questions per dimension
        ],
    },
    # ... 6 more dimensions
}
```

The overall score is a weighted average. The recommendation tier is determined by thresholds inspired by Capability Maturity Model (CMM) levels:

```python
def get_recommendation(overall_score):
    if overall_score < 30:
        return {"level": "DO NOT AUTOMATE", ...}
    elif overall_score < 50:
        return {"level": "IMPROVE PROCESS FIRST", ...}
    elif overall_score < 70:
        return {"level": "HUMAN-IN-THE-LOOP AI", ...}
    elif overall_score < 85:
        return {"level": "AI ASSISTED AUTOMATION", ...}
    else:
        return {"level": "AGENT AUTOMATION READY", ...}
```

### AI Integration

The LLM integration in `engine/llm.py` is optional and modular. It follows the OpenAI chat completions format, making it compatible with LM Studio, Ollama, OpenAI, Anthropic, or any other provider.

When enabled, the AI performs three tasks:

1. **Score inference** — given a workflow description, infer preliminary dimension scores
2. **Contextual risk analysis** — generate specific failure modes tied to the actual workflow context
3. **Executive summary** — produce a CTO-ready summary with key findings and recommendations

```python
def infer_workflow(description, industry):
    user_prompt = f"Industry: {industry}\n\nWorkflow Description:\n{description}"
    result = _call_llm(SYSTEM_WORKFLOW_ANALYSIS, user_prompt)
    if result and "dimension_scores" in result:
        # Clamp scores to 0-100 and return
        scores = {k: max(0, min(100, int(v))) for k, v in result["dimension_scores"].items()}
        return result
    return None
```

The system prompt instructs the LLM to be skeptical and default to moderate scores unless the description strongly suggests otherwise — preventing over-optimistic AI outputs.

### Benchmark Dataset

The `data/benchmark_generator.py` creates 600+ synthetic workflows across 10 industries with deliberately injected failure modes:

```python
FAILURE_PROFILES = {
    "contradictory_rules": "Business rules are contradictory across departments",
    "broken_apis": "Legacy systems have no stable API endpoints",
    "regulatory_churn": "Regulations change quarterly, invalidating logic",
    "data_rot": "Historical data uses outdated schemas",
    "seasonal_spikes": "Volume varies 10x between peak and off-peak",
    "fraud_scenarios": "Fraud patterns evolve faster than detection rules",
    # ... more failure modes
}
```

Each workflow gets randomized dimension scores, a metadata profile, and injected failure modes. The result is a realistic benchmark for similarity matching — when a user analyzes their workflow, we find the 5 most similar synthetic workflows.

## The Gamification Layer

The original UI had 35 range sliders visible at once. Users found it overwhelming. We redesigned it with three principles:

1. **Progressive disclosure.** Show 7 aggregate sliders. "Fine-tune" expands to the full 35.
2. **Instant feedback.** Every slider move updates the gauge, tier badge, and recommendation preview.
3. **Tier badges.** Each dimension gets a fun label: 🥉 Bronze, 🥈 Silver, 🥇 Gold, 🏆 Mythic.

```javascript
function getTier(score) {
  if (score >= 85) return { text: "Mythic", icon: "🏆", cls: "tier-excellent" };
  if (score >= 70) return { text: "Gold",   icon: "🥇", cls: "tier-good" };
  if (score >= 50) return { text: "Silver", icon: "🥈", cls: "tier-moderate" };
  if (score >= 30) return { text: "Bronze", icon: "🥉", cls: "tier-poor" };
  return { text: "Critical", icon: "⛔", cls: "tier-critical" };
}
```

AI auto-fill is now the default path. Users describe their workflow in a textarea, click "Auto-fill Scores," and the AI pre-fills all 35 sub-scores. Users can then fine-tune before analyzing.

## The Results Dashboard

After analysis, users get a comprehensive dashboard with seven tabs:

| Tab | Content |
|-----|---------|
| **Overview** | Gauge, radar chart, risks, red flags, failure mode analysis, ROI, benchmark comparison, next steps |
| **Explanation** | Per-dimension breakdown with pull-up/pull-down factors and improvement tips |
| **What-If** | Sensitivity analysis + preset scenarios + custom sliders |
| **Remediation** | Phased action plans per dimension with effort estimates |
| **Regulatory** | Applicable regulations with governance penalties and audit requirements |
| **AI Summary** | Executive summary generated by LLM (when enabled) |

## What We Learned

1. **Deterministic engines are underrated.** The LLM is a nice-to-have, but the deterministic scoring engine handles 90% of use cases. It's fast (~1 second), predictable, and doesn't require users to set up external services.

2. **Gamification reduces friction.** Users engaged more with tier badges and live preview than with a static form. The instant feedback loop makes the evaluation feel like a game rather than a survey.

3. **AI prefill is a trust cliff.** When AI prefills scores, users trust it more if they can see and tweak every value. The fine-tune section is critical for building confidence.

4. **Synthetic benchmarks are surprisingly useful.** Even though they're generated, they provide a reference frame. Users want to know how their scores compare to "similar" workflows.

## Getting Started

```bash
git clone https://github.com/harishkotra/ShouldWeAutomate.git
cd ShouldWeAutomate
pip install -r requirements.txt
python app.py
```

## Try It

The live version runs locally — no account required, no data stored. Open your browser, describe a workflow, and see where you stand.

---

*Built by [Harish Kotra](https://harishkotra.me) · Check out [other builds](https://dailybuild.xyz)*
