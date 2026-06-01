import logging
import smtplib
from email.message import EmailMessage

from core.config import settings

logger = logging.getLogger("fluvialert.email")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL


def send_alert_email(to_email: str, city_name: str, risk_level: str, status_desc: str):
    """
    Sends an alert email via Google SMTP.
    Requires an App Password for Gmail to work.
    """
    msg = EmailMessage()
    msg.set_content(
        f"Atenção!\n\n"
        f"A cidade de {city_name} que você monitora no FluviAlert encontra-se com risco: {risk_level.upper()}.\n"
        f"Status atual: {status_desc}\n\n"
        f"Acesse o painel do FluviAlert para mais informações e mantenha-se em segurança.\n\n"
        f"Equipe FluviAlert Intelligence."
    )

    msg['Subject'] = f"ALERTA FLUVIALERT - Risco em {city_name}"
    msg['From'] = settings.SMTP_USER
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
        logger.info(f"Email successfully sent to {to_email} for city {city_name}.")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
