"""E2E API tests — auth, profile, closet, outfits, social."""
import pytest
from fastapi.testclient import TestClient


# ── Helpers ──────────────────────────────────────────────────────────────────

def register(client, email="a@test.com", username="userA", password="pass1234"):
    r = client.post("/api/v1/auth/register", json={
        "email": email, "username": username, "password": password,
    })
    return r


def headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


ITEM = {
    "name": "Blue Jeans", "category": "bottom", "color": "blue",
    "style": "casual", "pattern": "solid", "formality": 2, "season": "all",
}


# ── Auth ─────────────────────────────────────────────────────────────────────

class TestAuth:
    def test_register_returns_token_and_user(self, client):
        r = register(client)
        assert r.status_code == 201
        d = r.json()
        assert "access_token" in d
        assert d["token_type"] == "bearer"
        u = d["user"]
        assert u["email"] == "a@test.com"
        assert u["username"] == "userA"
        # New profile fields present in response
        assert "gender" in u
        assert "country" in u
        assert "closet_visibility" in u
        assert u["closet_visibility"] == "private"

    def test_register_duplicate_email(self, client, sample_user):
        r = register(client, email="test@example.com")
        assert r.status_code == 409

    def test_login_success(self, client, sample_user):
        r = client.post("/api/v1/auth/login", data={
            "username": "test@example.com", "password": "securepass123",
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_login_wrong_password(self, client, sample_user):
        r = client.post("/api/v1/auth/login", data={
            "username": "test@example.com", "password": "wrong",
        })
        assert r.status_code == 401

    def test_get_me(self, client, auth_headers):
        r = client.get("/api/v1/auth/me", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["email"] == "test@example.com"

    def test_get_me_unauthorized(self, client):
        assert client.get("/api/v1/auth/me").status_code == 401

    def test_save_quiz_with_gender_country(self, client, auth_headers):
        r = client.post("/api/v1/auth/quiz", json={
            "preferred_styles": ["casual", "minimalist"],
            "formality_preference": 3,
            "color_preference": "mixed",
            "occasion_priority": "casual",
            "budget_sensitivity": "medium",
            "gender": "female",
            "country": "Kenya",
        }, headers=auth_headers)
        assert r.status_code == 200

        # Verify persisted
        me = client.get("/api/v1/auth/me", headers=auth_headers).json()
        assert me["gender"] == "female"
        assert me["country"] == "Kenya"


# ── Profile ───────────────────────────────────────────────────────────────────

class TestProfile:
    def test_update_profile(self, client, auth_headers):
        r = client.patch("/api/v1/auth/profile", json={
            "username": "updated_user",
            "bio": "I love fashion",
            "gender": "nonbinary",
            "country": "Nigeria",
        }, headers=auth_headers)
        assert r.status_code == 200
        d = r.json()
        assert d["username"] == "updated_user"
        assert d["bio"] == "I love fashion"
        assert d["gender"] == "nonbinary"
        assert d["country"] == "Nigeria"

    def test_update_closet_visibility(self, client, auth_headers):
        r = client.patch("/api/v1/auth/profile", json={
            "closet_visibility": "friends",
        }, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["closet_visibility"] == "friends"

    def test_change_password(self, client, sample_user):
        tok = sample_user["token"]
        r = client.post("/api/v1/auth/change-password", json={
            "current_password": "securepass123",
            "new_password": "newpass456",
        }, headers=headers(tok))
        assert r.status_code == 200

        # Old password should now fail
        bad = client.post("/api/v1/auth/login", data={
            "username": "test@example.com", "password": "securepass123",
        })
        assert bad.status_code == 401

        # New password works
        good = client.post("/api/v1/auth/login", data={
            "username": "test@example.com", "password": "newpass456",
        })
        assert good.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        r = client.post("/api/v1/auth/change-password", json={
            "current_password": "wrong",
            "new_password": "anything123",
        }, headers=auth_headers)
        assert r.status_code == 400


# ── Closet ────────────────────────────────────────────────────────────────────

class TestCloset:
    def test_add_item(self, client, auth_headers):
        r = client.post("/api/v1/closet", json=ITEM, headers=auth_headers)
        assert r.status_code == 201
        d = r.json()
        assert d["name"] == "Blue Jeans"
        assert "id" in d

    def test_get_closet_empty(self, client, auth_headers):
        r = client.get("/api/v1/closet", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_closet_with_items(self, client, auth_headers):
        client.post("/api/v1/closet", json=ITEM, headers=auth_headers)
        items = client.get("/api/v1/closet", headers=auth_headers).json()
        assert len(items) >= 1

    def test_update_item(self, client, auth_headers):
        item_id = client.post("/api/v1/closet", json=ITEM, headers=auth_headers).json()["id"]
        r = client.put(f"/api/v1/closet/{item_id}", json={"name": "Dark Jeans"}, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["name"] == "Dark Jeans"

    def test_delete_item(self, client, auth_headers):
        item_id = client.post("/api/v1/closet", json=ITEM, headers=auth_headers).json()["id"]
        assert client.delete(f"/api/v1/closet/{item_id}", headers=auth_headers).status_code == 204
        assert client.get(f"/api/v1/closet/{item_id}", headers=auth_headers).status_code == 404

    def test_filter_by_category(self, client, auth_headers):
        client.post("/api/v1/closet", json=ITEM, headers=auth_headers)
        client.post("/api/v1/closet", json={**ITEM, "category": "top", "name": "Tee"}, headers=auth_headers)
        items = client.get("/api/v1/closet?category=bottom&include_demo=false", headers=auth_headers).json()
        assert all(i["category"] == "bottom" for i in items)

    def test_load_demo_closet(self, client, auth_headers):
        r = client.post("/api/v1/closet/demo", headers=auth_headers)
        assert r.status_code == 200
        assert len(r.json()) > 0
        assert all(i["is_demo"] for i in r.json())

    def test_closet_stats(self, client, auth_headers):
        client.post("/api/v1/closet/demo", headers=auth_headers)
        r = client.get("/api/v1/closet/stats", headers=auth_headers)
        assert r.status_code == 200
        d = r.json()
        assert d["total"] > 0
        assert "categories" in d

    def test_unauthorized(self, client):
        assert client.get("/api/v1/closet").status_code == 401


# ── Outfits ───────────────────────────────────────────────────────────────────

class TestOutfits:
    def test_generate_no_items(self, client, auth_headers):
        r = client.post("/api/v1/outfits/generate", json={"occasion": "casual"}, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["count"] == 0

    def test_generate_with_demo_closet(self, client, auth_headers):
        client.post("/api/v1/closet/demo", headers=auth_headers)
        r = client.post("/api/v1/outfits/generate",
                        json={"occasion": "casual", "max_outfits": 3},
                        headers=auth_headers)
        assert r.status_code == 200
        d = r.json()
        assert d["count"] >= 1
        assert len(d["outfits"]) <= 3
        for outfit in d["outfits"]:
            assert len(outfit["items"]) >= 1
            # Each item now has proper fields (not empty {})
            for item in outfit["items"]:
                assert item.get("name"), f"item missing name: {item}"
                assert item.get("category")
            assert 0 <= outfit["compatibility_score"] <= 100
            assert isinstance(outfit["feedback"], list)

    def test_generate_all_occasions(self, client, auth_headers):
        client.post("/api/v1/closet/demo", headers=auth_headers)
        for occasion in ["casual", "work", "formal"]:
            r = client.post("/api/v1/outfits/generate",
                            json={"occasion": occasion}, headers=auth_headers)
            assert r.status_code == 200
            assert r.json()["occasion"] == occasion

    def test_save_and_retrieve_outfit(self, client, auth_headers):
        client.post("/api/v1/closet/demo", headers=auth_headers)
        gen = client.post("/api/v1/outfits/generate",
                          json={"occasion": "casual", "max_outfits": 2},
                          headers=auth_headers).json()
        if gen["count"] == 0:
            pytest.skip("No outfits generated")

        outfit_id = gen["outfits"][0]["id"]
        save_r = client.post(f"/api/v1/outfits/{outfit_id}/save", headers=auth_headers)
        assert save_r.status_code == 200

        saved = client.get("/api/v1/outfits/saved", headers=auth_headers).json()
        assert any(o["id"] == outfit_id for o in saved)

    def test_like_outfit(self, client, auth_headers):
        client.post("/api/v1/closet/demo", headers=auth_headers)
        gen = client.post("/api/v1/outfits/generate",
                          json={"occasion": "casual", "max_outfits": 1},
                          headers=auth_headers).json()
        if gen["count"] == 0:
            pytest.skip("No outfits generated")

        outfit_id = gen["outfits"][0]["id"]
        r = client.post(f"/api/v1/outfits/{outfit_id}/like",
                        json={"liked": True}, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["liked"] is True

    def test_saved_empty(self, client, auth_headers):
        assert client.get("/api/v1/outfits/saved", headers=auth_headers).json() == []


# ── Social ────────────────────────────────────────────────────────────────────

class TestSocial:
    def _make_user_b(self, client):
        r = register(client, email="b@test.com", username="userB", password="pass1234")
        assert r.status_code == 201
        d = r.json()
        return d["user"]["id"], d["access_token"]

    def test_search_users(self, client, sample_user, auth_headers):
        self._make_user_b(client)
        r = client.get("/api/v1/social/users/search?q=user", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        usernames = [u["username"] for u in r.json()]
        assert "userB" in usernames

    def test_get_user_profile(self, client, sample_user, auth_headers):
        uid_b, _ = self._make_user_b(client)
        r = client.get(f"/api/v1/social/users/{uid_b}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["username"] == "userB"
        # email must NOT be in public profile
        assert "email" not in r.json()

    def test_friend_request_flow(self, client, sample_user, auth_headers):
        uid_b, tok_b = self._make_user_b(client)

        # A sends request to B
        r = client.post(f"/api/v1/social/friends/{uid_b}", headers=auth_headers)
        assert r.status_code == 200
        fid = r.json()["friendship_id"]

        # B sees incoming request
        reqs = client.get("/api/v1/social/friends/requests", headers=headers(tok_b)).json()
        assert any(req["id"] == fid for req in reqs)

        # B accepts
        accept = client.post(f"/api/v1/social/friends/accept/{fid}", headers=headers(tok_b))
        assert accept.status_code == 200

        # A's friend list now includes B
        friends_a = client.get("/api/v1/social/friends", headers=auth_headers).json()
        assert any(f["id"] == uid_b for f in friends_a)

    def test_duplicate_friend_request_rejected(self, client, sample_user, auth_headers):
        uid_b, _ = self._make_user_b(client)
        client.post(f"/api/v1/social/friends/{uid_b}", headers=auth_headers)
        r = client.post(f"/api/v1/social/friends/{uid_b}", headers=auth_headers)
        assert r.status_code == 409

    def test_remove_friend(self, client, sample_user, auth_headers):
        uid_b, tok_b = self._make_user_b(client)
        r = client.post(f"/api/v1/social/friends/{uid_b}", headers=auth_headers)
        fid = r.json()["friendship_id"]
        client.post(f"/api/v1/social/friends/accept/{fid}", headers=headers(tok_b))

        del_r = client.delete(f"/api/v1/social/friends/{uid_b}", headers=auth_headers)
        assert del_r.status_code == 200

        friends_a = client.get("/api/v1/social/friends", headers=auth_headers).json()
        assert not any(f["id"] == uid_b for f in friends_a)

    def test_private_closet_blocked(self, client, sample_user, auth_headers):
        uid_b, tok_b = self._make_user_b(client)
        # B's closet is private (default)
        r = client.get(f"/api/v1/social/users/{uid_b}/closet", headers=auth_headers)
        assert r.status_code == 403

    def test_friends_closet_visible_after_share(self, client, sample_user, auth_headers):
        uid_b, tok_b = self._make_user_b(client)

        # B sets closet to friends
        client.patch("/api/v1/auth/profile",
                     json={"closet_visibility": "friends"}, headers=headers(tok_b))

        # Before friendship: still blocked
        assert client.get(f"/api/v1/social/users/{uid_b}/closet",
                          headers=auth_headers).status_code == 403

        # Become friends
        r = client.post(f"/api/v1/social/friends/{uid_b}", headers=auth_headers)
        fid = r.json()["friendship_id"]
        client.post(f"/api/v1/social/friends/accept/{fid}", headers=headers(tok_b))

        # Now A can see B's closet
        closet_r = client.get(f"/api/v1/social/users/{uid_b}/closet", headers=auth_headers)
        assert closet_r.status_code == 200
        assert isinstance(closet_r.json(), list)

    def test_public_closet_visible_to_anyone(self, client, sample_user, auth_headers):
        uid_b, tok_b = self._make_user_b(client)
        client.patch("/api/v1/auth/profile",
                     json={"closet_visibility": "public"}, headers=headers(tok_b))
        r = client.get(f"/api/v1/social/users/{uid_b}/closet", headers=auth_headers)
        assert r.status_code == 200

    def test_send_receive_recommendation(self, client, sample_user, auth_headers):
        uid_b, tok_b = self._make_user_b(client)
        uid_a = sample_user["user"]["id"]

        # Become friends first
        r = client.post(f"/api/v1/social/friends/{uid_b}", headers=auth_headers)
        fid = r.json()["friendship_id"]
        client.post(f"/api/v1/social/friends/accept/{fid}", headers=headers(tok_b))

        # B recommends an item to A
        rec_r = client.post("/api/v1/social/recommendations", json={
            "to_user_id": uid_a,
            "message": "You should add this!",
            "rec_type": "add",
        }, headers=headers(tok_b))
        assert rec_r.status_code == 201

        # A retrieves it
        recs = client.get("/api/v1/social/recommendations", headers=auth_headers).json()
        assert any(r["message"] == "You should add this!" for r in recs)

    def test_recommendation_requires_friendship(self, client, sample_user, auth_headers):
        uid_b, _ = self._make_user_b(client)
        uid_a = sample_user["user"]["id"]
        # Not friends yet — should fail
        r = client.post("/api/v1/social/recommendations", json={
            "to_user_id": uid_a, "message": "Nope", "rec_type": "add",
        }, headers=headers(register(client, "c@t.com", "userC", "p1234567").json()["access_token"]))
        assert r.status_code == 403

    def test_marketplace_listing(self, client, sample_user, auth_headers):
        # Add an item first
        item_id = client.post("/api/v1/closet", json=ITEM, headers=auth_headers).json()["id"]

        # List it for sale
        r = client.post("/api/v1/social/marketplace", json={
            "item_id": item_id,
            "price": 25.0,
            "currency": "USD",
            "description": "Barely worn",
        }, headers=auth_headers)
        assert r.status_code == 201
        listing_id = r.json()["id"]

        # Browse marketplace
        market = client.get("/api/v1/social/marketplace", headers=auth_headers).json()
        assert any(l["id"] == listing_id for l in market)

        # Mark sold
        sold = client.patch(f"/api/v1/social/marketplace/{listing_id}/sold", headers=auth_headers)
        assert sold.status_code == 200
        assert sold.json()["is_sold"] is True

    def test_friends_list_empty_initially(self, client, auth_headers):
        r = client.get("/api/v1/social/friends", headers=auth_headers)
        assert r.status_code == 200
        assert r.json() == []


# ── Health ────────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_root(self, client):
        assert client.get("/").status_code == 200

    def test_weather(self, client, auth_headers):
        r = client.get("/api/v1/weather?city=New+York", headers=auth_headers)
        assert r.status_code == 200
        assert "temperature_celsius" in r.json()
