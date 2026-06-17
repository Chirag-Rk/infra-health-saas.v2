from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class AssetConnection(Base):
    __tablename__ = "asset_connections"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("infrastructure_assets.id"), nullable=False)
    connected_asset_id = Column(Integer, ForeignKey("infrastructure_assets.id"), nullable=False)
    connection_type = Column(String(100), nullable=False)  # feeds_into, adjacent, dependent, structural
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("InfrastructureAsset", foreign_keys=[asset_id], back_populates="connections_from")
    connected_asset = relationship("InfrastructureAsset", foreign_keys=[connected_asset_id])
