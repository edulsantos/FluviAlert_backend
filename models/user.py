from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from db.database import Base
from core.utils import gen_uuid


class User(Base):
    __tablename__ = "users"

    id            = Column(CHAR(36), primary_key=True, default=gen_uuid)
    name          = Column(String(120), nullable=False)
    email         = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active     = Column(Boolean, default=True, nullable=False)
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    city_alerts = relationship("CityAlert", back_populates="user", cascade="all, delete-orphan")
