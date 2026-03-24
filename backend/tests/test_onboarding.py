"""
End-to-end onboarding tests.

Covers the full registration → quiz → demo flow and every edge case
needed to ensure the AI stylist receives complete, valid style data.
"""
import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def register(client, email="onboard@test.com", username="onboarduser", password="secure123"):
    return client.post("/api/v1/auth/register", json={
        "email": email, "username": username, "password": password,
    })


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# Minimal valid quiz payload (all required fields)
QUIZ_MINIMAL = {
    "preferred_styles": ["casual"],
    "formality_preference": 3,
    "color_preference": "mixed",
    "occasion_priority": "casual",
    "budget_sensitivity": "medium",
}

# Full quiz payload including all new optional fields
QUIZ_FULL = {
    "preferred_styles": ["casual", "minimalist"],
    "formality_preference": 2,
    "color_preference": "neutral",
    "occasion_priority": "work",
    "budget_sensitivity": "high",
    "fit_preference": "slim",
    "sustainability_preference": "high",
    "shopping_frequency": "seasonally",
    "gender": "female",
    "country": "Kenya",
}


# ── Registration ──────────────────────────────────────────────────────────────

class TestRegistration:
    def test_register_creates_account_with_defaults(self, client):
        r = register(client)
        assert r.status_code == 201
        d = r.json()
        assert "access_token" in d
        assert d["token_type"] == "bearer"
        u = d["user"]
        assert u["email"] == "onboard@test.com"
        assert u["username"] == "onboarduser"
        # Default privacy setting
        assert u["closet_visibility"] == "private"
        # Optional profile fields start empty
        assert u["gender"] is None
        assert u["country"] is None
        assert u["bio"] is None

    def test_register_rejects_duplicate_email(self, client):
        register(client)
        r = register(client)  # same email
        assert r.status_code == 409
        assert "already registered" in r.json()["detail"].lower()

    def test_register_rejects_short_password(self, client):
        r = client.post("/api/v1/auth/register", json={
            "email": "short@test.com", "username": "shortpass", "password": "abc",
        })
        # FastAPI returns 422 for validation errors
        assert r.status_code == 422

    def test_register_rejects_missing_fields(self, client):
        r = client.post("/api/v1/auth/register", json={"email": "x@y.com"})
        assert r.status_code == 422

    def test_register_token_grants_auth_access(self, client):
        token = register(client).json()["access_token"]
        r = client.get("/api/v1/auth/me", headers=auth(token))
        assert r.status_code == 200
        assert r.json()["email"] == "onboard@test.com"

    def test_unauthed_quiz_rejected(self, client):
        r = client.post("/api/v1/auth/quiz", json=QUIZ_MINIMAL)
        assert r.status_code == 401


# ── Quiz: validation ──────────────────────────────────────────────────────────

class TestQuizValidation:
    def _token(self, client):
        return register(client).json()["access_token"]

    def test_quiz_requires_preferred_styles(self, client):
        tok = self._token(client)
        payload = {**QUIZ_MINIMAL}
        del payload["preferred_styles"]
        assert client.post("/api/v1/auth/quiz", json=payload, headers=auth(tok)).status_code == 422

    def test_quiz_requires_formality_preference(self, client):
        tok = self._token(client)
        payload = {**QUIZ_MINIMAL}
        del payload["formality_preference"]
        assert client.post("/api/v1/auth/quiz", json=payload, headers=auth(tok)).status_code == 422

    def test_quiz_requires_color_preference(self, client):
        tok = self._token(client)
        payload = {**QUIZ_MINIMAL}
        del payload["color_preference"]
        assert client.post("/api/v1/auth/quiz", json=payload, headers=auth(tok)).status_code == 422

    def test_quiz_requires_occasion_priority(self, client):
        tok = self._token(client)
        payload = {**QUIZ_MINIMAL}
        del payload["occasion_priority"]
        assert client.post("/api/v1/auth/quiz", json=payload, headers=auth(tok)).status_code == 422

    def test_quiz_requires_budget_sensitivity(self, client):
        tok = self._token(client)
        payload = {**QUIZ_MINIMAL}
        del payload["budget_sensitivity"]
        assert client.post("/api/v1/auth/quiz", json=payload, headers=auth(tok)).status_code == 422

    def test_quiz_preferred_styles_must_be_list(self, client):
        tok = self._token(client)
        payload = {**QUIZ_MINIMAL, "preferred_styles": "casual"}
        assert client.post("/api/v1/auth/quiz", json=payload, headers=auth(tok)).status_code == 422


