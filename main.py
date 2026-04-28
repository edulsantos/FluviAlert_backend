from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import engine, Base
from routes import users, flood, alerts

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FluviAlert API",
    description="API de monitoramento de enchentes no Brasil",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://200.132.38.218:5173",
        "http://200.132.38.218",
    ],
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
