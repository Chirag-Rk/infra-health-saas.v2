from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class MaintenanceLogBase(BaseModel):
    asset_id: int
    inspection_date: date
    inspector: str
    condition_notes: Optional[str] = None
    damage_level: float = Field(default=0.0, ge=0.0, le=10.0)
    maintenance_action: Optional[str] = None


class MaintenanceLogCreate(MaintenanceLogBase):
    pass


class MaintenanceLogResponse(MaintenanceLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CitizenReportBase(BaseModel):
    asset_id: int
    report_type: str
    description: str
    location: Optional[str] = None
    severity: str = "low"


class CitizenReportCreate(CitizenReportBase):
    pass


class CitizenReportResponse(CitizenReportBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class PriorityAsset(BaseModel):
    rank: int
    asset_id: int
    asset_name: str
    asset_type: str
    risk_level: str
    health_score: float
    priority_score: float
    recommended_action: str
    department: str