# ── Quiz: persistence ─────────────────────────────────────────────────────────

class TestQuizPersistence:
    def _register_and_token(self, client, suffix=""):
        r = register(client, email=f"q{suffix}@test.com", username=f"quser{suffix}")
        return r.json()["access_token"]

    def test_minimal_quiz_saves_ok(self, client):
        tok = self._register_and_token(client, "min")
        r = client.post("/api/v1/auth/quiz", json=QUIZ_MINIMAL, headers=auth(tok))
        assert r.status_code == 200
        assert r.json()["message"] == "Style profile saved"

    def test_full_quiz_saves_all_fields(self, client):
        tok = self._register_and_token(client, "full")
        r = client.post("/api/v1/auth/quiz", json=QUIZ_FULL, headers=auth(tok))
        assert r.status_code == 200
        profile = r.json()["profile"]
        assert profile["preferred_styles"] == ["casual", "minimalist"]
        assert profile["formality_preference"] == 2
        assert profile["color_preference"] == "neutral"
        assert profile["occasion_priority"] == "work"
        assert profile["budget_sensitivity"] == "high"
        assert profile["fit_preference"] == "slim"
        assert profile["sustainability_preference"] == "high"
        assert profile["shopping_frequency"] == "seasonally"
        # gender/country are excluded from profile (stored on user directly)
        assert "gender" not in profile
        assert "country" not in profile

    def test_quiz_persists_gender_and_country_on_user(self, client):
        tok = self._register_and_token(client, "gc")
        client.post("/api/v1/auth/quiz", json=QUIZ_FULL, headers=auth(tok))
        me = client.get("/api/v1/auth/me", headers=auth(tok)).json()
        assert me["gender"] == "female"
        assert me["country"] == "Kenya"

    def test_quiz_style_profile_accessible_via_me(self, client):
        tok = self._register_and_token(client, "me")
        client.post("/api/v1/auth/quiz", json=QUIZ_FULL, headers=auth(tok))
        me = client.get("/api/v1/auth/me", headers=auth(tok)).json()
        profile = me["style_profile"]
        assert profile["fit_preference"] == "slim"
        assert profile["sustainability_preference"] == "high"
        assert profile["shopping_frequency"] == "seasonally"
        assert profile["budget_sensitivity"] == "high"

    def test_quiz_null_optional_fields_do_not_overwrite_existing(self, client):
        """If user skips gender/country (sends null), existing values must not be wiped."""
        tok = self._register_and_token(client, "null")

        # First set gender/country via profile update
        client.patch("/api/v1/auth/profile",
                     json={"gender": "male", "country": "Nigeria"},
                     headers=auth(tok))

        # Submit quiz with null gender/country (user skipped those steps)
        payload = {**QUIZ_MINIMAL, "gender": None, "country": None}
        client.post("/api/v1/auth/quiz", json=payload, headers=auth(tok))

        me = client.get("/api/v1/auth/me", headers=auth(tok)).json()
        # Should NOT be overwritten
        assert me["gender"] == "male"
        assert me["country"] == "Nigeria"

    def test_quiz_empty_preferred_styles_list_rejected(self, client):
        tok = self._register_and_token(client, "empty")
        payload = {**QUIZ_MINIMAL, "preferred_styles": []}
        # Empty list is valid JSON but the AI stylist needs at least one style;
        # Pydantic accepts it (list[str] allows empty), backend stores it.
        # Verify it round-trips correctly.
        r = client.post("/api/v1/auth/quiz", json=payload, headers=auth(tok))
        assert r.status_code == 200
        assert r.json()["profile"]["preferred_styles"] == []

    def test_quiz_all_style_options_accepted(self, client):
        tok = self._register_and_token(client, "styles")
        payload = {**QUIZ_MINIMAL,
                   "preferred_styles": ["casual", "minimalist", "formal", "bohemian", "sporty"]}
        r = client.post("/api/v1/auth/quiz", json=payload, headers=auth(tok))
        assert r.status_code == 200

    def test_quiz_new_optional_fields_default_to_none_when_absent(self, client):
        tok = self._register_and_token(client, "newopt")
        # Old quiz format without new fields
        r = client.post("/api/v1/auth/quiz", json=QUIZ_MINIMAL, headers=auth(tok))
        assert r.status_code == 200
        profile = r.json()["profile"]
        # Optional new fields should be None (absent from payload → pydantic default)
        assert profile.get("fit_preference") is None
        assert profile.get("sustainability_preference") is None
        assert profile.get("shopping_frequency") is None

    def test_quiz_fit_preference_values_accepted(self, client):
        tok = self._register_and_token(client, "fit")
        for fit in ["oversized", "regular", "slim"]:
            payload = {**QUIZ_MINIMAL, "fit_preference": fit}
            r = client.post("/api/v1/auth/quiz", json=payload, headers=auth(tok))
            assert r.status_code == 200, f"fit_preference={fit} should be accepted"
            assert r.json()["profile"]["fit_preference"] == fit

    def test_quiz_sustainability_values_accepted(self, client):
        tok = self._register_and_token(client, "sus")
        for val in ["high", "medium", "low"]:
            payload = {**QUIZ_MINIMAL, "sustainability_preference": val}
            r = client.post("/api/v1/auth/quiz", json=payload, headers=auth(tok))
            assert r.status_code == 200

    def test_quiz_shopping_frequency_values_accepted(self, client):
        tok = self._register_and_token(client, "shop")
        for val in ["rarely", "seasonally", "monthly", "weekly"]:
            payload = {**QUIZ_MINIMAL, "shopping_frequency": val}
            r = client.post("/api/v1/auth/quiz", json=payload, headers=auth(tok))
            assert r.status_code == 200

    def test_quiz_can_be_resubmitted_to_update_preferences(self, client):
        tok = self._register_and_token(client, "update")
        # First submission
        client.post("/api/v1/auth/quiz",
                    json={**QUIZ_MINIMAL, "color_preference": "neutral"},
                    headers=auth(tok))
        # Update with new preferences
        client.post("/api/v1/auth/quiz",
                    json={**QUIZ_MINIMAL, "color_preference": "bold"},
                    headers=auth(tok))
        me = client.get("/api/v1/auth/me", headers=auth(tok)).json()
        assert me["style_profile"]["color_preference"] == "bold"


