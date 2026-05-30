from engine.scorer import (
    SCORING_DEFAULTS,
    compute_dimension_score,
    compute_overall_score,
)


class SubProcess:
    def __init__(self, name, description="", weight=1.0, responses=None):
        self.name = name
        self.description = description
        self.weight = weight
        self.responses = responses or {}

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "responses": self.responses,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", "Unnamed"),
            description=data.get("description", ""),
            weight=data.get("weight", 1.0),
            responses=data.get("responses", {}),
        )

    def get_dimension_scores(self):
        scores = {}
        for dim in SCORING_DEFAULTS:
            scores[dim] = round(compute_dimension_score(self.responses, dim), 1)
        return scores

    def get_overall_score(self):
        return compute_overall_score(self.get_dimension_scores())


def decompose_workflow(workflow_responses, sub_processes=None):
    if not sub_processes:
        return [SubProcess("Main Process", "Primary workflow", 1.0, workflow_responses)]
    return [SubProcess.from_dict(sp) for sp in sub_processes]


def compute_aggregate_scores(sub_processes):
    if not sub_processes:
        return {}
    aggregate = {}
    for dim in SCORING_DEFAULTS:
        weighted_sum = 0
        total_weight = 0
        for sp in sub_processes:
            scores = sp.get_dimension_scores()
            weighted_sum += scores[dim] * sp.weight
            total_weight += sp.weight
        aggregate[dim] = round(weighted_sum / total_weight if total_weight else 0, 1)
    return aggregate


def compute_aggregate_overall(sub_processes):
    dim_scores = compute_aggregate_scores(sub_processes)
    return compute_overall_score(dim_scores)


def find_decomposition_opportunities(sub_processes):
    opportunities = []
    for sp in sub_processes:
        scores = sp.get_dimension_scores()
        overall = sp.get_overall_score()

        if overall >= 80:
            opp = {
                "sub_process": sp.name,
                "opportunity": "Strong candidate for autonomous agent automation",
                "suggested_architecture": "Single agent or multi-agent system",
                "priority": "High",
                "readiness": "Ready",
            }
        elif overall >= 60:
            opp = {
                "sub_process": sp.name,
                "opportunity": "Good candidate for AI-assisted automation with human oversight",
                "suggested_architecture": "Human-in-the-loop AI assistant",
                "priority": "Medium",
                "readiness": "Partial",
            }
        elif overall >= 40:
            opp = {
                "sub_process": sp.name,
                "opportunity": "Process improvement needed before automation",
                "suggested_architecture": "Process standardization first",
                "priority": "Low",
                "readiness": "Needs Improvement",
            }
        else:
            opp = {
                "sub_process": sp.name,
                "opportunity": "Not suitable for automation - fundamental operational problems",
                "suggested_architecture": "No automation recommended",
                "priority": "None",
                "readiness": "Not Ready",
            }

        low_dims = [(k, v) for k, v in scores.items() if v < 40]
        opp["blockers"] = (
            [f"{dim.replace('_', ' ').title()} ({score})" for dim, score in low_dims]
            if low_dims
            else []
        )
        opportunities.append(opp)

    priority_order = {"High": 0, "Medium": 1, "Low": 2, "None": 3}
    return sorted(opportunities, key=lambda x: priority_order.get(x["priority"], 99))


def get_dimensional_breakdown(sub_processes):
    breakdown = {}
    for sp in sub_processes:
        breakdown[sp.name] = sp.get_dimension_scores()
    return breakdown
