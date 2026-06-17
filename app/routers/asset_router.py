from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.models.asset_model import InfrastructureAsset
from app.models.maintenance_model import MaintenanceLog, CitizenReport
from app.models.connection_model import AssetConnection
from app.schemas.asset_schema import AssetCreate, AssetUpdate, AssetResponse, AssetWithDetails, ConnectionCreate, ConnectionResponse
from app.services.health_engine import calculate_health_score

router = APIRouter(prefix="/assets", tags=["Assets"])


def _recalculate_health(asset: InfrastructureAsset, db: Session):
    """Recalculate and update asset health score."""
    logs = db.query(MaintenanceLog).filter(MaintenanceLog.asset_id == asset.id).all()
    reports = db.query(CitizenReport).filter(CitizenReport.asset_id == asset.id).all()

    damage_levels = [l.damage_level for l in logs if l.damage_level is not None]
    maintenance_dates = [l.inspection_date for l in logs if l.inspection_date]

    result = calculate_health_score(
        installation_year=asset.installation_year,
        asset_type=asset.asset_type,
        last_inspection_date=asset.last_inspection_date,
        damage_levels=damage_levels,
        citizen_report_count=len(reports),
        maintenance_dates=maintenance_dates
    )
    asset.health_score = result["health_score"]
    asset.risk_level = result["risk_level"]
    db.commit()
    db.refresh(asset)


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(asset_in: AssetCreate, db: Session = Depends(get_db)):
    asset = InfrastructureAsset(**asset_in.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    _recalculate_health(asset, db)
    return asset


@router.get("/", response_model=List[AssetResponse])
def list_assets(
    skip: int = 0,
    limit: int = 100,
    asset_type: str = None,
    risk_level: str = None,
    department: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(InfrastructureAsset)
    if asset_type:
        query = query.filter(InfrastructureAsset.asset_type == asset_type)
    if risk_level:
        query = query.filter(InfrastructureAsset.risk_level == risk_level)
    if department:
        query = query.filter(InfrastructureAsset.department == department)
    return query.offset(skip).limit(limit).all()


@router.get("/{asset_id}", response_model=AssetWithDetails)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")

    maintenance_count = db.query(MaintenanceLog).filter(MaintenanceLog.asset_id == asset_id).count()
    report_count = db.query(CitizenReport).filter(CitizenReport.asset_id == asset_id).count()
    connections = db.query(AssetConnection).filter(AssetConnection.asset_id == asset_id).all()
    connected_ids = [c.connected_asset_id for c in connections]

    result = AssetWithDetails.model_validate(asset)
    result.maintenance_count = maintenance_count
    result.citizen_report_count = report_count
    result.connected_asset_ids = connected_ids
    return result


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, asset_in: AssetUpdate, db: Session = Depends(get_db)):
    asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")

    for field, value in asset_in.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    db.commit()
    db.refresh(asset)
    _recalculate_health(asset, db)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    db.delete(asset)
    db.commit()


@router.get("/{asset_id}/history")
def get_asset_history(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")

    logs = db.query(MaintenanceLog).filter(MaintenanceLog.asset_id == asset_id).all()
    reports = db.query(CitizenReport).filter(CitizenReport.asset_id == asset_id).all()

    from app.services.lifecycle_service import build_lifecycle_timeline, compute_lifecycle_stats, get_asset_age_profile

    asset_dict = {
        "id": asset.id,
        "asset_name": asset.asset_name,
        "asset_type": asset.asset_type,
        "installation_year": asset.installation_year,
        "status": asset.status
    }
    log_dicts = [
        {
            "inspection_date": l.inspection_date,
            "inspector": l.inspector,
            "condition_notes": l.condition_notes,
            "damage_level": l.damage_level,
            "maintenance_action": l.maintenance_action
        } for l in logs
    ]
    report_dicts = [
        {
            "report_type": r.report_type,
            "description": r.description,
            "severity": r.severity,
            "timestamp": r.timestamp
        } for r in reports
    ]

    timeline = build_lifecycle_timeline(asset_dict, log_dicts, report_dicts)
    stats = compute_lifecycle_stats(timeline)
    age_profile = get_asset_age_profile(asset.installation_year, asset.asset_type)

    return {
        "asset_id": asset_id,
        "asset_name": asset.asset_name,
        "timeline": timeline,
        "stats": stats,
        "age_profile": age_profile
    }


@router.post("/connections/", response_model=ConnectionResponse, status_code=201)
def create_connection(conn_in: ConnectionCreate, db: Session = Depends(get_db)):
    conn = AssetConnection(**conn_in.model_dump())
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return conn


@router.post("/{asset_id}/recalculate", response_model=AssetResponse)
def recalculate_health(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(InfrastructureAsset).filter(InfrastructureAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    _recalculate_health(asset, db)
    return asset