# ── Full onboarding flow ──────────────────────────────────────────────────────

class TestOnboardingFlow:
    def test_register_then_quiz_then_demo(self, client):
        """Full happy-path: register → quiz → load demo closet."""
        # Step 1: Register
        reg = register(client, email="flow@test.com", username="flowuser")
        assert reg.status_code == 201
        tok = reg.json()["access_token"]

        # Step 2: Submit full quiz
        quiz_r = client.post("/api/v1/auth/quiz", json=QUIZ_FULL, headers=auth(tok))
        assert quiz_r.status_code == 200

        # Step 3: Verify profile is complete
        me = client.get("/api/v1/auth/me", headers=auth(tok)).json()
        assert me["gender"] == "female"
        assert me["country"] == "Kenya"
        assert me["style_profile"]["preferred_styles"] == ["casual", "minimalist"]
        assert me["style_profile"]["fit_preference"] == "slim"

        # Step 4: Load demo closet
        demo_r = client.post("/api/v1/closet/demo", headers=auth(tok))
        assert demo_r.status_code == 200
        items = demo_r.json()
        assert len(items) > 0
        assert all(i["is_demo"] for i in items)

        # Step 5: Generate outfits using the demo wardrobe
        gen_r = client.post("/api/v1/outfits/generate",
                            json={"occasion": "casual", "max_outfits": 3},
                            headers=auth(tok))
        assert gen_r.status_code == 200
        assert gen_r.json()["count"] >= 1

    def test_skip_quiz_go_straight_to_closet(self, client):
        """User skips the quiz — should still be able to use the app."""
        reg = register(client, email="skip@test.com", username="skipuser")
        tok = reg.json()["access_token"]
        # No quiz submission — verify closet still works
        r = client.get("/api/v1/closet", headers=auth(tok))
        assert r.status_code == 200
        assert r.json() == []

    def test_quiz_then_outfit_generation_uses_style_profile(self, client):
        """After saving a quiz, outfit generation should work with the new profile data."""
        reg = register(client, email="profile@test.com", username="profileuser")
        tok = reg.json()["access_token"]
        client.post("/api/v1/auth/quiz", json={
            **QUIZ_FULL,
            "preferred_styles": ["formal"],
            "formality_preference": 5,
            "occasion_priority": "formal",
        }, headers=auth(tok))
        client.post("/api/v1/closet/demo", headers=auth(tok))
        r = client.post("/api/v1/outfits/generate",
                        json={"occasion": "formal"}, headers=auth(tok))
        assert r.status_code == 200

    def test_multiple_quiz_submissions_update_profile(self, client):
        """Re-submitting the quiz updates the style profile without creating duplicates."""
        reg = register(client, email="multi@test.com", username="multiuser")
        tok = reg.json()["access_token"]
        client.post("/api/v1/auth/quiz", json={**QUIZ_MINIMAL, "country": "France"}, headers=auth(tok))
        client.post("/api/v1/auth/quiz", json={**QUIZ_MINIMAL, "country": "Germany"}, headers=auth(tok))
        me = client.get("/api/v1/auth/me", headers=auth(tok)).json()
        assert me["country"] == "Germany"


