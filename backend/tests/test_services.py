"""Tests for service layer (CRUD, feedback learning)."""
import pytest
from sqlmodel import Session
from src.models.clothing import ClothingItem, ClothingItemCreate, Category, Style, Season, Pattern
from src.models.outfit import GenerateOutfitsRequest
from src.models.user import User
from src.services import closet_service, outfit_service
from src.core.exceptions import NotFoundError, AuthorizationError
from src.core.security import get_password_hash


def make_user(session: Session, email: str = "svc@test.com") -> User:
    user = User(
        email=email,
        username="svcuser",
        password_hash=get_password_hash("pass"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def make_item_create(**kwargs) -> ClothingItemCreate:
    defaults = {
        "name": "Test Shirt",
        "category": Category.top,
        "color": "white",
        "style": Style.casual,
        "pattern": Pattern.solid,
        "formality": 2,
        "season": Season.all,
    }
    defaults.update(kwargs)
    return ClothingItemCreate(**defaults)


class TestClosetCRUD:
    @pytest.mark.asyncio
    async def test_create_item(self, session):
        user = make_user(session)
        item_data = make_item_create()
        item = await closet_service.create_item(session, item_data, user.id)
        assert item.id is not None
        assert item.name == "Test Shirt"
        assert item.user_id == user.id

    @pytest.mark.asyncio
    async def test_get_closet(self, session):
        user = make_user(session)
        await closet_service.create_item(session, make_item_create(name="A"), user.id)
        await closet_service.create_item(session, make_item_create(name="B"), user.id)
        items = await closet_service.get_closet(session, user.id)
        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_get_item_not_found(self, session):
        user = make_user(session)
        with pytest.raises(NotFoundError):
            await closet_service.get_item(session, "nonexistent-id", user.id)

    @pytest.mark.asyncio
    async def test_get_item_wrong_user(self, session):
        user1 = make_user(session, "u1@test.com")
        user2 = make_user(session, "u2@test.com")
        item = await closet_service.create_item(session, make_item_create(), user1.id)
        with pytest.raises(AuthorizationError):
            await closet_service.get_item(session, item.id, user2.id)

    @pytest.mark.asyncio
    async def test_delete_item(self, session):
        user = make_user(session)
        item = await closet_service.create_item(session, make_item_create(), user.id)
        await closet_service.delete_item(session, item.id, user.id)
        items = await closet_service.get_closet(session, user.id)
        assert len(items) == 0

    @pytest.mark.asyncio
    async def test_load_demo_closet(self, session):
        user = make_user(session)
        items = await closet_service.load_demo_closet(session, user.id)
        assert len(items) > 0
        assert all(item.is_demo for item in items)

    @pytest.mark.asyncio
    async def test_closet_stats(self, session):
        user = make_user(session)
        await closet_service.load_demo_closet(session, user.id)
        stats = await closet_service.get_closet_stats(session, user.id)
        assert stats["total"] > 0
        assert "categories" in stats
        assert "colors" in stats


class TestFeedbackLearning:
    @pytest.mark.asyncio
    async def test_like_outfit(self, session):
        user = make_user(session)
        # Load demo and generate
        items = await closet_service.load_demo_closet(session, user.id)
        req = GenerateOutfitsRequest(occasion="casual", max_outfits=3)
        result = await outfit_service.generate_outfits(session, user.id, req, {}, items)

        if result["count"] > 0:
            outfit_id = result["outfits"][0].id
            outfit = await outfit_service.like_outfit(session, outfit_id, user.id, liked=True)
            assert outfit.liked is True

    @pytest.mark.asyncio
    async def test_save_outfit(self, session):
        user = make_user(session)
        items = await closet_service.load_demo_closet(session, user.id)
        req = GenerateOutfitsRequest(occasion="casual", max_outfits=2)
        result = await outfit_service.generate_outfits(session, user.id, req, {}, items)

        if result["count"] > 0:
            outfit_id = result["outfits"][0].id
            saved = await outfit_service.save_outfit(session, outfit_id, user.id)
            assert saved.is_saved is True

            saved_list = await outfit_service.get_saved_outfits(session, user.id, items)
            assert any(o.id == outfit_id for o in saved_list)

    @pytest.mark.asyncio
    async def test_generate_outfits_empty_closet(self, session):
        user = make_user(session)
        req = GenerateOutfitsRequest(occasion="casual")
        result = await outfit_service.generate_outfits(session, user.id, req, {}, [])
        assert result["count"] == 0
        assert result["outfits"] == []
