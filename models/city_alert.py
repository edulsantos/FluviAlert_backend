import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from db.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class CityAlert(Base):
    __tablename__ = "city_alerts"

    id          = Column(CHAR(36), primary_key=True, default=gen_uuid)
    user_id     = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    city_name   = Column(String(120), nullable=False)
    state_code  = Column(String(2),  nullable=False)
    latitude    = Column(Float, nullable=False)
    longitude   = Column(Float, nullable=False)
    alert_email = Column(String(255), nullable=False)
    is_active   = Column(Boolean, default=True, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="city_alerts")
