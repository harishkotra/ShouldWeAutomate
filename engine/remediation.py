REMEDIATION_PLAYBOOKS = {
    "data_quality": {
        "low": {
            "phase_1": {
                "name": "Data Source Audit",
                "actions": [
                    "Inventory all data sources feeding this workflow",
                    "Profile each source for completeness, accuracy, and timeliness",
                    "Identify single-source-of-truth candidates for each data element",
                    "Document data lineage from source to output",
                ],
                "effort": "2-4 weeks",
                "team": "Data analyst + SME",
            },
            "phase_2": {
                "name": "Validation & Cleansing",
                "actions": [
                    "Implement input validation rules for all required fields",
                    "Build automated data cleansing pipelines for common issues",
                    "Set up duplicate detection and merge logic",
                    "Create data quality scorecards per source",
                ],
                "effort": "4-8 weeks",
                "team": "Data engineer + Analyst",
            },
            "phase_3": {
                "name": "Governance & Monitoring",
                "actions": [
                    "Establish data ownership for each source",
                    "Deploy data quality monitoring dashboard with alerts",
                    "Implement monthly data quality review process",
                    "Create escalation path for chronic data issues",
                ],
                "effort": "4-6 weeks",
                "team": "Data governance lead + SMEs",
            },
        },
        "mid": {
            "phase_1": {
                "name": "Strengthen Validation",
                "actions": [
                    "Review and tighten existing validation rules",
                    "Add cross-field validation for dependent data elements",
                    "Implement real-time data quality checks at ingestion points",
                ],
                "effort": "2-4 weeks",
                "team": "Data engineer",
            },
            "phase_2": {
                "name": "Data Quality Monitoring",
                "actions": [
                    "Deploy automated data quality dashboards",
                    "Set up alerts for quality threshold breaches",
                    "Establish data quality SLAs with data producers",
                ],
                "effort": "3-5 weeks",
                "team": "Data engineer + Governance lead",
            },
        },
        "high": {
            "phase_1": {
                "name": "Continuous Improvement",
                "actions": [
                    "Monitor for emerging data quality issues",
                    "Conduct quarterly data quality reviews",
                    "Proactively address root causes of data issues",
                ],
                "effort": "Ongoing",
                "team": "Data governance team",
            },
        },
    },
    "process_stability": {
        "low": {
            "phase_1": {
                "name": "Process Discovery & Documentation",
                "actions": [
                    "Map current-state process with all variants",
                    "Interview process participants to capture tribal knowledge",
                    "Document process steps, decision points, and inputs/outputs",
                    "Identify and catalog all workflow variants",
                ],
                "effort": "3-6 weeks",
                "team": "Process analyst + SMEs",
            },
            "phase_2": {
                "name": "Standardization",
                "actions": [
                    "Align variants to a single standard process where possible",
                    "Define and document standard operating procedures",
                    "Implement process change control board",
                    "Establish process versioning and communication plan",
                ],
                "effort": "6-12 weeks",
                "team": "Process owner + Ops team",
            },
            "phase_3": {
                "name": "Stabilization",
                "actions": [
                    "Freeze process changes for 90 days",
                    "Monitor process adherence and address deviations",
                    "Implement process compliance checks",
                    "Create process exception handling guidelines",
                ],
                "effort": "4-8 weeks",
                "team": "Process owner + Quality team",
            },
        },
        "mid": {
            "phase_1": {
                "name": "Process Variant Reduction",
                "actions": [
                    "Analyze remaining process variants for consolidation potential",
                    "Document decision criteria for variant selection",
                    "Implement process change management workflow",
                ],
                "effort": "3-6 weeks",
                "team": "Process analyst",
            },
            "phase_2": {
                "name": "Process Monitoring",
                "actions": [
                    "Implement process adherence metrics",
                    "Set up process drift detection alerts",
                    "Establish periodic process review cadence",
                ],
                "effort": "2-4 weeks",
                "team": "Process owner",
            },
        },
        "high": {
            "phase_1": {
                "name": "Maintain & Optimize",
                "actions": [
                    "Conduct quarterly process effectiveness reviews",
                    "Proactively identify optimization opportunities",
                    "Share process best practices across organization",
                ],
                "effort": "Ongoing",
                "team": "Process owner",
            },
        },
    },
    "exception_rate": {
        "low": {
            "phase_1": {
                "name": "Exception Pattern Analysis",
                "actions": [
                    "Categorize all exception types from last 6 months",
                    "Quantify frequency, effort, and impact per exception type",
                    "Identify root causes for top 10 exception categories",
                    "Build decision trees for common exception paths",
                ],
                "effort": "3-5 weeks",
                "team": "Process analyst + Ops team",
            },
            "phase_2": {
                "name": "Exception Reduction Playbooks",
                "actions": [
                    "Create automated handling for rule-based exceptions",
                    "Build decision support tools for judgment-based exceptions",
                    "Implement pre-checks to prevent common exception triggers",
                    "Reduce approval chain depth for standard exceptions",
                ],
                "effort": "6-10 weeks",
                "team": "Process analyst + Developer",
            },
            "phase_3": {
                "name": "Continuous Exception Management",
                "actions": [
                    "Monitor exception rates with automated dashboards",
                    "Quarterly exception trend analysis and action planning",
                    "Periodic review and update of exception handling playbooks",
                ],
                "effort": "Ongoing",
                "team": "Ops team",
            },
        },
        "mid": {
            "phase_1": {
                "name": "Exception Process Optimization",
                "actions": [
                    "Review current exception handling for bottlenecks",
                    "Implement tiered exception handling (Tier 1 auto, Tier 2 review, Tier 3 escalate)",
                    "Create exception handling SLAs and monitoring",
                ],
                "effort": "4-6 weeks",
                "team": "Process analyst + Developer",
            },
        },
        "high": {
            "phase_1": {
                "name": "Monitor & Tune",
                "actions": [
                    "Track exception rate trends monthly",
                    "Proactively address emerging exception patterns",
                    "Fine-tune automated exception handling rules",
                ],
                "effort": "Ongoing",
                "team": "Ops team",
            },
        },
    },
    "decision_complexity": {
        "low": {
            "phase_1": {
                "name": "Decision Decomposition",
                "actions": [
                    "Map all decision points in the workflow",
                    "Classify each decision as rule-based, pattern-based, or judgment-based",
                    "Document decision criteria and inputs for each point",
                    "Identify decisions that can be fully automated vs. those needing humans",
                ],
                "effort": "3-5 weeks",
                "team": "Process analyst + SME",
            },
            "phase_2": {
                "name": "Decision Support System",
                "actions": [
                    "Build rule engines for deterministic decisions",
                    "Train ML models for pattern-based decisions",
                    "Create decision support dashboards for judgment-based decisions",
                    "Implement confidence thresholds for automated decisions",
                ],
                "effort": "8-16 weeks",
                "team": "Data scientist + Developer",
            },
        },
        "mid": {
            "phase_1": {
                "name": "Decision Clarity",
                "actions": [
                    "Document edge cases and their handling",
                    "Create clear decision criteria for ambiguous situations",
                    "Implement decision logging for audit trail",
                ],
                "effort": "3-5 weeks",
                "team": "SME + Process analyst",
            },
        },
        "high": {
            "phase_1": {
                "name": "Edge Case Monitoring",
                "actions": [
                    "Log and review all out-of-pattern decisions",
                    "Periodically validate decision rules against outcomes",
                    "Update decision criteria based on emerging patterns",
                ],
                "effort": "Ongoing",
                "team": "SME",
            },
        },
    },
    "integration_readiness": {
        "low": {
            "phase_1": {
                "name": "Integration Audit",
                "actions": [
                    "Inventory all tools and systems in the workflow",
                    "Assess API availability, version, and documentation quality",
                    "Identify authentication and authorization requirements",
                    "Document data formats and transfer mechanisms",
                ],
                "effort": "2-4 weeks",
                "team": "Integration architect",
            },
            "phase_2": {
                "name": "Integration Architecture",
                "actions": [
                    "Design integration architecture with API gateway or middleware",
                    "Implement standardized authentication (OAuth, API keys)",
                    "Build data transformation and mapping layer",
                    "Create error handling and retry logic",
                ],
                "effort": "8-16 weeks",
                "team": "Integration architect + Developer",
            },
            "phase_3": {
                "name": "Monitoring & Reliability",
                "actions": [
                    "Implement integration health monitoring",
                    "Set up alerts for API failures or degradation",
                    "Create integration runbook with escalation procedures",
                    "Establish vendor communication channels for API changes",
                ],
                "effort": "3-5 weeks",
                "team": "Developer + Ops",
            },
        },
        "mid": {
            "phase_1": {
                "name": "Integration Hardening",
                "actions": [
                    "Add retry logic and circuit breakers to existing integrations",
                    "Implement integration monitoring and alerting",
                    "Standardize error handling across integrations",
                    "Create API documentation and usage guidelines",
                ],
                "effort": "4-8 weeks",
                "team": "Developer",
            },
        },
        "high": {
            "phase_1": {
                "name": "Integration Optimization",
                "actions": [
                    "Explore event-driven architecture for real-time integration",
                    "Evaluate API version upgrades for performance gains",
                    "Optimize data transfer frequency and batch sizes",
                ],
                "effort": "4-8 weeks",
                "team": "Developer + Architect",
            },
        },
    },
    "governance_risk": {
        "low": {
            "phase_1": {
                "name": "Regulatory Mapping",
                "actions": [
                    "Map every regulatory requirement to specific process steps",
                    "Identify automated controls needed for each requirement",
                    "Document evidence collection procedures for audits",
                    "Engage compliance team in automation design review",
                ],
                "effort": "4-8 weeks",
                "team": "Compliance officer + Process owner",
            },
            "phase_2": {
                "name": "Compliance Automation",
                "actions": [
                    "Implement automated compliance checks at decision points",
                    "Build audit trail logging for all automated actions",
                    "Create compliance reporting dashboards",
                    "Set up automated regulatory change monitoring",
                ],
                "effort": "8-16 weeks",
                "team": "Developer + Compliance officer",
            },
            "phase_3": {
                "name": "Governance Framework",
                "actions": [
                    "Establish AI governance board for automation oversight",
                    "Implement human approval gates for high-risk decisions",
                    "Create automated testing and validation framework",
                    "Document disaster recovery and business continuity plans",
                ],
                "effort": "6-12 weeks",
                "team": "Governance lead + Legal + Compliance",
            },
        },
        "mid": {
            "phase_1": {
                "name": "Controls Strengthening",
                "actions": [
                    "Review and update existing control documentation",
                    "Implement additional automated controls for gaps",
                    "Strengthen audit trail completeness and retention",
                    "Conduct pre-automation compliance assessment",
                ],
                "effort": "4-8 weeks",
                "team": "Compliance officer + Developer",
            },
        },
        "high": {
            "phase_1": {
                "name": "Maintain Compliance",
                "actions": [
                    "Conduct periodic compliance reviews",
                    "Monitor regulatory landscape for changes",
                    "Update controls documentation as needed",
                ],
                "effort": "Ongoing",
                "team": "Compliance team",
            },
        },
    },
    "roi_potential": {
        "low": {
            "phase_1": {
                "name": "Cost-Benefit Analysis",
                "actions": [
                    "Build detailed as-is cost model (labor, errors, delays)",
                    "Identify automation candidate sub-processes",
                    "Estimate automation costs (build, run, maintain)",
                    "Calculate break-even analysis for multiple scenarios",
                ],
                "effort": "2-4 weeks",
                "team": "Finance analyst + Process owner",
            },
            "phase_2": {
                "name": "Minimum Viable Automation",
                "actions": [
                    "Identify single highest-value automation target",
                    "Build MVP automation with manual fallback",
                    "Measure actual time/cost savings vs. projections",
                    "Decide whether to expand based on validated data",
                ],
                "effort": "6-12 weeks",
                "team": "Developer + Process owner",
            },
        },
        "mid": {
            "phase_1": {
                "name": "Value Validation",
                "actions": [
                    "Measure pre/post automation metrics rigorously",
                    "Identify secondary automation opportunities",
                    "Optimize automation scope for maximum ROI",
                ],
                "effort": "4-8 weeks",
                "team": "Process owner + Developer",
            },
        },
        "high": {
            "phase_1": {
                "name": "Scale & Expand",
                "actions": [
                    "Expand automation to adjacent workflows",
                    "Implement self-service automation capabilities",
                    "Track and report automation ROI to stakeholders",
                    "Build center of excellence for automation",
                ],
                "effort": "8-16 weeks",
                "team": "Automation CoE + Business units",
            },
        },
    },
}


