# ⚡ ShouldWeAutomate?

**Decision intelligence platform for workflow automation readiness.** Evaluate any business process across 7 dimensions, get a readiness score, risk analysis, ROI projection, regulatory mapping, remediation playbooks — all in your browser. No account required.

![Screenshot](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)
[![Built by Harish Kotra](https://img.shields.io/badge/built%20by-harishkotra.me-blueviolet)](https://harishkotra.me)

### Screenshots

<img width="1667" height="4216" alt="screencapture-127-0-0-1-8080-2026-05-30-23_37_19" src="https://github.com/user-attachments/assets/63a35395-e8ae-4d2c-84a2-91210d5966e9" />
<img width="1667" height="7671" alt="screencapture-127-0-0-1-8080-2026-05-30-23_39_45" src="https://github.com/user-attachments/assets/67724a56-25c8-4a6b-a8b0-3c258e89c6dc" />
<img width="1667" height="1085" alt="screencapture-127-0-0-1-8080-2026-05-30-23_39_57" src="https://github.com/user-attachments/assets/6c3aae64-4ca3-45e4-a8a8-ac38c3535e09" />

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **7-Dimension Scoring** | Data Quality, Process Stability, Exception Rate, Decision Complexity, Tool Integration, Governance Risk, ROI Potential |
| **AI Auto-Fill** | Describe your workflow in plain language — optional LLM inference pre-fills all scores |
| **Live Gamified UX** | Aggregate sliders with tier badges (Bronze → Mythic), real-time gauge, instant recommendation preview |
| **Sub-Process Decomposition** | Break workflows into weighted sub-processes with independent scoring |
| **Quantitative ROI Calculator** | Dollar-based projection with payback period, 3-year NPV, FTE redeployment |
| **What-If Simulation** | Adjust scores and instantly see overall impact |
| **Synthetic Benchmark** | 600+ generated workflows across 10 industries for comparison |
| **Regulatory Mapping** | HIPAA, GDPR, SOX, PCI-DSS, and more — context-aware governance penalties |
| **Remediation Playbooks** | Actionable improvement plans per dimension with effort estimates |
| **Executive AI Summary** | CTO-ready summary with key findings and risk statement (when LLM enabled) |

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (Flask Templates)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │ Workflow │  │  AI      │  │  7-Dim   │  │   ROI      │ │
│  │  Desc    │→│  Prefill │→│ Scoring  │→│ Calculator │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘ │
│         ↓                                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Results Dashboard: Gauge · Radar · Risks · ROI ·   │   │
│  │  What-If · Remediation · Regulatory · Benchmark      │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP / JSON
┌──────────────────────────▼──────────────────────────────────┐
│                     Flask Backend                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │ Scorer   │  │ Analyzer │  │ Explainer│  │   LLM      │ │
│  │ Engine   │←→│ (orchest)│←→│ Engine   │  │  Gateway   │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────┬──────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │         │
│  │   ROI    │  │ Remediate│  │ What-If  │   LM Studio │
│  │ Calculator│  │ Playbook │  │ Simulator│  (OpenAI API)│
│  └──────────┘  └──────────┘  └──────────┘        │         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │         │
│  │Regulatory│  │Benchmark │  │Similarity│        ▼         │
│  │ Mapping  │  │ Dataset  │  │  Search  │  Local / Remote  │
│  └──────────┘  └──────────┘  └──────────┘     LLM Server   │
└─────────────────────────────────────────────────────────────┘
```

## 🧠 How Scoring Works

Each workflow is evaluated across **7 weighted dimensions**. Each dimension has **5 sub-questions** (0-100 scale). The dimension score is the average of its sub-questions, and the overall score is a weighted sum:

```python
WEIGHTS = {
    "data_quality":        0.20,  # Completeness, consistency, structure, dedup, reliability
    "process_stability":   0.20,  # Change frequency, variants, standardization, docs, reg churn
    "exception_rate":      0.15,  # Intervention %, special cases, escalations, judgment, edges
    "decision_complexity": 0.15,  # Decision points, ambiguity, reasoning depth, subjectivity
    "integration_readiness": 0.10, # APIs, software stack, data accessibility, auth, vendor support
    "governance_risk":     0.10,  # Regulatory exposure, compliance, financial impact, liability, audit
    "roi_potential":       0.10,  # Time saved, cost reduction, error reduction, revenue, scalability
}
```

### Recommendation Tiers

| Score Range | Recommendation | Architecture |
|-------------|----------------|-------------|
| 85-100 | 🚀 **AGENT AUTOMATION READY** | Autonomous multi-agent system |
| 70-84 | ⚡ **AI ASSISTED AUTOMATION** | AI-assisted with human escalation |
| 50-69 | 🔶 **HUMAN-IN-THE-LOOP AI** | AI recommends, humans decide |
| 30-49 | ⚠️ **IMPROVE PROCESS FIRST** | Process improvement initiative |
| 0-29 | 🛑 **DO NOT AUTOMATE** | Foundational problems must be resolved first |

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/harishkotra/ShouldWeAutomate.git
cd ShouldWeAutomate

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

Open the URL printed in the terminal (default `http://127.0.0.1:8080`).

### Optional: Enable AI Features

Create a `.env` file in the project root:

```bash
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=your-model-name
```

Works with any OpenAI-compatible endpoint (LM Studio, Ollama, OpenAI API, etc.).

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dimensions` | GET | Scoring dimensions and questions |
| `/api/analyze` | POST | Full workflow analysis |
| `/api/roi/calculate` | POST | Quantitative ROI calculation |
| `/api/what-if` | POST | Score simulation |
| `/api/sensitivity` | POST | Sensitivity analysis |
| `/api/explain` | POST | Score explanation engine |
| `/api/remediation` | POST | Remediation playbooks |
| `/api/regulations/analyze` | POST | Regulatory framework mapping |
| `/api/llm/infer-workflow` | POST | AI score inference |
| `/api/llm/status` | GET | LLM availability check |
| `/api/benchmark` | GET | Benchmark workflows with filters |
| `/api/benchmark/similar-by-scores` | POST | Similarity search |

## 🛠 Tech Stack

- **Backend**: Python 3, Flask 3.0, Flask-CORS
- **Frontend**: Vanilla JS, Chart.js, CSS3 (dark theme)
- **AI**: OpenAI-compatible LLM (LM Studio, Ollama, OpenAI)
- **Data**: Synthetic benchmark dataset (600+ workflows)
- **Testing**: pytest

## 🤝 Contributing

Contributions are welcome! Here are some ideas:

### New Feature Ideas

1. **Multi-language support** — add i18n for international workflows and regulatory frameworks
2. **PDF export** — generate downloadable PDF reports with all scores and recommendations
3. **User accounts & history** — save analysis history, compare across runs, track improvements
4. **Custom dimension weights** — let users adjust weights per their industry/context
5. **Real API integrations** — connect to actual tools (Jira, ServiceNow, SAP) to pull real workflow metrics
6. **Team collaboration** — share analysis results with team comments and approvals
7. **Time-series tracking** — re-evaluate same workflow over time to track automation readiness improvements
8. **More benchmark industries** — add Pharma, Energy, Education, Non-profit sectors
9. **CI/CD integration** — GitHub Actions bot that auto-evaluates workflow descriptions from issues
10. **Mobile responsive enhancements** — further polish the mobile experience

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

```bash
# Setup dev environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest
```
