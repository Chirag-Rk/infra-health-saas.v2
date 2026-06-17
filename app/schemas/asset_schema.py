from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class AssetBase(BaseModel):
    asset_name: str = Field(..., min_length=2, max_length=200)
    asset_type: str = Field(..., description="road, bridge, pipeline, drainage, street_light, public_facility")
    department: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    installation_year: int = Field(..., ge=1900, le=2100)
    status: str = Field(default="active")
    last_inspection_date: Optional[date] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    asset_type: Optional[str] = None
    department: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    installation_year: Optional[int] = None
    status: Optional[str] = None
    last_inspection_date: Optional[date] = None
    health_score: Optional[float] = None
    risk_level: Optional[str] = None


class AssetResponse(AssetBase):
    id: int
    health_score: float
    risk_level: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetWithDetails(AssetResponse):
    maintenance_count: int = 0
    citizen_report_count: int = 0
    connected_asset_ids: List[int] = []


class ConnectionCreate(BaseModel):
    asset_id: int
    connected_asset_id: int
    connection_type: str


class ConnectionResponse(ConnectionCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
