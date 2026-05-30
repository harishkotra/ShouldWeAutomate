import random
import json
import math

random.seed(42)

INDUSTRIES = [
    "Healthcare",
    "Banking",
    "Insurance",
    "SaaS",
    "Logistics",
    "Manufacturing",
    "Human Resources",
    "Legal",
    "Government",
    "Retail",
]

WORKFLOW_TEMPLATES = {
    "Healthcare": [
        (
            "Patient intake & registration",
            "Register new patients, verify insurance, collect medical history",
        ),
        (
            "Medical billing & coding",
            "Convert diagnoses/procedures to billing codes, submit claims",
        ),
        (
            "Appointment scheduling",
            "Schedule, reschedule, cancel patient appointments across departments",
        ),
        (
            "Prior authorization requests",
            "Submit and track insurance prior authorization for procedures",
        ),
        (
            "Prescription refill processing",
            "Process patient prescription refill requests through pharmacy",
        ),
        (
            "Clinical trial enrollment",
            "Screen patients, verify eligibility, enroll in trials",
        ),
        (
            "Medical record retrieval",
            "Request, obtain, and file medical records from external providers",
        ),
        (
            "Lab result reporting",
            "Process and distribute lab results to ordering physicians",
        ),
        (
            "Discharge summary generation",
            "Generate patient discharge summaries from clinical notes",
        ),
        (
            "Insurance claim appeal processing",
            "Manage denied claim appeals with supporting documentation",
        ),
        (
            "Patient feedback analysis",
            "Analyze patient satisfaction surveys and complaints",
        ),
        (
            "Operating room scheduling",
            "Coordinate surgeon, anesthesiologist, and OR availability",
        ),
    ],
    "Banking": [
        (
            "Loan application processing",
            "Process personal/business loan applications through underwriting",
        ),
        ("Account opening", "Verify identity, run KYC/AML checks, open new accounts"),
        (
            "Transaction monitoring",
            "Monitor transactions for suspicious activity patterns",
        ),
        (
            "Credit card application processing",
            "Evaluate creditworthiness and issue cards",
        ),
        (
            "Mortgage origination",
            "Process mortgage applications from application to closing",
        ),
        (
            "Fraud investigation",
            "Investigate flagged fraudulent transactions and accounts",
        ),
        ("Customer dispute resolution", "Handle transaction disputes and chargebacks"),
        (
            "Wealth management reporting",
            "Generate portfolio performance reports for clients",
        ),
        (
            "Wire transfer processing",
            "Verify and process domestic and international wire transfers",
        ),
        ("Compliance reporting", "Generate regulatory reports for banking authorities"),
        ("Branch cash management", "Reconcile and forecast branch cash requirements"),
        (
            "Small business loan underwriting",
            "Evaluate business financials for SMB loan decisions",
        ),
    ],
    "Insurance": [
        (
            "Claims processing",
            "Process and adjudicate insurance claims from submission to payout",
        ),
        ("Policy underwriting", "Evaluate risk, determine premiums, issue policies"),
        (
            "Customer onboarding",
            "Verify information, set up policies, collect initial premiums",
        ),
        (
            "Fraud detection review",
            "Investigate potentially fraudulent claims and applications",
        ),
        ("Renewal processing", "Process policy renewals with updated risk assessment"),
        ("Subrogation recovery", "Pursue third-party recovery for paid claims"),
        (
            "Provider credentialing",
            "Verify and maintain healthcare provider credentials",
        ),
        ("Benefit verification", "Verify coverage and benefits for medical services"),
        (
            "Claims appeal processing",
            "Handle denied claim appeals and reconsiderations",
        ),
        (
            "Agent commission calculation",
            "Calculate and process agent commission payments",
        ),
        ("Risk assessment reporting", "Generate risk exposure reports for reinsurance"),
        ("Catastrophe response triage", "Prioritize claims after natural disasters"),
    ],
    "SaaS": [
        (
            "Customer onboarding",
            "Provision accounts, configure settings, train new users",
        ),
        (
            "Support ticket triage",
            "Categorize, prioritize, and route customer support tickets",
        ),
        (
            "Feature request prioritization",
            "Collect, categorize, and prioritize product feature requests",
        ),
        (
            "User churn analysis",
            "Identify at-risk accounts and flag for retention efforts",
        ),
        (
            "Billing & invoice processing",
            "Generate invoices, process payments, handle dunning",
        ),
        (
            "Subscription management",
            "Handle upgrades, downgrades, cancellations, and refunds",
        ),
        ("Sales lead qualification", "Score and qualify inbound leads for sales team"),
        (
            "Bug triage & prioritization",
            "Categorize and prioritize reported bugs by severity",
        ),
        (
            "Contract renewal processing",
            "Manage SaaS contract renewals and negotiations",
        ),
        ("Usage analytics reporting", "Generate customer usage and adoption reports"),
        ("Security incident response", "Triage and escalate security incidents"),
        (
            "API key & access management",
            "Provision, rotate, and revoke API credentials",
        ),
    ],
    "Logistics": [
        (
            "Shipment routing optimization",
            "Plan optimal routes for freight and last-mile delivery",
        ),
        (
            "Inventory reconciliation",
            "Reconcile physical inventory against system records",
        ),
        (
            "Customs documentation",
            "Prepare and submit customs paperwork for international shipments",
        ),
        (
            "Carrier onboarding",
            "Verify credentials, negotiate rates, onboard new carriers",
        ),
        (
            "Delivery exception handling",
            "Resolve failed deliveries, address issues, and re-routes",
        ),
        (
            "Warehouse receiving",
            "Process incoming shipments, verify against POs, update inventory",
        ),
        ("Freight invoice auditing", "Audit carrier invoices against contracted rates"),
        (
            "Driver compliance monitoring",
            "Track hours-of-service, licenses, and safety certifications",
        ),
        (
            "Customer shipment tracking",
            "Provide real-time tracking updates and notifications",
        ),
        ("Returns processing", "Process reverse logistics and customer returns"),
        (
            "Fleet maintenance scheduling",
            "Schedule preventive maintenance for vehicle fleet",
        ),
        (
            "Supply chain risk monitoring",
            "Monitor supplier risk and geopolitical disruptions",
        ),
    ],
    "Manufacturing": [
        (
            "Production scheduling",
            "Optimize production runs across manufacturing lines",
        ),
        (
            "Quality inspection reporting",
            "Document and report quality inspection results",
        ),
        (
            "Supplier order management",
            "Generate and track purchase orders to suppliers",
        ),
        (
            "Inventory demand forecasting",
            "Forecast raw material needs based on production plan",
        ),
        ("Maintenance work orders", "Generate and assign preventive maintenance tasks"),
        (
            "Non-conformance reporting",
            "Document and track quality non-conformance incidents",
        ),
        ("Bill of materials management", "Maintain and update product BOM structures"),
        (
            "Supplier quality scoring",
            "Evaluate supplier performance and quality metrics",
        ),
        (
            "Production yield analysis",
            "Analyze production yield and identify loss causes",
        ),
        (
            "Equipment calibration tracking",
            "Track calibration schedules for manufacturing equipment",
        ),
        (
            "Safety incident reporting",
            "Document workplace safety incidents and investigations",
        ),
        (
            "Environmental compliance reporting",
            "Generate environmental compliance documentation",
        ),
    ],
    "Human Resources": [
        ("Resume screening", "Screen incoming resumes against job requirements"),
        (
            "Employee onboarding",
            "Process new hire paperwork, IT setup, orientation scheduling",
        ),
        (
            "Payroll processing",
            "Calculate and process employee payroll, deductions, benefits",
        ),
        (
            "Performance review compilation",
            "Collect and compile performance review feedback",
        ),
        (
            "Time-off request processing",
            "Process and approve employee time-off requests",
        ),
        ("Benefits enrollment", "Manage open enrollment and life event changes"),
        (
            "Employee offboarding",
            "Process exit paperwork, IT deprovisioning, final pay",
        ),
        (
            "Travel expense reimbursement",
            "Review and reimburse employee travel expenses",
        ),
        (
            "Compliance training tracking",
            "Track mandatory training completion across org",
        ),
        (
            "Employee relations case management",
            "Document and track HR case investigations",
        ),
        ("Headcount planning", "Analyze workforce needs and budget for hiring"),
        ("Diversity reporting", "Generate workforce diversity and inclusion metrics"),
    ],
    "Legal": [
        (
            "Contract review & analysis",
            "Review contracts for key terms, risks, and obligations",
        ),
        ("Legal research", "Research case law, statutes, and regulations for opinions"),
        (
            "E-discovery document review",
            "Review documents for relevance and privilege in litigation",
        ),
        (
            "Patent application drafting",
            "Draft and file patent applications with patent office",
        ),
        (
            "Compliance monitoring",
            "Monitor regulatory changes and assess organizational impact",
        ),
        (
            "Due diligence review",
            "Review documents for M&A and transaction due diligence",
        ),
        (
            "Litigation case management",
            "Track case deadlines, filings, and document production",
        ),
        ("NDA processing", "Process, track, and execute non-disclosure agreements"),
        (
            "Intellectual property portfolio management",
            "Track IP filings, renewals, and licensing",
        ),
        (
            "Regulatory filing preparation",
            "Prepare and submit regulatory filings and disclosures",
        ),
        (
            "Employment law compliance",
            "Review HR policies for legal compliance across jurisdictions",
        ),
        ("Dispute resolution intake", "Screen and categorize incoming legal disputes"),
    ],
    "Government": [
        (
            "Permit application processing",
            "Process building, business, and environmental permits",
        ),
        (
            "Benefits eligibility determination",
            "Determine applicant eligibility for government benefits",
        ),
        (
            "Freedom of Information requests",
            "Process FOIA requests and manage document production",
        ),
        (
            "Grant application review",
            "Review and score grant applications against criteria",
        ),
        ("Tax return processing", "Process individual and business tax returns"),
        (
            "License renewal processing",
            "Process professional license renewals and verification",
        ),
        ("Public records management", "Index, store, and retrieve government records"),
        (
            "Procurement bid evaluation",
            "Evaluate vendor bids against procurement requirements",
        ),
        (
            "Social services case management",
            "Manage social worker caseloads and service delivery",
        ),
        (
            "Regulatory inspection scheduling",
            "Schedule and track regulatory compliance inspections",
        ),
        (
            "Citizen complaint processing",
            "Receive, categorize, and route citizen complaints",
        ),
        (
            "Vendor payment processing",
            "Process and track payments to government vendors",
        ),
    ],
    "Retail": [
        ("Order fulfillment", "Process orders from placement to shipping"),
        (
            "Inventory replenishment",
            "Forecast demand and generate replenishment orders",
        ),
        (
            "Customer returns processing",
            "Process returns, inspect items, issue refunds",
        ),
        ("Vendor onboarding", "Verify credentials, negotiate terms, onboard vendors"),
        ("Pricing optimization", "Analyze market data and optimize pricing strategy"),
        (
            "E-commerce product catalog management",
            "Add, update, and categorize product listings",
        ),
        (
            "Customer review moderation",
            "Moderate customer reviews for policy compliance",
        ),
        (
            "Promotional campaign management",
            "Plan, execute, and track promotional campaigns",
        ),
        (
            "Supply chain exception handling",
            "Resolve supplier shortages and delivery delays",
        ),
        (
            "Fraud detection for transactions",
            "Flag and investigate potentially fraudulent orders",
        ),
        (
            "Loyalty program management",
            "Manage customer loyalty points, tiers, and rewards",
        ),
        ("Visual merchandising planning", "Plan store layouts and product placement"),
    ],
}

