import asyncio
import logging
import time
import httpx
from typing import Optional

logger = logging.getLogger("fluvialert.flood")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FLOOD_URL     = "https://flood-api.open-meteo.com/v1/flood"

# ---------- HTTP Client reutilizável ----------
_http_client: Optional[httpx.AsyncClient] = None


async def _get_client() -> httpx.AsyncClient:
    """Retorna um AsyncClient reutilizável (connection pooling)."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=15.0)
    return _http_client


# ---------- Cache simples em memória ----------
_cache: dict[str, tuple[float, any]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutos


def _cache_get(key: str):
    """Retorna valor do cache se ainda válido, senão None."""
    entry = _cache.get(key)
    if entry is None:
        return None
    timestamp, value = entry
    if time.time() - timestamp > CACHE_TTL_SECONDS:
        del _cache[key]
        return None
    return value


def _cache_set(key: str, value):
    """Armazena valor no cache."""
    _cache[key] = (time.time(), value)


# ---------- Mapa de estados ----------
STATE_NAME_TO_CODE = {
    "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM",
    "Bahia": "BA", "Ceará": "CE", "Distrito Federal": "DF",
    "Espírito Santo": "ES", "Goiás": "GO", "Maranhão": "MA",
    "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG",
    "Pará": "PA", "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE",
    "Piauí": "PI", "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS", "Rondônia": "RO", "Roraima": "RR",
    "Santa Catarina": "SC", "São Paulo": "SP", "Sergipe": "SE",
    "Tocantins": "TO",
}

MONITORED_CITIES = [
    {"city_name": "São Paulo",      "state_code": "SP", "latitude": -23.5505, "longitude": -46.6333},
    {"city_name": "Rio de Janeiro", "state_code": "RJ", "latitude": -22.9068, "longitude": -43.1729},
    {"city_name": "Belo Horizonte", "state_code": "MG", "latitude": -19.9191, "longitude": -43.9386},
    {"city_name": "Salvador",       "state_code": "BA", "latitude": -12.9714, "longitude": -38.5014},
    {"city_name": "Fortaleza",      "state_code": "CE", "latitude": -3.7172,  "longitude": -38.5433},
    {"city_name": "Curitiba",       "state_code": "PR", "latitude": -25.4284, "longitude": -49.2733},
    {"city_name": "Manaus",         "state_code": "AM", "latitude": -3.1190,  "longitude": -60.0217},
    {"city_name": "Recife",         "state_code": "PE", "latitude": -8.0578,  "longitude": -34.8829},
    {"city_name": "Porto Alegre",   "state_code": "RS", "latitude": -30.0346, "longitude": -51.2177},
    {"city_name": "Belém",          "state_code": "PA", "latitude": -1.4558,  "longitude": -48.4902},
    {"city_name": "Goiânia",        "state_code": "GO", "latitude": -16.6864, "longitude": -49.2643},
    {"city_name": "Florianópolis",  "state_code": "SC", "latitude": -27.5954, "longitude": -48.5480},
    {"city_name": "Maceió",         "state_code": "AL", "latitude": -9.6658,  "longitude": -35.7350},
    {"city_name": "Natal",          "state_code": "RN", "latitude": -5.7945,  "longitude": -35.2110},
    {"city_name": "Campo Grande",   "state_code": "MS", "latitude": -20.4697, "longitude": -54.6201},
    {"city_name": "Teresina",       "state_code": "PI", "latitude": -5.0892,  "longitude": -42.8019},
    {"city_name": "João Pessoa",    "state_code": "PB", "latitude": -7.1195,  "longitude": -34.8450},
    {"city_name": "Aracaju",        "state_code": "SE", "latitude": -10.9472, "longitude": -37.0731},
    {"city_name": "Porto Velho",    "state_code": "RO", "latitude": -8.7612,  "longitude": -63.9039},
    {"city_name": "Cuiabá",         "state_code": "MT", "latitude": -15.6014, "longitude": -56.0979},
    {"city_name": "Macapá",         "state_code": "AP", "latitude": 0.0349,   "longitude": -51.0694},
    {"city_name": "Rio Branco",     "state_code": "AC", "latitude": -9.9754,  "longitude": -67.8249},
    {"city_name": "Boa Vista",      "state_code": "RR", "latitude": 2.8235,   "longitude": -60.6758},
    {"city_name": "Palmas",         "state_code": "TO", "latitude": -10.2491, "longitude": -48.3243},
    {"city_name": "São Luís",       "state_code": "MA", "latitude": -2.5297,  "longitude": -44.3028},
    {"city_name": "Vitória",        "state_code": "ES", "latitude": -20.3155, "longitude": -40.3128},
    {"city_name": "Campinas",       "state_code": "SP", "latitude": -22.9099, "longitude": -47.0626},
    {"city_name": "Santos",         "state_code": "SP", "latitude": -23.9608, "longitude": -46.3336},
    {"city_name": "Joinville",      "state_code": "SC", "latitude": -26.3044, "longitude": -48.8487},
    {"city_name": "Pelotas",        "state_code": "RS", "latitude": -31.7654, "longitude": -52.3376},
]


async def get_city_coordinates(city_name: str) -> Optional[dict]:
    """Busca coordenadas de uma cidade brasileira via Open-Meteo Geocoding."""
    client = await _get_client()
    try:
        response = await client.get(GEOCODING_URL, params={
            "name":       city_name,
            "count":      5,
            "language":   "pt",
            "country_id": "BR",
        })
        response.raise_for_status()
        data = response.json()
    except httpx.TimeoutException:
        logger.warning("Timeout ao buscar coordenadas de '%s'", city_name)
        return None
    except httpx.HTTPStatusError as e:
        logger.warning("Erro HTTP %d ao buscar coordenadas de '%s'", e.response.status_code, city_name)
        return None
    except httpx.RequestError as e:
        logger.error("Erro de conexão ao buscar coordenadas: %s", e)
        return None

    results = data.get("results")
    if not results:
        return None

    city = results[0]

    admin1_full = city.get("admin1", "")
    state_code  = STATE_NAME_TO_CODE.get(admin1_full, admin1_full[:2].upper())

    return {
        "city_name":  city.get("name"),
        "state_code": state_code,
        "latitude":   city.get("latitude"),
        "longitude":  city.get("longitude"),
    }


async def get_flood_forecast(
    latitude: float,
    longitude: float,
    days: int = 7,
    state_code: str = ""
) -> dict:
    """Busca previsão de enchente da Open-Meteo Flood API."""
    # Verifica cache
    cache_key = f"forecast:{latitude:.4f},{longitude:.4f},{days}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    client = await _get_client()
    try:
        response = await client.get(FLOOD_URL, params={
            "latitude":      latitude,
            "longitude":     longitude,
            "daily":         "river_discharge,river_discharge_max",
            "forecast_days": days,
        })
        response.raise_for_status()
        data = response.json()
    except httpx.TimeoutException:
        logger.warning("Timeout ao buscar previsão para (%.4f, %.4f)", latitude, longitude)
        return {"latitude": latitude, "longitude": longitude, "forecast": []}
    except httpx.HTTPStatusError as e:
        logger.warning("Erro HTTP %d ao buscar previsão para (%.4f, %.4f)", e.response.status_code, latitude, longitude)
        return {"latitude": latitude, "longitude": longitude, "forecast": []}
    except httpx.RequestError as e:
        logger.error("Erro de conexão ao buscar previsão: %s", e)
        return {"latitude": latitude, "longitude": longitude, "forecast": []}

    daily         = data.get("daily", {})
    dates         = daily.get("time", [])
    discharge     = daily.get("river_discharge", [])
    discharge_max = daily.get("river_discharge_max", [])

    forecast = []
    for i, date in enumerate(dates):
        dmax = discharge_max[i] if i < len(discharge_max) else None
        forecast.append({
            "date":          date,
            "discharge":     discharge[i] if i < len(discharge) else None,
            "discharge_max": dmax,
            "risk_level":    _classify_risk(dmax, state_code),
        })

    result = {
        "latitude":  latitude,
        "longitude": longitude,
        "forecast":  forecast,
    }
    _cache_set(cache_key, result)
    return result


async def search_city_flood_risk(city_name: str) -> Optional[dict]:
    """Busca risco de enchente para uma cidade pelo nome."""
    city = await get_city_coordinates(city_name)
    if not city:
        return None

    forecast = await get_flood_forecast(city["latitude"], city["longitude"], state_code=city["state_code"])
    return {
        "city_name":  city["city_name"],
        "state_code": city["state_code"],
        "latitude":   city["latitude"],
        "longitude":  city["longitude"],
        "forecast":   forecast["forecast"],
    }


async def get_top20_flood_risk() -> list[dict]:
    """Retorna as 20 cidades com maior risco de enchente."""
    # Verifica cache do ranking completo
    cached = _cache_get("ranking_top20")
    if cached is not None:
        return cached

    semaphore = asyncio.Semaphore(5)

    async def fetch_city(city: dict) -> dict:
        async with semaphore:
            try:
                await asyncio.sleep(0.2)
                forecast = await get_flood_forecast(city["latitude"], city["longitude"], days=7, state_code=city["state_code"])
                max_discharge = max(
                    (d["discharge_max"] for d in forecast["forecast"] if d["discharge_max"] is not None),
                    default=0,
                )
                peak_day = next(
                    (d for d in forecast["forecast"] if d["discharge_max"] == max_discharge),
                    None,
                )
                return {
                    **city,
                    "max_discharge": max_discharge,
                    "peak_date":     peak_day["date"] if peak_day else None,
                    "risk_level":    _classify_risk(max_discharge, city["state_code"]),
                }
            except Exception as e:
                logger.error("Erro ao buscar %s: %s", city["city_name"], e)
                return {**city, "max_discharge": 0, "peak_date": None, "risk_level": "desconhecido"}

    results = await asyncio.gather(*[fetch_city(c) for c in MONITORED_CITIES])
    ranked  = sorted(results, key=lambda x: x["max_discharge"], reverse=True)
    top20   = ranked[:20]

    _cache_set("ranking_top20", top20)
    return top20


async def get_flood_stats() -> dict:
    """Retorna estatísticas reais baseadas nos dados do ranking."""
    ranking = await get_top20_flood_risk()

    total_cities = len(ranking)
    safe_cities = len([c for c in ranking if c["risk_level"] == "baixo"])
    moderate_cities = len([c for c in ranking if c["risk_level"] == "moderado"])
    critical_cities = len([c for c in ranking if c["risk_level"] == "alto"])
    safety_percentage = (safe_cities / total_cities * 100) if total_cities else 100

    return {
        "safety_percentage": round(safety_percentage, 1),
        "monitored_cities": len(MONITORED_CITIES),
        "cities_analyzed": total_cities,
        "safe_count": safe_cities,
        "moderate_count": moderate_cities,
        "critical_alerts_count": critical_cities,
    }


# ---------- Thresholds por bacia hidrográfica ----------
BASIN_THRESHOLDS: dict[str, tuple[float, float]] = {
    # AMAZÔNICA
    "AM": (150_000, 200_000),
    "PA": (150_000, 200_000),
    "AP": (150_000, 200_000),
    "RR": (150_000, 200_000),
    "AC": (150_000, 200_000),
    "RO": (150_000, 200_000),
    # TOCANTINS-ARAGUAIA
    "TO": (12_000, 18_000),
    # PARANÁ
    "SP": (8_000, 12_000),
    "PR": (8_000, 12_000),
    "MS": (2_000, 3_000),
    "GO": (8_000, 12_000),
    "DF": (8_000, 12_000),
    # SÃO FRANCISCO
    "MG": (2_000, 3_500),
    "BA": (2_000, 3_500),
    "PE": (2_000, 3_500),
    "AL": (2_000, 3_500),
    "SE": (2_000, 3_500),
    # PARAGUAI
    "MT": (2_000, 3_000),
    # SUL
    "RS": (500, 800),
    "SC": (500, 800),
    # ATLÂNTICO SUDESTE
    "RJ": (400, 700),
    "ES": (400, 700),
    # NORDESTE
    "CE": (150, 300),
    "RN": (150, 300),
    "PB": (150, 300),
    "PI": (150, 300),
    "MA": (150, 300),
}

_DEFAULT_THRESHOLDS: tuple[float, float] = (500, 1_000)


def _classify_risk(discharge_max: Optional[float], state_code: str = "") -> str:
    """Classifica o risco de enchente com base na vazão máxima do rio
    e nos thresholds calibrados para a bacia hidrográfica do estado."""
    if discharge_max is None:
        return "desconhecido"

    moderado, alto = BASIN_THRESHOLDS.get(state_code.upper(), _DEFAULT_THRESHOLDS)

    if discharge_max > alto:
        return "alto"
    if discharge_max > moderado:
        return "moderado"
    return "baixo"
