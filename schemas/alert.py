from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class AlertCreate(BaseModel):
    city_name:  str
    alert_email: EmailStr


class AlertUpdate(BaseModel):
    alert_email: Optional[EmailStr] = None
    is_active:   Optional[bool] = None


class AlertResponse(BaseModel):
    id:          str
    city_name:   str
    state_code:  str
    latitude:    float
    longitude:   float
    alert_email: str
    is_active:   bool
    created_at:  datetime

    class Config:
        from_attributes = True
