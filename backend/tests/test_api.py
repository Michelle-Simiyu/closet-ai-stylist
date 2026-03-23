"""Tests for the REST API endpoints."""
import pytest
from fastapi.testclient import TestClient


class TestAuth:
    def test_register_new_user(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepass123",
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@example.com"

    def test_register_duplicate_email(self, client, sample_user):
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "another",
            "password": "pass123",
        })
        assert response.status_code == 409

    def test_login_success(self, client, sample_user):
        response = client.post("/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "securepass123",
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client, sample_user):
        response = client.post("/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "wrongpass",
        })
        assert response.status_code == 401

    def test_get_me(self, client, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    def test_get_me_unauthorized(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestCloset:
    ITEM_DATA = {
        "name": "Blue Jeans",
        "category": "bottom",
        "color": "blue",
        "style": "casual",
        "pattern": "solid",
        "formality": 2,
        "season": "all",
    }

    def test_add_item(self, client, auth_headers):
        response = client.post("/api/v1/closet", json=self.ITEM_DATA, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Blue Jeans"
        assert data["category"] == "bottom"
        assert "id" in data

    def test_get_closet_empty(self, client, auth_headers):
        response = client.get("/api/v1/closet", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_closet_with_items(self, client, auth_headers):
        client.post("/api/v1/closet", json=self.ITEM_DATA, headers=auth_headers)
        response = client.get("/api/v1/closet", headers=auth_headers)
        assert response.status_code == 200
        items = response.json()
        assert len(items) >= 1

    def test_update_item(self, client, auth_headers):
        # Create item
        create_response = client.post("/api/v1/closet", json=self.ITEM_DATA, headers=auth_headers)
        item_id = create_response.json()["id"]

        # Update it
        response = client.put(
            f"/api/v1/closet/{item_id}",
            json={"name": "Updated Jeans", "color": "dark blue"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Jeans"

    def test_delete_item(self, client, auth_headers):
        create_response = client.post("/api/v1/closet", json=self.ITEM_DATA, headers=auth_headers)
        item_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/closet/{item_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/api/v1/closet/{item_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_filter_by_category(self, client, auth_headers):
        client.post("/api/v1/closet", json=self.ITEM_DATA, headers=auth_headers)
        client.post("/api/v1/closet", json={**self.ITEM_DATA, "category": "top", "name": "T-Shirt"}, headers=auth_headers)

        response = client.get("/api/v1/closet?category=bottom&include_demo=false", headers=auth_headers)
        items = response.json()
        assert all(item["category"] == "bottom" for item in items)

    def test_load_demo_closet(self, client, auth_headers):
        response = client.post("/api/v1/closet/demo", headers=auth_headers)
        assert response.status_code == 200
        items = response.json()
        assert len(items) > 0
        assert all(item["is_demo"] for item in items)

    def test_closet_stats(self, client, auth_headers):
        client.post("/api/v1/closet/demo", headers=auth_headers)
        response = client.get("/api/v1/closet/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "categories" in data

    def test_unauthorized_access(self, client):
        response = client.get("/api/v1/closet")
        assert response.status_code == 401


class TestOutfits:
    def test_generate_outfits_no_items(self, client, auth_headers):
        response = client.post(
            "/api/v1/outfits/generate",
            json={"occasion": "casual"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["outfits"] == []
        assert data["count"] == 0

    def test_generate_outfits_with_demo_closet(self, client, auth_headers):
        # Load demo closet first
        client.post("/api/v1/closet/demo", headers=auth_headers)

        response = client.post(
            "/api/v1/outfits/generate",
            json={"occasion": "casual", "max_outfits": 3},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        assert len(data["outfits"]) <= 3
        assert data["occasion"] == "casual"

        # Each outfit should have items and a score
        for outfit in data["outfits"]:
            assert len(outfit["items"]) >= 1
            assert 0 <= outfit["compatibility_score"] <= 100

    def test_generate_outfits_occasions(self, client, auth_headers):
        client.post("/api/v1/closet/demo", headers=auth_headers)

        for occasion in ["casual", "work", "formal"]:
            response = client.post(
                "/api/v1/outfits/generate",
                json={"occasion": occasion},
                headers=auth_headers,
            )
            assert response.status_code == 200
            assert response.json()["occasion"] == occasion

    def test_get_saved_outfits_empty(self, client, auth_headers):
        response = client.get("/api/v1/outfits/saved", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []


class TestHealthEndpoints:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_weather(self, client, auth_headers):
        response = client.get("/api/v1/weather?city=New+York", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "temperature_celsius" in data
        assert "condition" in data
