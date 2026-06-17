from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.database import get_db
from app.models.asset_model import InfrastructureAsset
from app.models.maintenance_model import MaintenanceLog, CitizenReport
from app.models.connection_model import AssetConnection
from app.services.risk_propagation import compute_network_risk, get_cascade_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    total = db.query(InfrastructureAsset).count()
    healthy = db.query(InfrastructureAsset).filter(InfrastructureAsset.risk_level == "healthy").count()
    warning = db.query(InfrastructureAsset).filter(InfrastructureAsset.risk_level == "warning").count()
    critical = db.query(InfrastructureAsset).filter(InfrastructureAsset.risk_level == "critical").count()

    today = date.today()
    overdue_threshold = today - timedelta(days=365)
    overdue = db.query(InfrastructureAsset).filter(
        (InfrastructureAsset.last_inspection_date < overdue_threshold) |
        (InfrastructureAsset.last_inspection_date == None)  # noqa
    ).count()

    avg_health = db.query(func.avg(InfrastructureAsset.health_score)).scalar() or 0

    type_breakdown = db.query(
        InfrastructureAsset.asset_type,
        func.count(InfrastructureAsset.id).label("count"),
        func.avg(InfrastructureAsset.health_score).label("avg_health")
    ).group_by(InfrastructureAsset.asset_type).all()

    dept_breakdown = db.query(
        InfrastructureAsset.department,
        func.count(InfrastructureAsset.id).label("count")
    ).group_by(InfrastructureAsset.department).all()

    recent_reports = db.query(CitizenReport).order_by(CitizenReport.timestamp.desc()).limit(5).all()

    return {
        "summary": {
            "total_assets": total,
            "healthy": healthy,
            "warning": warning,
            "critical": critical,
            "overdue_inspections": overdue,
            "network_health_index": round(100 - avg_health, 1),
            "avg_health_score": round(float(avg_health), 2),
        },
        "by_type": [
            {
                "asset_type": row.asset_type,
                "count": row.count,
                "avg_health_score": round(float(row.avg_health or 0), 2)
            }
            for row in type_breakdown
        ],
        "by_department": [
            {"department": row.department, "count": row.count}
            for row in dept_breakdown
        ],
        "recent_citizen_reports": [
            {
                "id": r.id,
                "asset_id": r.asset_id,
                "report_type": r.report_type,
                "severity": r.severity,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None
            }
            for r in recent_reports
        ]
    }


@router.get("/network-risk")
def get_network_risk(db: Session = Depends(get_db)):
    assets = db.query(InfrastructureAsset).all()
    connections = db.query(AssetConnection).all()

    assets_data = [
        {
            "id": a.id,
            "asset_name": a.asset_name,
            "asset_type": a.asset_type,
            "health_score": a.health_score,
            "risk_level": a.risk_level,
        }
        for a in assets
    ]
    connections_data = [
        {"asset_id": c.asset_id, "connected_asset_id": c.connected_asset_id}
        for c in connections
    ]

    network_risk = compute_network_risk(assets_data, connections_data)
    summary = get_cascade_summary(network_risk)

    return {
        "summary": summary,
        "asset_risks": list(network_risk.values())
    }


@router.get("/health-trend")
def get_health_trend(db: Session = Depends(get_db)):
    """Returns health score distribution over installation years."""
    assets = db.query(
        InfrastructureAsset.installation_year,
        func.avg(InfrastructureAsset.health_score).label("avg_score"),
        func.count(InfrastructureAsset.id).label("count")
    ).group_by(InfrastructureAsset.installation_year).order_by(InfrastructureAsset.installation_year).all()

    return [
        {
            "year": row.installation_year,
            "avg_health_score": round(float(row.avg_score or 0), 2),
            "asset_count": row.count
        }
        for row in assets
    ]
