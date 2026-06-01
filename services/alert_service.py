from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.city_alert import CityAlert
from schemas.alert import AlertCreate, AlertUpdate
from services.flood_service import get_city_coordinates


from models.aut_city import AutCity

async def create_alert(db: Session, user_id: str, data: AlertCreate) -> CityAlert:
    city = await get_city_coordinates(data.city_name)
    if not city:
        raise HTTPException(status_code=404, detail="Cidade não encontrada.")

    # Find or create AutCity
    aut_city = db.query(AutCity).filter(AutCity.city_name == city["city_name"]).first()
    if not aut_city:
        aut_city = AutCity(
            city_name=city["city_name"],
            state_code=city["state_code"],
            latitude=city["latitude"],
            longitude=city["longitude"],
            current_status="Monitoramento Iniciado",
            risk_level="baixo"
        )
        db.add(aut_city)
        db.commit()
        db.refresh(aut_city)

    alert = CityAlert(
        user_id=user_id,
        aut_city_id=aut_city.id,
        city_name=city["city_name"],
        state_code=city["state_code"],
        latitude=city["latitude"],
        longitude=city["longitude"],
        alert_email=data.alert_email,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alerts_by_user(db: Session, user_id: str) -> list[CityAlert]:
    return db.query(CityAlert).filter(CityAlert.user_id == user_id).all()


def get_alert_by_id(db: Session, alert_id: str, user_id: str) -> CityAlert:
    alert = db.query(CityAlert).filter(
        CityAlert.id == alert_id,
        CityAlert.user_id == user_id,
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado.")
    return alert


def update_alert(db: Session, alert_id: str, user_id: str, data: AlertUpdate) -> CityAlert:
    alert = get_alert_by_id(db, alert_id, user_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(alert, field, value)
    db.commit()
    db.refresh(alert)
    return alert


def delete_alert(db: Session, alert_id: str, user_id: str) -> None:
    alert = get_alert_by_id(db, alert_id, user_id)
    db.delete(alert)
    db.commit()
