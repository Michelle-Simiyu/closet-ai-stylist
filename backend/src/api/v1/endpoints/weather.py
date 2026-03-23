import logging
from fastapi import APIRouter, Depends
from ....core.security import get_current_user
from ....models.user import User
from ....services.ai_service import get_mock_weather

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("")
async def get_weather(
    city: str = "New York",
    current_user: User = Depends(get_current_user),
):
    """Get mock weather data for outfit recommendations."""
    return get_mock_weather(city)