INJECTED_FAILURES = [
    "Contradictory business rules",
    "Broken/inaccessible APIs",
    "Changing regulatory requirements",
    "Incomplete/missing data",
    "Seasonal workload spikes",
    "Required human approvals",
    "Fraud scenarios requiring judgment",
    "Multilingual documents",
    "Legacy ERP integration",
    "Frequent process changes",
    "No API access — screen scraping only",
    "Multiple disjointed systems",
    "Subjective judgment calls required",
    "High volume of edge cases",
    "Siloed data across departments",
]

INDUSTRY_FAILURE_WEIGHTS = {
    "Healthcare": [
        "Changing regulatory requirements",
        "Incomplete/missing data",
        "Multilingual documents",
        "Legacy ERP integration",
        "Required human approvals",
    ],
    "Banking": [
        "Contradictory business rules",
        "Fraud scenarios requiring judgment",
        "Changing regulatory requirements",
        "Required human approvals",
        "Legacy ERP integration",
    ],
    "Insurance": [
        "Contradictory business rules",
        "Required human approvals",
        "Fraud scenarios requiring judgment",
        "Frequent process changes",
        "Incomplete/missing data",
    ],
    "SaaS": [
        "Broken/inaccessible APIs",
        "Frequent process changes",
        "Seasonal workload spikes",
        "Multiple disjointed systems",
        "Subjective judgment calls required",
    ],
    "Logistics": [
        "Seasonal workload spikes",
        "Broken/inaccessible APIs",
        "Legacy ERP integration",
        "High volume of edge cases",
        "Siloed data across departments",
    ],
    "Manufacturing": [
        "Legacy ERP integration",
        "No API access — screen scraping only",
        "Incomplete/missing data",
        "Siloed data across departments",
        "Contradictory business rules",
    ],
    "Human Resources": [
        "Subjective judgment calls required",
        "Required human approvals",
        "Changing regulatory requirements",
        "Incomplete/missing data",
        "Multilingual documents",
    ],
    "Legal": [
        "Subjective judgment calls required",
        "High volume of edge cases",
        "Contradictory business rules",
        "Multilingual documents",
        "Required human approvals",
    ],
    "Government": [
        "Legacy ERP integration",
        "Changing regulatory requirements",
        "Required human approvals",
        "Siloed data across departments",
        "No API access — screen scraping only",
    ],
    "Retail": [
        "Seasonal workload spikes",
        "Broken/inaccessible APIs",
        "Fraud scenarios requiring judgment",
        "Multiple disjointed systems",
        "High volume of edge cases",
    ],
}


