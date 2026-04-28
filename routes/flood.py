from fastapi import APIRouter, HTTPException

from schemas.flood import CityFloodResponse, RankingCity
from services.flood_service import search_city_flood_risk, get_top20_flood_risk, get_flood_stats

router = APIRouter()


@router.get("/search", response_model=CityFloodResponse)
async def search_city(city: str):
    """
    Busca o risco de enchente para uma cidade brasileira nos próximos 7 dias.
    Exemplo: /api/flood/search?city=Porto Alegre
    """
    result = await search_city_flood_risk(city)
    if not result:
        raise HTTPException(status_code=404, detail="Cidade não encontrada.")
    return result


@router.get("/ranking", response_model=list[RankingCity])
async def top20_ranking():
    """
    Retorna as 20 cidades brasileiras com maior risco de enchente no momento.
    """
    return await get_top20_flood_risk()


@router.get("/stats")
async def flood_stats():
    """
    Retorna estatísticas gerais de monitoramento.
    """
    return await get_flood_stats()
