"""
Compatibility scorer — combines all rule engines into a single score.

Weights:
  - Formality consistency: 30%
  - Color harmony:         25%
  - Style coherence:       20%
  - Completeness:          15%
  - Weather/season:        10%
"""
from typing import List, Tuple, Optional, Dict, Any
from ..models.clothing import ClothingItem
from .color_analyzer import outfit_color_harmony
from .rules_engine import (
    formality_compatible,
    style_compatible,
    season_compatible,
    outfit_complete,
    weather_appropriate,
)


WEIGHTS = {
    "formality": 0.30,
    "color": 0.25,
    "style": 0.20,
    "completeness": 0.15,
    "weather": 0.10,
}


def score_outfit(
    items: List[ClothingItem],
    occasion: str = "casual",
    temperature: Optional[float] = None,
    current_season: Optional[str] = None,
) -> Tuple[float, Dict[str, Any]]:
    """
    Score an outfit combination.
    Returns (total_score 0-100, breakdown_dict).
    """
    if not items:
        return 0.0, {}

    # --- Formality ---
    _, formality_score, formality_feedback = formality_compatible(items, occasion)

    # --- Color ---
    colors = [item.color for item in items]
    secondary = [item.secondary_color for item in items if item.secondary_color]
    all_colors = colors + secondary
    color_score, color_feedback = outfit_color_harmony(all_colors)

    # --- Style ---
    style_score, style_feedback = style_compatible(items)

    # --- Completeness ---
    _, completeness_score = outfit_complete(items, occasion)

    # --- Weather/Season ---
    weather_score, weather_feedback = weather_appropriate(items, temperature)
    season_score = season_compatible(items, current_season)
    combined_weather = (weather_score + season_score) / 2

    # --- Total ---
    total = (
        formality_score * WEIGHTS["formality"]
        + color_score * WEIGHTS["color"]
        + style_score * WEIGHTS["style"]
        + completeness_score * WEIGHTS["completeness"]
        + combined_weather * WEIGHTS["weather"]
    )

    score_100 = round(total * 100, 1)

    breakdown = {
        "total": score_100,
        "formality": round(formality_score * 100, 1),
        "color": round(color_score * 100, 1),
        "style": round(style_score * 100, 1),
        "completeness": round(completeness_score * 100, 1),
        "weather": round(combined_weather * 100, 1),
        "feedback": [f for f in [formality_feedback, style_feedback, weather_feedback] if f]
        + color_feedback,
    }

    return score_100, breakdown


def generate_outfit_description(
    items: List[ClothingItem],
    occasion: str,
    score: float,
) -> str:
    """Generate a human-readable outfit description."""
    if not items:
        return ""

    cats = {item.category.value: item for item in items}
    parts = []

    if "top" in cats:
        t = cats["top"]
        parts.append(f"{t.color} {t.name}")
    elif "dress" in cats:
        d = cats["dress"]
        parts.append(f"{d.color} {d.name}")

    if "bottom" in cats:
        b = cats["bottom"]
        parts.append(f"{b.color} {b.name}")

    if "outerwear" in cats:
        o = cats["outerwear"]
        parts.append(f"{o.color} {o.name}")

    if "shoes" in cats:
        s = cats["shoes"]
        parts.append(f"{s.color} {s.name}")

    outfit_str = " + ".join(parts) if parts else "outfit"

    occasion_map = {
        "casual": "a relaxed casual look",
        "work": "a professional work ensemble",
        "formal": "an elegant formal outfit",
        "party": "a fun party look",
        "date": "a stylish date-night outfit",
        "sport": "an athletic look",
    }

    occ_desc = occasion_map.get(occasion, f"a {occasion} outfit")
    quality = "excellent" if score >= 85 else "great" if score >= 70 else "solid"

    return f"A {quality} {occ_desc}: {outfit_str}"


def apply_user_preferences(
    score: float,
    items: List[ClothingItem],
    style_profile: Dict[str, Any],
) -> float:
    """Adjust score based on user style preferences."""
    if not style_profile:
        return score

    preferred_styles = style_profile.get("preferred_styles", [])
    formality_pref = style_profile.get("formality_preference", 3)

    item_styles = [item.style.value for item in items]
    style_match = sum(1 for s in item_styles if s in preferred_styles)
    style_bonus = (style_match / max(len(item_styles), 1)) * 5  # up to +5 pts

    item_formalities = [item.formality for item in items]
    avg_formality = sum(item_formalities) / len(item_formalities)
    formality_diff = abs(avg_formality - formality_pref)
    formality_adj = max(-5, -formality_diff * 2)  # up to -10 pts

    adjusted = score + style_bonus + formality_adj
    return round(min(100.0, max(0.0, adjusted)), 1)
