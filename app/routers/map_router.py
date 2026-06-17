from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.asset_model import InfrastructureAsset
from app.models.connection_model import AssetConnection
from app.utils.geo_utils import assets_to_geojson, get_map_bounds, find_nearby_assets

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/assets")
def get_map_assets(
    risk_level: Optional[str] = None,
    asset_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Return all assets as GeoJSON FeatureCollection for map rendering."""
    query = db.query(InfrastructureAsset)
    if risk_level:
        query = query.filter(InfrastructureAsset.risk_level == risk_level)
    if asset_type:
        query = query.filter(InfrastructureAsset.asset_type == asset_type)

    assets = query.all()
    asset_dicts = [
        {
            "id": a.id,
            "asset_name": a.asset_name,
            "asset_type": a.asset_type,
            "department": a.department,
            "latitude": a.latitude,
            "longitude": a.longitude,
            "status": a.status,
            "health_score": a.health_score,
            "risk_level": a.risk_level,
            "installation_year": a.installation_year,
        }
        for a in assets
    ]

    geojson = assets_to_geojson(asset_dicts)
    bounds = get_map_bounds(asset_dicts)
    return {
        "geojson": geojson,
        "bounds": bounds,
        "total": len(asset_dicts)
    }


@router.get("/nearby")
def get_nearby_assets(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=1.0, ge=0.1, le=50),
    db: Session = Depends(get_db)
):
    """Find assets near a given coordinate."""
    assets = db.query(InfrastructureAsset).all()
    asset_dicts = [
        {
            "id": a.id,
            "asset_name": a.asset_name,
            "asset_type": a.asset_type,
            "latitude": a.latitude,
            "longitude": a.longitude,
            "health_score": a.health_score,
            "risk_level": a.risk_level,
        }
        for a in assets
    ]
    nearby = find_nearby_assets(lat, lon, asset_dicts, radius_km)
    return {"nearby_assets": nearby, "count": len(nearby), "radius_km": radius_km}


@router.get("/connections")
def get_asset_connections(db: Session = Depends(get_db)):
    """Return all asset connections for network graph visualization."""
    connections = db.query(AssetConnection).all()
    assets = {a.id: a for a in db.query(InfrastructureAsset).all()}

    edges = []
    for conn in connections:
        src = assets.get(conn.asset_id)
        dst = assets.get(conn.connected_asset_id)
        if src and dst:
            edges.append({
                "from_id": conn.asset_id,
                "to_id": conn.connected_asset_id,
                "connection_type": conn.connection_type,
                "from_lat": src.latitude,
                "from_lon": src.longitude,
                "to_lat": dst.latitude,
                "to_lon": dst.longitude,
                "from_name": src.asset_name,
                "to_name": dst.asset_name,
            })
    return {"connections": edges, "count": len(edges)}
