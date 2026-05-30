import json
import os
import requests
from typing import Optional

LLM_CONFIG = {
    "base_url": os.environ.get("LLM_BASE_URL", "").rstrip("/") or "",
    "api_key": os.environ.get("LLM_API_KEY", ""),
    "model": os.environ.get("LLM_MODEL", ""),
}

LLM_CONFIG["enabled"] = bool(LLM_CONFIG["base_url"] and LLM_CONFIG["model"])


def _chat_endpoint():
    return f"{LLM_CONFIG['base_url']}/chat/completions"


def _headers():
    headers = {"Content-Type": "application/json"}
    if LLM_CONFIG["api_key"]:
        headers["Authorization"] = f"Bearer {LLM_CONFIG['api_key']}"
    return headers


def _call_llm(system_prompt, user_prompt, temperature=0.3, max_tokens=2048):
    if not LLM_CONFIG["enabled"]:
        return None

    try:
        body = {
            "model": LLM_CONFIG["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        resp = requests.post(
            _chat_endpoint(),
            headers=_headers(),
            json=body,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        message = data["choices"][0]["message"]
        content = message.get("content", "")

        if not content:
            return None

        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

        return json.loads(cleaned)
    except requests.ConnectionError:
        return None
    except requests.Timeout:
        return None
    except Exception:
        return None


SYSTEM_WORKFLOW_ANALYSIS = """You are an expert automation analyst. Given a workflow description and industry, infer preliminary readiness scores across 7 dimensions. Return strictly a JSON object with:

{
  "dimension_scores": {
    "data_quality": <0-100>,
    "process_stability": <0-100>,
    "exception_rate": <0-100>,
    "decision_complexity": <0-100>,
    "integration_readiness": <0-100>,
    "governance_risk": <0-100>,
    "roi_potential": <0-100>
  },
  "reasoning": "<one-sentence rationale per dimension>",
  "suggested_sub_processes": ["<2-4 natural sub-process names>"],
  "key_risks": ["<2-3 specific risks the workflow likely faces>"]
}

Scoring guide:
- 81-100: Excellent. No issues.
- 61-80: Good. Minor concerns.
- 41-60: Moderate. Some problems.
- 21-40: Poor. Significant issues.
- 0-20: Critical. Major blockers.

Data Quality: completeness, consistency, structure, duplication, reliability
Process Stability: change frequency, standardization, documentation, regulatory churn
Exception Rate: how often humans intervene, edge cases, judgment calls
Decision Complexity: ambiguity, reasoning depth, policy clarity, subjectivity
Integration Readiness: API availability, software stack, data accessibility
Governance Risk: regulatory exposure, compliance burden, legal liability. HIGH SCORE = LOW RISK.
ROI Potential: time saved, cost reduction, error reduction, scalability

Be skeptical. Default to moderate scores unless the description strongly suggests otherwise. Do not inflate scores."""


SYSTEM_CONTEXTUAL_RISKS = """You are a risk analyst specializing in AI automation failures. Given a workflow's scores and context, generate specific, contextual failure modes. Return JSON:

{
  "risks": [
    {
      "mode": "<failure mode name>",
      "description": "<specific description tied to this workflow, not generic>",
      "severity": "Critical|High|Medium|Low",
      "likelihood": "High|Medium|Low",
      "detectability": "High|Medium|Low",
      "mitigation": "<specific action for this workflow context>"
    }
  ]
}

Generate 2-4 risks. Each must reference specifics from the workflow context — never generic text. Focus on realistic failure chains given the dimension scores."""


SYSTEM_EXECUTIVE_SUMMARY = """You are a management consultant writing an executive summary. Given the full automation analysis, write a concise, impactful summary. Return JSON:

{
  "executive_summary": "<2-3 paragraph summary suitable for a VP or CTO>",
  "key_findings": ["<3-5 bullet-point findings>"],
  "recommendation": "<one-sentence bottom-line recommendation>",
  "risk_statement": "<one-sentence top risk the executive should know>"
}

Write in clear business language. No jargon. Be direct about whether automation should or should not proceed."""


def get_status():
    if not LLM_CONFIG["enabled"]:
        return {
            "available": False,
            "configured": False,
            "message": "LLM inference not configured. Set LLM_BASE_URL and LLM_MODEL environment variables to enable AI-powered enrichment.",
        }

    try:
        resp = requests.get(
            f"{LLM_CONFIG['base_url']}/models",
            headers=_headers(),
            timeout=5,
        )
        resp.raise_for_status()
        models = resp.json()
        model_list = [m["id"] for m in models.get("data", [])]
        has_model = LLM_CONFIG["model"] in model_list

        return {
            "available": True,
            "configured": True,
            "endpoint": LLM_CONFIG["base_url"],
            "model": LLM_CONFIG["model"],
            "model_loaded": has_model,
            "available_models": model_list[:10] if model_list else [],
        }
    except Exception as e:
        return {
            "available": False,
            "configured": True,
            "endpoint": LLM_CONFIG["base_url"],
            "model": LLM_CONFIG["model"],
            "error": str(e),
            "message": "Configured but unreachable. Ensure LM Studio is running and the model is loaded.",
        }


def infer_workflow(description, industry):
    if not LLM_CONFIG["enabled"]:
        return None

    user_prompt = f"Industry: {industry or 'Unknown'}\n\nWorkflow Description:\n{description}\n\nAnalyze this workflow and return the JSON assessment."
    result = _call_llm(
        SYSTEM_WORKFLOW_ANALYSIS, user_prompt, temperature=0.3, max_tokens=2048
    )

    if result and "dimension_scores" in result:
        scores = result["dimension_scores"]
        for key in [
            "data_quality",
            "process_stability",
            "exception_rate",
            "decision_complexity",
            "integration_readiness",
            "governance_risk",
            "roi_potential",
        ]:
            if key in scores:
                scores[key] = max(0, min(100, int(scores[key])))
        return result
    return None


def generate_contextual_risks(workflow_data):
    if not LLM_CONFIG["enabled"]:
        return None

    context = json.dumps(workflow_data, indent=2)
    user_prompt = f"Workflow context:\n{context}\n\nGenerate specific, contextual failure modes as JSON."
    result = _call_llm(
        SYSTEM_CONTEXTUAL_RISKS, user_prompt, temperature=0.4, max_tokens=2048
    )
    return result.get("risks", []) if result and "risks" in result else None


def generate_executive_summary(analysis_result):
    if not LLM_CONFIG["enabled"]:
        return None

    context = json.dumps(analysis_result, indent=2, default=str)
    user_prompt = f"Full analysis:\n{context}\n\nGenerate executive summary as JSON."
    result = _call_llm(
        SYSTEM_EXECUTIVE_SUMMARY, user_prompt, temperature=0.4, max_tokens=2048
    )
    return result if result and "executive_summary" in result else None
