from pydantic import BaseModel
from typing import Optional


class DayForecast(BaseModel):
    date:          str
    discharge:     Optional[float]
    discharge_max: Optional[float]
    risk_level:    str


class CityFloodResponse(BaseModel):
    city_name:  str
    state_code: str
    latitude:   float
    longitude:  float
    forecast:   list[DayForecast]


class RankingCity(BaseModel):
    city_name:     str
    state_code:    str
    latitude:      float
    longitude:     float
    max_discharge: float
    peak_date:     Optional[str]
    risk_level:    str
