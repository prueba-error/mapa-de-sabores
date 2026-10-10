from app.routers.auth import router as auth_router
from app.routers.ingredients import router as ingredients_router
from app.routers.graph import router as graph_router

__all__ = ["auth_router", "ingredients_router", "graph_router"]
