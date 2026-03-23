"""Tests for the AI compatibility engine."""
import pytest
from src.ai.color_analyzer import (
    color_harmony_score,
    outfit_color_harmony,
    is_neutral,
    get_color_group,
)
from src.ai.rules_engine import (
    formality_compatible,
    style_compatible,
    outfit_complete,
    weather_appropriate,
)
from src.ai.compatibility import score_outfit, generate_outfit_description
from src.models.clothing import ClothingItem, Category, Style, Season, Pattern


def make_item(**kwargs) -> ClothingItem:
    defaults = {
        "id": "test-id",
        "user_id": "user-id",
        "name": "Test Item",
        "category": Category.top,
        "color": "white",
        "style": Style.casual,
        "pattern": Pattern.solid,
        "formality": 2,
        "season": Season.all,
        "times_worn": 0,
    }
    defaults.update(kwargs)
    return ClothingItem(**defaults)


# --- Color Analyzer Tests ---

class TestColorAnalyzer:
    def test_neutral_detection(self):
        assert is_neutral("white")
        assert is_neutral("black")
        assert is_neutral("gray")
        assert is_neutral("beige")
        assert not is_neutral("red")
        assert not is_neutral("blue")

    def test_color_groups(self):
        assert get_color_group("red") == "warm"
        assert get_color_group("blue") == "cool"
        assert get_color_group("white") == "neutral"
        assert get_color_group("green") == "green"

    def test_neutral_harmony_score(self):
        """Neutrals should always score high."""
        score = color_harmony_score("white", "black")
        assert score >= 0.85

    def test_complementary_harmony(self):
        """Complementary pairs should score high."""
        score = color_harmony_score("navy", "gold")
        assert score >= 0.80

    def test_same_color(self):
        """Same color should score moderately."""
        score = color_harmony_score("blue", "blue")
        assert 0.65 <= score <= 0.85

    def test_outfit_all_neutrals(self):
        """All-neutral outfit should score very high."""
        score, feedback = outfit_color_harmony(["white", "black", "gray"])
        assert score >= 0.88
        assert any("neutral" in f.lower() for f in feedback)

    def test_outfit_one_accent(self):
        """Neutral base + one accent should score high."""
        score, feedback = outfit_color_harmony(["white", "navy", "beige"])
        assert score >= 0.80


# --- Rules Engine Tests ---

class TestFormalityMatching:
    def test_consistent_formality(self):
        """Items with same formality should score perfectly."""
        items = [
            make_item(formality=3, id="1"),
            make_item(formality=3, id="2"),
        ]
        is_compat, score, feedback = formality_compatible(items, "work")
        assert is_compat
        assert score >= 0.95

    def test_small_formality_gap(self):
        """Gap of 1 should be compatible."""
        items = [
            make_item(formality=2, id="1"),
            make_item(formality=3, id="2"),
        ]
        is_compat, score, _ = formality_compatible(items, "casual")
        assert is_compat
        assert score >= 0.75

    def test_large_formality_gap(self):
        """Gap of 4 should score very low."""
        items = [
            make_item(formality=1, id="1"),
            make_item(formality=5, id="2"),
        ]
        is_compat, score, _ = formality_compatible(items, "casual")
        assert not is_compat
        assert score < 0.40

    def test_empty_items(self):
        is_compat, score, _ = formality_compatible([], "casual")
        assert is_compat
        assert score == 1.0


class TestStyleCompatibility:
    def test_same_style(self):
        items = [
            make_item(style=Style.casual, id="1"),
            make_item(style=Style.casual, id="2"),
        ]
        score, feedback = style_compatible(items)
        assert score == 1.0

    def test_compatible_styles(self):
        """Casual + minimalist should work."""
        items = [
            make_item(style=Style.casual, id="1"),
            make_item(style=Style.minimalist, id="2"),
        ]
        score, _ = style_compatible(items)
        assert score >= 0.80

    def test_incompatible_styles(self):
        """Sporty + formal should score low."""
        items = [
            make_item(style=Style.sporty, id="1"),
            make_item(style=Style.formal, id="2"),
        ]
        score, feedback = style_compatible(items)
        assert score < 0.80

    def test_single_item(self):
        items = [make_item(style=Style.casual)]
        score, _ = style_compatible(items)
        assert score == 1.0


class TestOutfitCompleteness:
    def test_complete_casual_outfit(self):
        items = [
            make_item(category=Category.top, id="1"),
            make_item(category=Category.bottom, id="2"),
        ]
        is_complete, score = outfit_complete(items, "casual")
        assert is_complete
        assert score >= 0.85

    def test_complete_with_shoes(self):
        items = [
            make_item(category=Category.top, id="1"),
            make_item(category=Category.bottom, id="2"),
            make_item(category=Category.shoes, id="3"),
        ]
        is_complete, score = outfit_complete(items, "casual")
        assert is_complete
        assert score >= 0.90

    def test_dress_is_complete(self):
        items = [make_item(category=Category.dress, id="1")]
        is_complete, score = outfit_complete(items, "casual")
        assert is_complete

    def test_incomplete_outfit(self):
        """Only a top is not a complete outfit."""
        items = [make_item(category=Category.top, id="1")]
        is_complete, score = outfit_complete(items, "casual")
        assert not is_complete


class TestWeatherAppropriate:
    def test_cold_weather_with_coat(self):
        items = [
            make_item(category=Category.top, id="1"),
            make_item(category=Category.outerwear, id="2"),
        ]
        score, feedback = weather_appropriate(items, temperature=5)
        assert score >= 0.95

    def test_cold_weather_without_coat(self):
        items = [make_item(category=Category.top, id="1")]
        score, feedback = weather_appropriate(items, temperature=5)
        assert score <= 0.60

    def test_hot_weather_with_coat(self):
        items = [
            make_item(category=Category.top, id="1"),
            make_item(category=Category.outerwear, id="2"),
        ]
        score, feedback = weather_appropriate(items, temperature=30)
        assert score < 0.80

    def test_no_temperature(self):
        items = [make_item(category=Category.top, id="1")]
        score, _ = weather_appropriate(items, temperature=None)
        assert 0.80 <= score <= 0.90


# --- Full Scoring Tests ---

class TestScoreOutfit:
    def test_perfect_outfit(self):
        """Well-coordinated outfit should score high."""
        items = [
            make_item(category=Category.top, color="white", style=Style.minimalist,
                      formality=3, id="1"),
            make_item(category=Category.bottom, color="navy", style=Style.minimalist,
                      formality=3, id="2"),
            make_item(category=Category.shoes, color="white", style=Style.casual,
                      formality=2, id="3"),
        ]
        score, breakdown = score_outfit(items, occasion="casual")
        assert score >= 65  # Should score above 65
        assert "formality" in breakdown
        assert "color" in breakdown
        assert "style" in breakdown

    def test_formality_mismatch_penalty(self):
        """Huge formality gap should significantly lower score."""
        items = [
            make_item(category=Category.top, formality=1, id="1"),
            make_item(category=Category.bottom, formality=5, id="2"),
        ]
        score, _ = score_outfit(items, occasion="casual")
        assert score < 60

    def test_empty_items(self):
        score, breakdown = score_outfit([], occasion="casual")
        assert score == 0.0

    def test_description_generated(self):
        items = [
            make_item(category=Category.top, color="white", name="White Shirt", id="1"),
            make_item(category=Category.bottom, color="navy", name="Navy Pants", id="2"),
        ]
        desc = generate_outfit_description(items, "casual", 75.0)
        assert "white" in desc.lower() or "White" in desc
        assert len(desc) > 10