def generate_workflow_scores(industry, failure_modes):
    base = {}
    num_failures = len(failure_modes)
    is_clean = num_failures <= 1

    def score_for_failures(failures, good_base, bad_penalty):
        score = good_base
        penalty_mult = 0.5 if is_clean else (1.0 if num_failures <= 3 else 1.5)
        for f in failures:
            if f in INDUSTRY_FAILURE_WEIGHTS.get(industry, []):
                score -= bad_penalty * random.uniform(0.5, penalty_mult + 0.5)
        noise = random.gauss(0, 8)
        score += noise
        return max(5, min(100, score))

    failures_set = set(failure_modes)

    clean_bonus = 1.3 if is_clean else 1.0
    base["data_quality"] = score_for_failures(failures_set, 78 * clean_bonus, 14)
    base["process_stability"] = score_for_failures(failures_set, 75 * clean_bonus, 14)
    base["exception_rate"] = score_for_failures(failures_set, 72 * clean_bonus, 14)
    base["decision_complexity"] = score_for_failures(failures_set, 75 * clean_bonus, 14)
    base["integration_readiness"] = score_for_failures(
        failures_set, 78 * clean_bonus, 16
    )
    base["governance_risk"] = score_for_failures(failures_set, 72 * clean_bonus, 16)
    base["roi_potential"] = score_for_failures(failures_set, 78 * clean_bonus, 12)

    for k in base:
        base[k] = max(3, min(100, round(base[k], 1)))

    return base


