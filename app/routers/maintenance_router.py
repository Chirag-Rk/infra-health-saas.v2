from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models.asset_model import InfrastructureAsset
from app.models.maintenance_model import MaintenanceLog, CitizenReport
from app.models.connection_model import AssetConnection
from app.schemas.maintenance_schema import (
    MaintenanceLogCreate, MaintenanceLogResponse,
    CitizenReportCreate, CitizenReportResponse,
    PriorityAsset
)
from app.services.priority_engine import rank_assets_by_priority
from app.services.risk_propagation import compute_network_risk
from app.routers.asset_router import _recalculate_health

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.get("/priority", response_model=List[PriorityAsset])
def get_maintenance_priority(db: Session = Depends(get_db)):
    assets = db.query(InfrastructureAsset).all()
    connections = db.query(AssetConnection).all()

    assets_data = [
        {"id": a.id, "asset_name": a.asset_name, "asset_type": a.asset_type,
         "health_score": a.health_score, "risk_level": a.risk_level}
        for a in assets
    ]
    connections_data = [
        {"asset_id": c.asset_id, "connected_asset_id": c.connected_asset_id}
        for c in connections
    ]
    network_risk = compute_network_risk(assets_data, connections_data)

    assets_for_ranking = []
    for asset in assets:
        report_count = db.query(CitizenReport).filter(CitizenReport.asset_id == asset.id).count()
        conn_count = db.query(AssetConnection).filter(AssetConnection.asset_id == asset.id).count()
        prop_delta = network_risk.get(asset.id, {}).get("propagated_delta", 0.0)

        assets_for_ranking.append({
            "asset_id": asset.id,
            "asset_name": asset.asset_name,
            "asset_type": asset.asset_type,
            "department": asset.department,
            "health_score": asset.health_score,
            "risk_level": asset.risk_level,
            "installation_year": asset.installation_year,
            "citizen_report_count": report_count,
            "connections_count": conn_count,
            "propagated_delta": prop_delta,
        })

    ranked = rank_assets_by_priority(assets_for_ranking)

    return [
        PriorityAsset(
            rank=item["rank"],
            asset_id=item["asset_id"],
            asset_name=item["asset_name"],
            asset_type=item["asset_type"],
            risk_level=item["risk_level"],
            health_score=item["health_score"],
            priority_score=item["priority_score"],
            recommended_action=item["recommended_action"],
            department=item["department"],
        )
        for item in ranked
    ]


@router.post("/logs/", response_model=MaintenanceLogResponse, status_code=201)
def create_log(log_in: MaintenanceLogCreate, db: Session = Depends(get_db)):
    asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.id == log_in.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Update last_inspection_date
    if asset.last_inspection_date is None or log_in.inspection_date > asset.last_inspection_date:
        asset.last_inspection_date = log_in.inspection_date

    log = MaintenanceLog(**log_in.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)

    _recalculate_health(asset, db)
    return log


@router.get("/logs/{asset_id}", response_model=List[MaintenanceLogResponse])
def get_logs_for_asset(asset_id: int, db: Session = Depends(get_db)):
    return db.query(MaintenanceLog).filter(MaintenanceLog.asset_id == asset_id).order_by(
        MaintenanceLog.inspection_date.desc()
    ).all()


@router.post("/reports/", response_model=CitizenReportResponse, status_code=201)
def create_citizen_report(report_in: CitizenReportCreate, db: Session = Depends(get_db)):
    asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.id == report_in.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    report = CitizenReport(**report_in.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    _recalculate_health(asset, db)
    return report


@router.get("/reports/{asset_id}", response_model=List[CitizenReportResponse])
def get_reports_for_asset(asset_id: int, db: Session = Depends(get_db)):
    return db.query(CitizenReport).filter(CitizenReport.asset_id == asset_id).order_by(
        CitizenReport.timestamp.desc()
    ).all()
