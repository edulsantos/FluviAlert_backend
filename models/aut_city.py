from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.mysql import CHAR

from db.database import Base
from core.utils import gen_uuid

class AutCity(Base):
    __tablename__ = "aut_cities"

    id             = Column(CHAR(36), primary_key=True, default=gen_uuid)
    city_name      = Column(String(120), unique=True, nullable=False, index=True)
    state_code     = Column(String(2), nullable=False)
    latitude       = Column(Float, nullable=False)
    longitude      = Column(Float, nullable=False)
    last_updated   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    current_status = Column(String(50), nullable=True)
    risk_level     = Column(String(50), nullable=True)
