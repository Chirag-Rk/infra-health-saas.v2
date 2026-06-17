import math
from typing import List, Dict, Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers between two coordinates."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def assets_to_geojson(assets: List[dict]) -> dict:
    """Convert asset list to GeoJSON FeatureCollection."""
    features = []
    for asset in assets:
        risk_colors = {
            "healthy": "#22c55e",
            "warning": "#eab308",
            "critical": "#ef4444"
        }
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [asset.get("longitude", 0), asset.get("latitude", 0)]
            },
            "properties": {
                "id": asset.get("id"),
                "asset_name": asset.get("asset_name"),
                "asset_type": asset.get("asset_type"),
                "department": asset.get("department"),
                "status": asset.get("status"),
                "health_score": asset.get("health_score"),
                "risk_level": asset.get("risk_level"),
                "installation_year": asset.get("installation_year"),
                "marker_color": risk_colors.get(asset.get("risk_level", "healthy"), "#6b7280")
            }
        })
    return {"type": "FeatureCollection", "features": features}


def get_map_bounds(assets: List[dict]) -> Dict:
    """Get bounding box for all assets."""
    if not assets:
        return {"min_lat": -90, "max_lat": 90, "min_lon": -180, "max_lon": 180}
    lats = [a["latitude"] for a in assets if a.get("latitude")]
    lons = [a["longitude"] for a in assets if a.get("longitude")]
    return {
        "min_lat": min(lats), "max_lat": max(lats),
        "min_lon": min(lons), "max_lon": max(lons),
        "center_lat": sum(lats) / len(lats),
        "center_lon": sum(lons) / len(lons),
    }


def find_nearby_assets(
    target_lat: float,
    target_lon: float,
    assets: List[dict],
    radius_km: float = 1.0
) -> List[dict]:
    """Find assets within a given radius (km) of a coordinate."""
    nearby = []
    for asset in assets:
        dist = haversine_distance(target_lat, target_lon, asset["latitude"], asset["longitude"])
        if dist <= radius_km:
            nearby.append({**asset, "distance_km": round(dist, 3)})
    return sorted(nearby, key=lambda x: x["distance_km"])
