"""
Infrastructure Health Scoring Engine
=====================================
Evaluates asset health using a weighted formula combining:
- Asset age (normalized decay curve)
- Inspection delay (days since last inspection)
- Damage reports (from maintenance logs and citizen reports)
- Maintenance frequency (recency and count of maintenance)

Score Range: 0 (best) to 100 (worst)
Classifications:
  0–30   → Healthy (Green)
  31–60  → Warning (Yellow)
  61–100 → Critical (Red)
"""

from datetime import date, timedelta
from typing import Optional, List
import math


WEIGHT_AGE = 0.40
WEIGHT_INSPECTION_DELAY = 0.30
WEIGHT_DAMAGE = 0.20
WEIGHT_MAINTENANCE = 0.10

HEALTHY_MAX = 30
WARNING_MAX = 60
# Above 60 = Critical

ASSET_DESIGN_LIFE = {
    "road": 20,
    "bridge": 50,
    "pipeline": 40,
    "drainage": 30,
    "street_light": 15,
    "public_facility": 40,
}

INSPECTION_STANDARD_DAYS = {
    "road": 180,
    "bridge": 365,
    "pipeline": 365,
    "drainage": 180,
    "street_light": 730,
    "public_facility": 365,
}


def compute_age_score(installation_year: int, asset_type: str) -> float:
    """
    Returns a 0–100 score representing aging degradation.
    Uses a logarithmic curve to model infrastructure decay.
    """
    current_year = date.today().year
    age = max(0, current_year - installation_year)
    design_life = ASSET_DESIGN_LIFE.get(asset_type, 30)

    age_ratio = age / design_life
    # Logarithmic decay: slow at first, accelerates as age approaches design life
    score = min(100, 100 * (1 - math.exp(-2.5 * age_ratio)))
    return round(score, 2)


def compute_inspection_delay_score(last_inspection_date: Optional[date], asset_type: str) -> float:
    """
    Returns 0–100 score based on how overdue inspection is.
    0 = inspected recently, 100 = severely overdue.
    """
    if last_inspection_date is None:
        return 90.0  # Never inspected = high risk

    today = date.today()
    days_since = (today - last_inspection_date).days
    standard_interval = INSPECTION_STANDARD_DAYS.get(asset_type, 365)

    ratio = days_since / standard_interval
    score = min(100, ratio * 60)  # cap at 100, but 60 at exactly 1 interval
    return round(score, 2)


def compute_damage_score(damage_levels: List[float], citizen_report_count: int) -> float:
    """
    Returns 0–100 score from maintenance damage assessments + citizen reports.
    """
    if not damage_levels and citizen_report_count == 0:
        return 0.0

    # Average damage level from maintenance logs (0–10 scale → 0–100)
    avg_damage = (sum(damage_levels) / len(damage_levels) * 10) if damage_levels else 0.0

    # Citizen reports add noise/urgency
    report_penalty = min(30, citizen_report_count * 5)

    score = min(100, avg_damage + report_penalty)
    return round(score, 2)


def compute_maintenance_frequency_score(
    maintenance_dates: List[date],
    asset_type: str
) -> float:
    """
    Returns 0–100 score; lower = more recently/frequently maintained.
    Assets that haven't been maintained recently score higher (worse).
    """
    if not maintenance_dates:
        return 80.0

    today = date.today()
    most_recent = max(maintenance_dates)
    days_since_maintenance = (today - most_recent).days
    standard_interval = INSPECTION_STANDARD_DAYS.get(asset_type, 365)

    ratio = days_since_maintenance / standard_interval
    score = min(100, ratio * 50)
    return round(score, 2)


def calculate_health_score(
    installation_year: int,
    asset_type: str,
    last_inspection_date: Optional[date],
    damage_levels: List[float],
    citizen_report_count: int,
    maintenance_dates: List[date]
) -> dict:
    """
    Master health score calculator.
    Returns health_score (0–100) and risk_level classification.
    """
    age_score = compute_age_score(installation_year, asset_type)
    inspection_score = compute_inspection_delay_score(last_inspection_date, asset_type)
    damage_score = compute_damage_score(damage_levels, citizen_report_count)
    maintenance_score = compute_maintenance_frequency_score(maintenance_dates, asset_type)

    health_score = (
        WEIGHT_AGE * age_score
        + WEIGHT_INSPECTION_DELAY * inspection_score
        + WEIGHT_DAMAGE * damage_score
        + WEIGHT_MAINTENANCE * maintenance_score
    )
    health_score = round(min(100, max(0, health_score)), 2)

    if health_score <= HEALTHY_MAX:
        risk_level = "healthy"
    elif health_score <= WARNING_MAX:
        risk_level = "warning"
    else:
        risk_level = "critical"

    return {
        "health_score": health_score,
        "risk_level": risk_level,
        "breakdown": {
            "age_score": age_score,
            "inspection_delay_score": inspection_score,
            "damage_score": damage_score,
            "maintenance_score": maintenance_score,
        }
    }


def get_risk_color(risk_level: str) -> str:
    colors = {
        "healthy": "#22c55e",
        "warning": "#eab308",
        "critical": "#ef4444"
    }
    return colors.get(risk_level, "#6b7280")


def get_recommended_action(health_score: float, risk_level: str) -> str:
    if risk_level == "critical":
        if health_score >= 80:
            return "IMMEDIATE INTERVENTION: Emergency repair required. Close to traffic/use."
        return "URGENT: Schedule priority repair within 7 days. Increase inspection frequency."
    elif risk_level == "warning":
        return "SCHEDULE MAINTENANCE: Plan repair within 30–90 days. Monitor closely."
    else:
        return "ROUTINE: Continue standard inspection cycle. No immediate action needed."
