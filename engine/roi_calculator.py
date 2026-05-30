import math


def calculate_roi(params):
    required = [
        "headcount",
        "avg_annual_salary",
        "annual_volume",
        "hours_per_unit_current",
        "hours_per_unit_automated",
        "error_rate_current_pct",
        "error_rate_automated_pct",
        "avg_cost_per_error",
        "automation_budget",
    ]
    for field in required:
        if field not in params:
            params[field] = 0

    hc = float(params.get("headcount", 0))
    salary = float(params.get("avg_annual_salary", 0))
    volume = float(params.get("annual_volume", 0))
    hours_current = float(params.get("hours_per_unit_current", 0))
    hours_auto = float(params.get("hours_per_unit_automated", 0))
    err_rate_cur = float(params.get("error_rate_current_pct", 0))
    err_rate_auto = float(params.get("error_rate_automated_pct", 0))
    cost_per_err = float(params.get("avg_cost_per_error", 0))
    budget = float(params.get("automation_budget", 0))
    maintenance_yearly = float(params.get("maintenance_yearly", budget * 0.15))

    labor_cost_current = hc * salary
    total_hours_current = volume * hours_current
    total_hours_auto = volume * hours_auto
    labor_cost_automated = (
        total_hours_auto / max(total_hours_current, 1)
    ) * labor_cost_current
    if labor_cost_automated < 0:
        labor_cost_automated = 0

    errors_current = volume * (err_rate_cur / 100)
    errors_auto = volume * (err_rate_auto / 100)
    error_cost_current = errors_current * cost_per_err
    error_cost_auto = errors_auto * cost_per_err

    total_cost_current = labor_cost_current + error_cost_current
    total_cost_automated = labor_cost_automated + error_cost_auto + maintenance_yearly

    annual_savings = total_cost_current - total_cost_automated
    if budget > 0:
        payback_years = budget / max(annual_savings, 0.01)
    else:
        payback_years = float("inf")

    if annual_savings > 0 and budget > 0:
        roi_3yr = ((annual_savings * 3) - budget) / budget * 100
    else:
        roi_3yr = 0

    labor_savings = labor_cost_current - labor_cost_automated
    error_savings = error_cost_current - error_cost_auto

    if labor_cost_current > 0 and hours_auto < hours_current:
        implied_hc = max(1, round((hours_auto / max(hours_current, 0.001)) * hc))
        ftes_redeployed = max(0, int(hc - implied_hc))
    else:
        ftes_redeployed = 0

    npv_3yr = 0
    if budget > 0:
        discount_rate = 0.10
        npv_3yr = -budget
        for year in range(1, 4):
            npv_3yr += annual_savings / ((1 + discount_rate) ** year)

    return {
        "annual_savings": round(annual_savings, 2),
        "payback_years": round(payback_years, 1)
        if payback_years != float("inf")
        else None,
        "roi_3yr_pct": round(roi_3yr, 1),
        "npv_3yr": round(npv_3yr, 2),
        "labor_cost_current": round(labor_cost_current, 2),
        "labor_cost_automated": round(labor_cost_automated, 2),
        "error_cost_current": round(error_cost_current, 2),
        "error_cost_automated": round(error_cost_auto, 2),
        "total_cost_current": round(total_cost_current, 2),
        "total_cost_automated": round(total_cost_automated, 2),
        "labor_savings": round(labor_savings, 2),
        "error_savings": round(error_savings, 2),
        "ftes_redeployed": ftes_redeployed,
        "errors_current_annual": round(errors_current, 0),
        "errors_automated_annual": round(errors_auto, 0),
        "maintenance_yearly": round(maintenance_yearly, 2),
    }


def classify_roi(roi_result):
    annual = roi_result.get("annual_savings", 0)
    payback = roi_result.get("payback_years")
    roi_3yr = roi_result.get("roi_3yr_pct", 0)

    if annual <= 0 and roi_3yr <= 0:
        return {
            "category": "NEGATIVE ROI",
            "color": "#ef4444",
            "summary": "Automation costs exceed benefits even over 3 years. Do not proceed.",
        }
    if payback is None or payback > 5:
        return {
            "category": "POOR ROI",
            "color": "#f97316",
            "summary": f"Payback period exceeds 5 years (or never). ROI: {roi_3yr}%. Benefits insufficient.",
        }
    if payback > 3:
        return {
            "category": "MODEST ROI",
            "color": "#eab308",
            "summary": f"Payback in {payback} years. 3-year ROI: {roi_3yr}%. Worth considering.",
        }
    if payback > 1:
        return {
            "category": "GOOD ROI",
            "color": "#22c55e",
            "summary": f"Payback in {payback} years. 3-year ROI: {roi_3yr}%. Strong candidate.",
        }
    return {
        "category": "EXCEPTIONAL ROI",
        "color": "#0d6efd",
        "summary": f"Payback in {payback} years. 3-year ROI: {roi_3yr}%. Transformational.",
    }


ROI_INPUT_FIELDS = [
    {
        "id": "headcount",
        "label": "Current Headcount on Process",
        "type": "number",
        "default": 5,
        "suffix": "FTEs",
    },
    {
        "id": "avg_annual_salary",
        "label": "Average Annual Salary (fully loaded)",
        "type": "number",
        "default": 75000,
        "prefix": "$",
        "suffix": "/yr",
    },
    {
        "id": "annual_volume",
        "label": "Annual Transaction Volume",
        "type": "number",
        "default": 10000,
        "suffix": "units/yr",
    },
    {
        "id": "hours_per_unit_current",
        "label": "Hours per Unit (current manual)",
        "type": "number",
        "default": 0.5,
        "suffix": "hrs",
    },
    {
        "id": "hours_per_unit_automated",
        "label": "Hours per Unit (automated)",
        "type": "number",
        "default": 0.05,
        "suffix": "hrs",
    },
    {
        "id": "error_rate_current_pct",
        "label": "Current Error Rate",
        "type": "number",
        "default": 5.0,
        "suffix": "%",
    },
    {
        "id": "error_rate_automated_pct",
        "label": "Projected Automated Error Rate",
        "type": "number",
        "default": 0.5,
        "suffix": "%",
    },
    {
        "id": "avg_cost_per_error",
        "label": "Average Cost per Error",
        "type": "number",
        "default": 50,
        "prefix": "$",
    },
    {
        "id": "automation_budget",
        "label": "Estimated Automation Budget",
        "type": "number",
        "default": 200000,
        "prefix": "$",
    },
]
