from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth_router
from app.routers.ingredients import router as ingredients_router
from app.routers.graph import router as graph_router
from app.routers.favorites import router as favorites_router
from app.routers.pairings import router as pairings_router


settings = get_settings()

app = FastAPI(
    title="Mapa de Sabores API",
    description="Sistema Web Interactivo de Descubrimiento Gastronómico mediante Grafos de Sabores asistido por IA",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers bajo el prefijo /api/v1
app.include_router(auth_router, prefix="/api/v1")
app.include_router(ingredients_router, prefix="/api/v1")
app.include_router(graph_router, prefix="/api/v1")
app.include_router(favorites_router, prefix="/api/v1")
app.include_router(pairings_router, prefix="/api/v1")



@app.get("/api/v1/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
