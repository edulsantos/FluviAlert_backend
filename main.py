import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from db.database import engine, Base
from routes import users, flood, alerts

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("fluvialert")

Base.metadata.create_all(bind=engine)

from contextlib import asynccontextmanager
from services.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(
    title="FluviAlert API",
    description="API de monitoramento de enchentes no Brasil",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router,  prefix="/api/users",  tags=["Usuários"])
app.include_router(flood.router,  prefix="/api/flood",  tags=["Enchentes"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alertas"])


@app.get("/")
def root():
    return {"message": "FluviAlert API rodando"}

@app.post("/api/sync-db", tags=["Manutenção"])
def sync_db():
    Base.metadata.create_all(bind=engine)
    return {"message": "Tabelas sincronizadas no banco de dados."}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
