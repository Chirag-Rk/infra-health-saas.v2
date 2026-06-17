from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class InfrastructureAsset(Base):
    __tablename__ = "infrastructure_assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_name = Column(String(200), nullable=False, index=True)
    asset_type = Column(String(100), nullable=False)  # road, bridge, pipeline, drainage, street_light, public_facility
    department = Column(String(150), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    installation_year = Column(Integer, nullable=False)
    status = Column(String(50), default="active")  # active, inactive, under_maintenance, decommissioned
    last_inspection_date = Column(Date, nullable=True)
    health_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="healthy")  # healthy, warning, critical
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    maintenance_logs = relationship("MaintenanceLog", back_populates="asset", cascade="all, delete-orphan")
    connections_from = relationship(
        "AssetConnection",
        foreign_keys="AssetConnection.asset_id",
        back_populates="asset",
        cascade="all, delete-orphan"
    )
    citizen_reports = relationship("CitizenReport", back_populates="asset", cascade="all, delete-orphan")
