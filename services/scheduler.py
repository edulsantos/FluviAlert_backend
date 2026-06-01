import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from db.database import SessionLocal
from models.aut_city import AutCity
from models.city_alert import CityAlert
from services.flood_service import get_flood_forecast
from services.email_service import send_alert_email

logger = logging.getLogger("fluvialert.scheduler")


async def async_check_city_risks():
    """Consulta o risco de enchente de todas as cidades cadastradas na tabela aut_cities,
    atualiza o status e nível de risco, e envia e-mails de alerta se necessário."""
    logger.info("Starting scheduled job: check_city_risks")
    db: Session = SessionLocal()
    try:
        cities = db.query(AutCity).all()
        if not cities:
            logger.info("No cities registered in aut_cities. Skipping.")
            return

        for city in cities:
            try:
                # Buscar previsão de enchente via Open-Meteo Flood API
                forecast_data = await get_flood_forecast(
                    city.latitude, city.longitude, days=7, state_code=city.state_code
                )

                forecast_list = forecast_data.get("forecast", [])
                if not forecast_list:
                    city.current_status = "Sem dados disponíveis"
                    city.risk_level = "desconhecido"
                    city.last_updated = datetime.now(timezone.utc)
                    db.commit()
                    continue

                # Encontrar a vazão máxima projetada no período
                max_discharge = max(
                    (d["discharge_max"] for d in forecast_list if d["discharge_max"] is not None),
                    default=0,
                )

                # O risk_level já vem classificado pelo flood_service com os thresholds por bacia
                worst_risk = "baixo"
                for d in forecast_list:
                    if d["risk_level"] == "alto":
                        worst_risk = "alto"
                        break
                    elif d["risk_level"] == "moderado":
                        worst_risk = "moderado"

                new_status = f"Vazão máx. projetada: {max_discharge:.2f} m³/s"
                new_risk = worst_risk

                # Atualizar AutCity
                city.current_status = new_status
                city.risk_level = new_risk
                city.last_updated = datetime.now(timezone.utc)

                # Se risco moderado ou alto, enviar e-mails para todos os alertas ativos da cidade
                if new_risk in ["alto", "moderado"]:
                    alerts = db.query(CityAlert).filter(
                        CityAlert.aut_city_id == city.id,
                        CityAlert.is_active == True
                    ).all()
                    for alert in alerts:
                        send_alert_email(
                            to_email=alert.alert_email,
                            city_name=city.city_name,
                            risk_level=new_risk,
                            status_desc=new_status,
                        )
                    logger.info(
                        f"City {city.city_name}: risk={new_risk}, "
                        f"emails sent to {len(alerts)} users."
                    )
                else:
                    logger.info(f"City {city.city_name}: risk={new_risk}. No alerts needed.")

                db.commit()
            except Exception as e:
                logger.error(f"Error processing city {city.city_name}: {e}")
                db.rollback()
    except Exception as e:
        logger.error(f"Error in async_check_city_risks: {e}")
    finally:
        db.close()
    logger.info("Finished scheduled job: check_city_risks")


def start_scheduler():
    scheduler = AsyncIOScheduler()
    
    # PRODUÇÃO: Roda todos os dias às 10:00 e às 22:00
    scheduler.add_job(async_check_city_risks, 'cron', hour='10,22', minute='0')
    
    scheduler.start()
    logger.info("Scheduler started for 10:00 and 22:00 daily.")
    return scheduler
