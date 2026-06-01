from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from core.security import get_current_user
from models.user import User
from services import alert_service

router = APIRouter()


@router.post("/check-risks", tags=["Manutenção"])
async def trigger_check_risks():
    """Dispara manualmente a verificação de riscos de todas as cidades cadastradas.
    Útil para testes e validação do envio de e-mails."""
    from services.scheduler import async_check_city_risks
    await async_check_city_risks()
    return {"message": "Verificação de riscos concluída. Consulte os logs para detalhes."}


@router.post("/{user_id}", response_model=AlertResponse, status_code=201)
async def create_alert(user_id: str, data: AlertCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Não autorizado a criar alerta para outro usuário.")
    return await alert_service.create_alert(db, user_id, data)


@router.get("/{user_id}", response_model=list[AlertResponse])
def list_alerts(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Não autorizado a listar alertas de outro usuário.")
    return alert_service.get_alerts_by_user(db, user_id)


@router.put("/{user_id}/{alert_id}", response_model=AlertResponse)
def update_alert(user_id: str, alert_id: str, data: AlertUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Não autorizado a alterar alerta de outro usuário.")
    return alert_service.update_alert(db, alert_id, user_id, data)


@router.delete("/{user_id}/{alert_id}", status_code=204)
def delete_alert(user_id: str, alert_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Não autorizado a deletar alerta de outro usuário.")
    alert_service.delete_alert(db, alert_id, user_id)