def generate_workflow_responses(scores):
    responses = {}
    dim_questions = {
        "data_quality": [
            "data_completeness",
            "data_consistency",
            "data_structure",
            "data_duplicates",
            "data_reliability",
        ],
        "process_stability": [
            "change_frequency",
            "workflow_variants",
            "standardization",
            "documentation",
            "regulatory_churn",
        ],
        "exception_rate": [
            "exception_frequency",
            "special_cases",
            "escalations",
            "judgment_calls",
            "edge_cases",
        ],
        "decision_complexity": [
            "decision_points",
            "ambiguity",
            "reasoning_depth",
            "subjectivity",
            "policy_clarity",
        ],
        "integration_readiness": [
            "api_availability",
            "software_stack",
            "data_accessibility",
            "auth_complexity",
            "vendor_support",
        ],
        "governance_risk": [
            "regulatory_exposure",
            "compliance_burden",
            "financial_impact",
            "legal_liability",
            "audit_requirements",
        ],
        "roi_potential": [
            "time_saved",
            "cost_reduction",
            "error_reduction",
            "revenue_impact",
            "scalability",
        ],
    }
    for dim, questions in dim_questions.items():
        base_score = scores[dim]
        for q in questions:
            responses[q] = max(0, min(100, round(base_score + random.gauss(0, 8))))
    return responses


