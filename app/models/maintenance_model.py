from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("infrastructure_assets.id"), nullable=False)
    inspection_date = Column(Date, nullable=False)
    inspector = Column(String(150), nullable=False)
    condition_notes = Column(Text, nullable=True)
    damage_level = Column(Float, default=0.0)  # 0.0 to 10.0
    maintenance_action = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("InfrastructureAsset", back_populates="maintenance_logs")


class CitizenReport(Base):
    __tablename__ = "citizen_reports"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("infrastructure_assets.id"), nullable=False)
    report_type = Column(String(100), nullable=False)  # pothole, crack, flooding, outage, structural
    description = Column(Text, nullable=False)
    location = Column(String(300), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    severity = Column(String(20), default="low")  # low, medium, high

    asset = relationship("InfrastructureAsset", back_populates="citizen_reports")
