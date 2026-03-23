from fastapi import APIRouter
from .endpoints import auth, closet, outfits, ai, weather, social

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(closet.router)
api_router.include_router(outfits.router)
api_router.include_router(ai.router)
api_router.include_router(weather.router)
api_router.include_router(social.router)