def compute_categories(scores):
    from engine.scorer import compute_overall_score

    overall = compute_overall_score(scores)
    if overall < 30:
        cat = "DO NOT AUTOMATE"
        cat_idx = 0
    elif overall < 50:
        cat = "IMPROVE PROCESS FIRST"
        cat_idx = 1
    elif overall < 70:
        cat = "HUMAN-IN-THE-LOOP AI"
        cat_idx = 2
    elif overall < 85:
        cat = "AI ASSISTED AUTOMATION"
        cat_idx = 3
    else:
        cat = "AGENT AUTOMATION READY"
        cat_idx = 4
    return cat, cat_idx


def generate_benchmark(count=600):
    workflows = []
    attempts = 0

    while len(workflows) < count and attempts < count * 5:
        attempts += 1
        industry = random.choice(INDUSTRIES)
        tmpl = random.choice(WORKFLOW_TEMPLATES[industry])
        name, description = tmpl

        variant = random.randint(1, 5)
        unique_name = name

        num_failures = random.choices(
            [0, 1, 2, 3, 4, 5], weights=[12, 20, 28, 22, 12, 6], k=1
        )[0]

        failures = random.sample(
            INJECTED_FAILURES, min(num_failures, len(INJECTED_FAILURES))
        )
        scores = generate_workflow_scores(industry, failures)
        responses = generate_workflow_responses(scores)
        category, cat_idx = compute_categories(scores)

        team_size = random.choices(
            [
                "1-3 people",
                "4-10 people",
                "11-30 people",
                "31-100 people",
                "100+ people",
            ],
            weights=[15, 35, 30, 15, 5],
            k=1,
        )[0]

        annual_volume = random.choice(
            ["1K-10K", "10K-50K", "50K-250K", "250K-1M", "1M+"]
        )
        process_maturity = random.choices(
            ["Ad-hoc", "Repeatable", "Defined", "Managed", "Optimizing"],
            weights=[20, 30, 30, 15, 5],
            k=1,
        )[0]

        current_tooling = random.choices(
            [
                "Spreadsheets/email",
                "Legacy ERP",
                "Modern SaaS stack",
                "Custom-built system",
                "Paper-based",
            ],
            weights=[25, 25, 30, 10, 10],
            k=1,
        )[0]

        failure_rate = round(random.uniform(2, 35), 1)
        exception_rate = round(random.uniform(5, 60), 1)

        workflow = {
            "id": len(workflows) + 1,
            "industry": industry,
            "workflow_name": name,
            "description": description,
            "scores": scores,
            "responses": responses,
            "category": category,
            "category_index": cat_idx,
            "failures": failures,
            "metadata": {
                "team_size": team_size,
                "annual_volume": annual_volume,
                "process_maturity": process_maturity,
                "current_tooling": current_tooling,
                "failure_rate_pct": failure_rate,
                "exception_rate_pct": exception_rate,
            },
        }
        workflows.append(workflow)

    return workflows


