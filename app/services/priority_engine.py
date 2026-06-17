"""
Maintenance Priority Engine
============================
Ranks infrastructure assets by urgency to optimize resource allocation.

Priority Formula:
  priority_score = 0.4 × safety_risk
                 + 0.3 × population_impact
                 + 0.2 × infrastructure_importance
                 + 0.1 × repair_cost_urgency

Returns assets ranked highest-to-lowest priority.
"""

from typing import List, Dict
import math

WEIGHT_SAFETY = 0.40
WEIGHT_POPULATION = 0.30
WEIGHT_IMPORTANCE = 0.20
WEIGHT_COST = 0.10

# Asset type importance scores (0–100)
ASSET_IMPORTANCE = {
    "bridge": 95,
    "road": 85,
    "pipeline": 90,
    "drainage": 75,
    "street_light": 40,
    "public_facility": 60,
}

# Estimated population impact multipliers
POPULATION_IMPACT_FACTORS = {
    "bridge": 90,       # Disrupts routes for many
    "road": 80,         # High daily usage
    "pipeline": 95,     # Water/gas affects thousands
    "drainage": 70,     # Flooding impact
    "street_light": 30, # Safety at night, lower impact
    "public_facility": 55,
}

# Cost urgency: higher means cheaper to fix now vs later (prevent escalation)
REPAIR_COST_URGENCY = {
    "bridge": 90,          # Very expensive if neglected
    "road": 70,
    "pipeline": 85,
    "drainage": 65,
    "street_light": 50,
    "public_facility": 60,
}

ACTION_MATRIX = {
    (True, True): "EMERGENCY: Immediate shutdown & repair",
    (True, False): "URGENT: Schedule repair within 7 days",
    (False, True): "HIGH PRIORITY: Plan repair within 30 days",
    (False, False): "MONITOR: Schedule within 90 days",
}


def compute_safety_risk_score(health_score: float, risk_level: str, propagated_delta: float = 0) -> float:
    """Combines direct health score with any cascaded risk."""
    base = health_score
    cascade_bonus = min(20, propagated_delta * 0.5)
    score = min(100, base + cascade_bonus)

    # Amplify critical assets
    if risk_level == "critical":
        score = min(100, score * 1.15)
    return round(score, 2)


def compute_population_impact(asset_type: str, citizen_reports: int) -> float:
    """Population impact based on asset type + number of citizen reports."""
    base = POPULATION_IMPACT_FACTORS.get(asset_type, 50)
    # More reports = more people affected
    report_boost = min(20, citizen_reports * 2)
    return min(100, base + report_boost)


def compute_infrastructure_importance(asset_type: str, connections_count: int) -> float:
    """
    More connected assets have greater systemic importance.
    """
    base = ASSET_IMPORTANCE.get(asset_type, 50)
    # Each connection adds marginal importance
    connection_boost = min(15, connections_count * 3)
    return min(100, base + connection_boost)


def compute_cost_urgency(asset_type: str, age_years: int) -> float:
    """
    Older assets cost more to repair later than now.
    """
    base = REPAIR_COST_URGENCY.get(asset_type, 60)
    # Age increases urgency (diminishing returns)
    age_factor = min(20, 20 * (1 - math.exp(-age_years / 30)))
    return min(100, base + age_factor)


def calculate_priority_score(
    health_score: float,
    risk_level: str,
    asset_type: str,
    age_years: int,
    citizen_reports: int,
    connections_count: int,
    propagated_delta: float = 0.0
) -> dict:
    """
    Full priority score calculation.
    Returns priority_score (0–100) and component breakdown.
    """
    safety = compute_safety_risk_score(health_score, risk_level, propagated_delta)
    population = compute_population_impact(asset_type, citizen_reports)
    importance = compute_infrastructure_importance(asset_type, connections_count)
    cost = compute_cost_urgency(asset_type, age_years)

    priority_score = (
        WEIGHT_SAFETY * safety
        + WEIGHT_POPULATION * population
        + WEIGHT_IMPORTANCE * importance
        + WEIGHT_COST * cost
    )
    priority_score = round(min(100, priority_score), 2)

    is_critical = risk_level == "critical"
    has_high_impact = population >= 70 or importance >= 80

    action = ACTION_MATRIX.get(
        (is_critical, has_high_impact),
        "SCHEDULE: Review within 90 days"
    )

    return {
        "priority_score": priority_score,
        "action": action,
        "breakdown": {
            "safety_risk": safety,
            "population_impact": population,
            "infrastructure_importance": importance,
            "cost_urgency": cost,
        }
    }


def rank_assets_by_priority(assets_data: List[Dict]) -> List[Dict]:
    """
    Input: list of asset dicts with fields needed for scoring.
    Output: list ranked by priority_score descending, with rank field.
    """
    scored = []
    for asset in assets_data:
        from datetime import date
        age = date.today().year - asset.get("installation_year", 2010)
        result = calculate_priority_score(
            health_score=asset.get("health_score", 0),
            risk_level=asset.get("risk_level", "healthy"),
            asset_type=asset.get("asset_type", "road"),
            age_years=age,
            citizen_reports=asset.get("citizen_report_count", 0),
            connections_count=asset.get("connections_count", 0),
            propagated_delta=asset.get("propagated_delta", 0.0),
        )
        scored.append({
            **asset,
            "priority_score": result["priority_score"],
            "recommended_action": result["action"],
            "priority_breakdown": result["breakdown"],
        })

    scored.sort(key=lambda x: x["priority_score"], reverse=True)

    for i, item in enumerate(scored, start=1):
        item["rank"] = i

    return scored
