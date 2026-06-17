"""
Lifecycle Tracking Service
============================
Builds a complete chronological history of each infrastructure asset.

Timeline events include:
  - Construction / installation
  - Inspections
  - Maintenance actions
  - Citizen reports
  - Risk escalations
  - Status changes
"""

from typing import List, Dict, Optional
from datetime import date, datetime


EVENT_ICONS = {
    "construction": "🏗️",
    "inspection": "🔍",
    "maintenance": "🔧",
    "citizen_report": "📢",
    "risk_escalation": "⚠️",
    "status_change": "🔄",
    "decommission": "🚫",
}

EVENT_COLORS = {
    "construction": "#3b82f6",
    "inspection": "#8b5cf6",
    "maintenance": "#f59e0b",
    "citizen_report": "#ef4444",
    "risk_escalation": "#dc2626",
    "status_change": "#6b7280",
    "decommission": "#111827",
}


def build_lifecycle_timeline(
    asset: dict,
    maintenance_logs: List[dict],
    citizen_reports: List[dict],
    risk_history: Optional[List[dict]] = None
) -> List[dict]:
    """
    Constructs a chronological timeline of all lifecycle events for an asset.

    Args:
        asset: asset dict with id, asset_name, asset_type, installation_year, status
        maintenance_logs: list of maintenance log dicts
        citizen_reports: list of citizen report dicts
        risk_history: optional list of risk escalation events

    Returns:
        Sorted list of timeline event dicts.
    """
    events = []

    # 1. Construction / installation event
    construction_date = date(asset["installation_year"], 1, 1)
    events.append({
        "event_type": "construction",
        "date": construction_date.isoformat(),
        "date_obj": construction_date,
        "title": f"Asset Installed: {asset['asset_name']}",
        "description": f"{asset['asset_type'].replace('_', ' ').title()} constructed and commissioned.",
        "icon": EVENT_ICONS["construction"],
        "color": EVENT_COLORS["construction"],
        "severity": "info",
    })

    # 2. Maintenance / inspection events
    for log in maintenance_logs:
        insp_date = log.get("inspection_date")
        if isinstance(insp_date, str):
            insp_date = date.fromisoformat(insp_date)

        damage = log.get("damage_level", 0)
        if damage >= 7:
            event_type = "risk_escalation"
            severity = "critical"
        elif damage >= 4:
            event_type = "maintenance"
            severity = "warning"
        else:
            event_type = "inspection"
            severity = "info"

        events.append({
            "event_type": event_type,
            "date": insp_date.isoformat() if insp_date else "unknown",
            "date_obj": insp_date,
            "title": f"{event_type.replace('_', ' ').title()} by {log.get('inspector', 'Unknown')}",
            "description": (
                f"Damage Level: {damage}/10. "
                f"Action: {log.get('maintenance_action', 'None recorded')}. "
                f"Notes: {log.get('condition_notes', 'N/A')}"
            ),
            "icon": EVENT_ICONS[event_type],
            "color": EVENT_COLORS[event_type],
            "severity": severity,
            "damage_level": damage,
        })

    # 3. Citizen report events
    for report in citizen_reports:
        ts = report.get("timestamp")
        if isinstance(ts, str):
            try:
                report_date = datetime.fromisoformat(ts).date()
            except Exception:
                report_date = date.today()
        elif isinstance(ts, datetime):
            report_date = ts.date()
        else:
            report_date = date.today()

        severity_map = {"high": "critical", "medium": "warning", "low": "info"}
        severity = severity_map.get(report.get("severity", "low"), "info")

        events.append({
            "event_type": "citizen_report",
            "date": report_date.isoformat(),
            "date_obj": report_date,
            "title": f"Citizen Report: {report.get('report_type', 'Issue').replace('_', ' ').title()}",
            "description": report.get("description", "No description provided."),
            "icon": EVENT_ICONS["citizen_report"],
            "color": EVENT_COLORS["citizen_report"],
            "severity": severity,
        })

    # 4. Risk history events (if provided)
    if risk_history:
        for rh in risk_history:
            rh_date = rh.get("date", date.today())
            if isinstance(rh_date, str):
                rh_date = date.fromisoformat(rh_date)
            events.append({
                "event_type": "risk_escalation",
                "date": rh_date.isoformat(),
                "date_obj": rh_date,
                "title": f"Risk Escalated: {rh.get('from_level', '?')} → {rh.get('to_level', '?')}",
                "description": rh.get("reason", "Automated risk escalation detected."),
                "icon": EVENT_ICONS["risk_escalation"],
                "color": EVENT_COLORS["risk_escalation"],
                "severity": "critical",
            })

    # Sort chronologically
    events.sort(key=lambda e: e["date_obj"] or date.min)

    return events


def compute_lifecycle_stats(events: List[dict]) -> dict:
    """Compute summary statistics from lifecycle timeline."""
    total = len(events)
    inspections = sum(1 for e in events if e["event_type"] == "inspection")
    maintenance = sum(1 for e in events if e["event_type"] == "maintenance")
    reports = sum(1 for e in events if e["event_type"] == "citizen_report")
    escalations = sum(1 for e in events if e["event_type"] == "risk_escalation")

    if total > 0:
        first = events[0]["date"]
        last = events[-1]["date"]
    else:
        first = last = None

    return {
        "total_events": total,
        "inspections": inspections,
        "maintenance_actions": maintenance,
        "citizen_reports": reports,
        "risk_escalations": escalations,
        "timeline_start": first,
        "timeline_end": last,
    }


def get_asset_age_profile(installation_year: int, asset_type: str) -> dict:
    """Returns age profile information for an asset."""
    from app.services.health_engine import ASSET_DESIGN_LIFE
    current_year = date.today().year
    age = current_year - installation_year
    design_life = ASSET_DESIGN_LIFE.get(asset_type, 30)
    remaining = max(0, design_life - age)
    pct_life_used = min(100, round((age / design_life) * 100, 1))

    return {
        "installation_year": installation_year,
        "current_age_years": age,
        "design_life_years": design_life,
        "remaining_life_years": remaining,
        "percent_life_used": pct_life_used,
        "lifecycle_stage": (
            "new" if pct_life_used < 20
            else "mature" if pct_life_used < 60
            else "aging" if pct_life_used < 85
            else "end_of_life"
        )
    }