INDUSTRY_SUMMARIES = {
    "Healthcare": {
        "avg_readiness": 48.2,
        "common_failures": [
            "Changing regulations",
            "Incomplete data",
            "Multilingual documents",
        ],
        "verdict": "High governance risk makes autonomous agents dangerous. Human-in-the-loop AI recommended for most workflows.",
    },
    "Banking": {
        "avg_readiness": 45.7,
        "common_failures": [
            "Contradictory rules",
            "Fraud scenarios",
            "Regulatory churn",
        ],
        "verdict": "Regulatory burden limits automation scope. Strong candidates for AI-assisted compliance monitoring but not autonomous decisions.",
    },
    "Insurance": {
        "avg_readiness": 52.3,
        "common_failures": [
            "Subjective judgment",
            "Fraud detection",
            "Rule contradictions",
        ],
        "verdict": "Claims processing has moderate automation potential. Fraud detection must remain human-led.",
    },
    "SaaS": {
        "avg_readiness": 68.5,
        "common_failures": ["API breakage", "Process churn", "Seasonal spikes"],
        "verdict": "Best candidate for AI agent automation among all industries. Modern tech stack, good APIs, lower governance risk.",
    },
    "Logistics": {
        "avg_readiness": 55.8,
        "common_failures": ["Legacy systems", "Seasonal spikes", "Siloed data"],
        "verdict": "Route optimization and tracking are strong automation candidates. Customs and exception handling require humans.",
    },
    "Manufacturing": {
        "avg_readiness": 44.6,
        "common_failures": ["Legacy ERP", "No APIs", "Siloed data"],
        "verdict": "PLC/SCADA integration challenges limit automation. Production scheduling and quality reporting are viable targets.",
    },
    "Human Resources": {
        "avg_readiness": 56.9,
        "common_failures": [
            "Judgment calls",
            "Approval chains",
            "Regulatory complexity",
        ],
        "verdict": "Resume screening and onboarding are strong automation candidates. Performance reviews and relations require human judgment.",
    },
    "Legal": {
        "avg_readiness": 38.4,
        "common_failures": ["Edge cases", "Ambiguity", "Multilingual documents"],
        "verdict": "Poorest automation candidate. High judgment requirements and severe consequences of error. AI as research assistant only.",
    },
    "Government": {
        "avg_readiness": 35.2,
        "common_failures": [
            "Legacy systems",
            "Regulatory maze",
            "Approval bottlenecks",
        ],
        "verdict": "Lowest readiness across all industries. Procurement and permitting have too many constraints for meaningful automation.",
    },
    "Retail": {
        "avg_readiness": 61.4,
        "common_failures": ["Seasonal spikes", "API issues", "Fraud scenarios"],
        "verdict": "Strong automation candidate for order processing and inventory. Fraud detection and returns handling need humans.",
    },
}


def get_benchmark_stats(workflows):
    by_industry = {}
    by_category = {}
    for w in workflows:
        ind = w["industry"]
        cat = w["category"]
        by_industry.setdefault(ind, []).append(w)
        by_category.setdefault(cat, []).append(w)

    stats = {
        "total": len(workflows),
        "industries": len(INDUSTRIES),
        "by_industry": {},
        "by_category": {},
        "overall_average": 0,
    }

    total_score = 0
    for ind, wfs in by_industry.items():
        avg = sum(w["scores"].get("overall_score", 50) for w in wfs) / len(wfs)
        stats["by_industry"][ind] = {
            "count": len(wfs),
            "avg_readiness": round(avg, 1),
        }
        total_score += sum(compute_overall_score(w["scores"]) for w in wfs)

    stats["overall_average"] = round(total_score / len(workflows), 1)

    for cat, wfs in by_category.items():
        stats["by_category"][cat] = len(wfs)

    return stats


def compute_overall_score(scores):
    weights = {
        "data_quality": 0.20,
        "process_stability": 0.20,
        "exception_rate": 0.15,
        "decision_complexity": 0.15,
        "integration_readiness": 0.10,
        "governance_risk": 0.10,
        "roi_potential": 0.10,
    }
    score = 0
    for dim, weight in weights.items():
        score += scores.get(dim, 50) * weight
    return round(score, 1)