def get_remediation_playbook(dimension_scores):
    playbook = {}
    for dim_key, score in dimension_scores.items():
        template = REMEDIATION_PLAYBOOKS.get(dim_key, {})
        if score < 40:
            phases = template.get("low", {})
        elif score < 70:
            phases = template.get("mid", {})
        else:
            phases = template.get("high", {})

        if phases:
            playbook[dim_key] = {
                "dimension": dim_key,
                "current_score": score,
                "severity": "Critical"
                if score < 30
                else ("High" if score < 50 else ("Medium" if score < 70 else "Low")),
                "phases": [
                    {
                        "name": phases[key]["name"],
                        "actions": phases[key]["actions"],
                        "effort": phases[key]["effort"],
                        "team": phases[key]["team"],
                    }
                    for key in sorted(phases.keys())
                ],
            }

    return playbook


def estimate_remediation_timeline(playbook):
    total_weeks = 0
    teams_needed = set()
    for dim_key, plan in playbook.items():
        for phase in plan["phases"]:
            effort_str = phase["effort"]
            weeks = 0
            parts = effort_str.split("-")
            try:
                if len(parts) == 2:
                    weeks = (
                        int(parts[0])
                        + int(
                            parts[1]
                            .replace(" weeks", "")
                            .replace(" week", "")
                            .replace("+", "")
                        )
                    ) / 2
                elif "ongoing" in effort_str.lower():
                    weeks = 2
                else:
                    weeks = int(parts[0].replace(" weeks", "").replace(" week", ""))
            except (ValueError, IndexError):
                weeks = 4
            total_weeks += weeks
            teams_needed.add(phase["team"])

    return {
        "estimated_total_weeks": int(total_weeks),
        "estimated_months": round(total_weeks / 4.33, 1),
        "teams_involved": sorted(list(teams_needed)),
    }