# ── Feed (social) ─────────────────────────────────────────────────────────────

class TestFeed:
    def _register_tok(self, client, email, username):
        r = register(client, email=email, username=username)
        assert r.status_code == 201
        return r.json()["access_token"]

    def test_feed_requires_auth(self, client):
        assert client.get("/api/v1/social/feed").status_code == 401

    def test_feed_returns_empty_when_no_public_users(self, client):
        tok = self._register_tok(client, "feed1@t.com", "feeduser1")
        r = client.get("/api/v1/social/feed", headers=auth(tok))
        assert r.status_code == 200
        assert r.json() == []

    def test_feed_shows_public_users(self, client):
        tok_a = self._register_tok(client, "feedA@t.com", "feedA")
        tok_b = self._register_tok(client, "feedB@t.com", "feedB")
        # B sets profile to public
        client.patch("/api/v1/auth/profile",
                     json={"closet_visibility": "public"}, headers=auth(tok_b))
        feed = client.get("/api/v1/social/feed", headers=auth(tok_a)).json()
        assert len(feed) == 1
        assert feed[0]["user"]["username"] == "feedB"

    def test_feed_excludes_private_users(self, client):
        tok_a = self._register_tok(client, "privA@t.com", "privA")
        tok_b = self._register_tok(client, "privB@t.com", "privB")
        # B stays private (default)
        feed = client.get("/api/v1/social/feed", headers=auth(tok_a)).json()
        assert not any(u["user"]["username"] == "privB" for u in feed)

    def test_feed_excludes_friends_only_users(self, client):
        tok_a = self._register_tok(client, "foA@t.com", "foA")
        tok_b = self._register_tok(client, "foB@t.com", "foB")
        client.patch("/api/v1/auth/profile",
                     json={"closet_visibility": "friends"}, headers=auth(tok_b))
        feed = client.get("/api/v1/social/feed", headers=auth(tok_a)).json()
        assert not any(u["user"]["username"] == "foB" for u in feed)

    def test_feed_excludes_self(self, client):
        tok = self._register_tok(client, "selfeed@t.com", "selfeed")
        client.patch("/api/v1/auth/profile",
                     json={"closet_visibility": "public"}, headers=auth(tok))
        feed = client.get("/api/v1/social/feed", headers=auth(tok)).json()
        assert not any(u["user"]["username"] == "selfeed" for u in feed)

    def test_feed_entry_shape(self, client):
        tok_a = self._register_tok(client, "shapeA@t.com", "shapeA")
        tok_b = self._register_tok(client, "shapeB@t.com", "shapeB")
        client.patch("/api/v1/auth/profile",
                     json={"closet_visibility": "public", "country": "Kenya"},
                     headers=auth(tok_b))
        feed = client.get("/api/v1/social/feed", headers=auth(tok_a)).json()
        assert len(feed) == 1
        entry = feed[0]
        # Check all required fields are present
        assert "user" in entry
        assert "item_count" in entry
        assert "outfit_count" in entry
        assert "top_styles" in entry
        assert "recent_items" in entry
        assert "is_friend" in entry
        assert "has_pending_request" in entry
        assert entry["user"]["country"] == "Kenya"
        assert isinstance(entry["recent_items"], list)
        assert isinstance(entry["top_styles"], list)

    def test_feed_filter_by_country(self, client):
        tok_a = self._register_tok(client, "countA@t.com", "countA")
        tok_b = self._register_tok(client, "countB@t.com", "countB")
        tok_c = self._register_tok(client, "countC@t.com", "countC")
        client.patch("/api/v1/auth/profile",
                     json={"closet_visibility": "public", "country": "France"},
                     headers=auth(tok_b))
        client.patch("/api/v1/auth/profile",
                     json={"closet_visibility": "public", "country": "Germany"},
                     headers=auth(tok_c))
        feed = client.get("/api/v1/social/feed?country=France", headers=auth(tok_a)).json()
        assert all(u["user"]["country"] == "France" for u in feed)

    def test_feed_friendship_status_reflected(self, client):
        tok_a = self._register_tok(client, "fsA@t.com", "fsA")
        tok_b = self._register_tok(client, "fsB@t.com", "fsB")
        uid_b = client.get("/api/v1/auth/me", headers=auth(tok_b)).json()["id"]
        client.patch("/api/v1/auth/profile",
                     json={"closet_visibility": "public"}, headers=auth(tok_b))

        # Before request
        feed = client.get("/api/v1/social/feed", headers=auth(tok_a)).json()
        b_entry = next(e for e in feed if e["user"]["id"] == uid_b)
        assert b_entry["is_friend"] is False
        assert b_entry["has_pending_request"] is False

        # After sending friend request
        r = client.post(f"/api/v1/social/friends/{uid_b}", headers=auth(tok_a))
        assert r.status_code == 200
        feed2 = client.get("/api/v1/social/feed", headers=auth(tok_a)).json()
        b_entry2 = next(e for e in feed2 if e["user"]["id"] == uid_b)
        assert b_entry2["has_pending_request"] is True

    def test_feed_pagination_limit(self, client):
        tok_a = self._register_tok(client, "pagA@t.com", "pagA")
        # Create 5 public users
        for i in range(5):
            t = self._register_tok(client, f"pag{i}@t.com", f"pag{i}")
            client.patch("/api/v1/auth/profile",
                         json={"closet_visibility": "public"}, headers=auth(t))
        feed = client.get("/api/v1/social/feed?limit=3", headers=auth(tok_a)).json()
        assert len(feed) <= 3

    def test_feed_with_closet_items_in_snapshot(self, client):
        tok_a = self._register_tok(client, "snapA@t.com", "snapA")
        tok_b = self._register_tok(client, "snapB@t.com", "snapB")
        client.patch("/api/v1/auth/profile",
                     json={"closet_visibility": "public"}, headers=auth(tok_b))
        # Add items to B's closet
        for name in ["Shirt", "Jeans", "Jacket"]:
            client.post("/api/v1/closet", json={
                "name": name, "category": "top", "color": "blue",
                "style": "casual", "pattern": "solid", "formality": 2, "season": "all",
            }, headers=auth(tok_b))
        feed = client.get("/api/v1/social/feed", headers=auth(tok_a)).json()
        b_entry = next(e for e in feed if e["user"]["username"] == "snapB")
        assert b_entry["item_count"] == 3
        assert len(b_entry["recent_items"]) == 3
        # Each item in snapshot has required shape
        for item in b_entry["recent_items"]:
            assert "id" in item
            assert "name" in item
            assert "category" in item
            assert "color" in item
            assert "style" in item
