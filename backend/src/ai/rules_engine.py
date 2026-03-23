"""
Rule-based styling engine for outfit generation.
Defines which clothing items work together based on fashion rules.
"""
from typing import List, Dict, Tuple, Optional
from ..models.clothing import ClothingItem, Category, Style, Season


# What categories are needed for a complete outfit
OUTFIT_TEMPLATES = {
    "casual": [
        [Category.top, Category.bottom],
        [Category.top, Category.bottom, Category.shoes],
        [Category.top, Category.bottom, Category.outerwear],
        [Category.dress],
        [Category.dress, Category.outerwear],
    ],
    "work": [
        [Category.top, Category.bottom],
        [Category.top, Category.bottom, Category.outerwear],
        [Category.dress],
        [Category.dress, Category.outerwear],
    ],
    "formal": [
        [Category.top, Category.bottom],
        [Category.top, Category.bottom, Category.outerwear],
        [Category.dress],
        [Category.dress, Category.outerwear],
    ],
    "party": [
        [Category.dress],
        [Category.top, Category.bottom],
        [Category.dress, Category.outerwear],
    ],
    "date": [
        [Category.dress],
        [Category.top, Category.bottom],
        [Category.dress, Category.outerwear],
    ],
    "sport": [
        [Category.top, Category.bottom],
        [Category.top, Category.bottom, Category.outerwear],
    ],
}

# Formality mappings per occasion
OCCASION_FORMALITY: Dict[str, Tuple[int, int]] = {
    "casual": (1, 3),
    "work": (2, 4),
    "formal": (3, 5),
    "party": (2, 5),
    "date": (2, 5),
    "sport": (1, 2),
}

# Style compatibility matrix (which styles work together)
STYLE_COMPATIBILITY: Dict[str, List[str]] = {
    "casual": ["casual", "sporty", "bohemian", "minimalist"],
    "formal": ["formal", "minimalist"],
    "sporty": ["casual", "sporty"],
    "bohemian": ["casual", "bohemian"],
    "minimalist": ["casual", "formal", "minimalist"],
}

# Season compatibility
SEASON_COMPAT: Dict[str, List[str]] = {
    "summer": ["summer", "all", "spring"],
    "winter": ["winter", "all", "fall"],
    "spring": ["spring", "all", "summer"],
    "fall": ["fall", "all", "winter"],
    "all": ["summer", "winter", "spring", "fall", "all"],
}


def formality_compatible(items: List[ClothingItem], occasion: str) -> Tuple[bool, float, str]:
    """
    Check if formality levels are compatible.
    Returns (is_compatible, score, feedback).
    """
    if not items:
        return True, 1.0, ""

    formalitites = [item.formality for item in items]
    min_f = min(formalitites)
    max_f = max(formalitites)
    gap = max_f - min_f

    min_ok, max_ok = OCCASION_FORMALITY.get(occasion, (1, 5))

    # Check all items are in occasion range
    in_range = all(min_ok <= f <= max_ok for f in formalitites)

    if gap <= 1:
        score = 1.0
        feedback = "Formality levels are perfectly consistent"
    elif gap == 2:
        score = 0.80
        feedback = "Slight formality variation adds interest"
    elif gap == 3:
        score = 0.50
        feedback = "Consider matching formality levels more closely"
    else:
        score = 0.20
        feedback = "Formality mismatch — pieces don't belong to the same dress code"

    if not in_range:
        score *= 0.70
        feedback += f" (some items may be too casual/formal for {occasion})"

    return gap <= 2, score, feedback


def style_compatible(items: List[ClothingItem]) -> Tuple[float, str]:
    """
    Check style coherence across items.
    Returns (score, feedback).
    """
    if not items:
        return 1.0, ""

    styles = [item.style.value for item in items]
    dominant_style = max(set(styles), key=styles.count)
    compatible_styles = STYLE_COMPATIBILITY.get(dominant_style, [dominant_style])

    incompatible = [s for s in styles if s not in compatible_styles]

    if not incompatible:
        style_map = {
            "casual": "Cohesive casual look",
            "formal": "Polished formal ensemble",
            "sporty": "Athletic and active vibe",
            "bohemian": "Free-spirited bohemian style",
            "minimalist": "Clean minimalist aesthetic",
        }
        return 1.0, style_map.get(dominant_style, "Consistent style")

    ratio = len(incompatible) / len(styles)
    score = 1.0 - (ratio * 0.6)
    return round(score, 3), "Mixed style signals — consider a more unified aesthetic"


def season_compatible(items: List[ClothingItem], current_season: Optional[str] = None) -> float:
    """Check season appropriateness."""
    if not items or not current_season:
        return 0.85

    compatible_seasons = SEASON_COMPAT.get(current_season, [current_season, "all"])
    suitable = sum(1 for item in items if item.season.value in compatible_seasons)
    return suitable / len(items)


def outfit_complete(items: List[ClothingItem], occasion: str) -> Tuple[bool, float]:
    """
    Check if outfit is complete for the occasion.
    Returns (is_complete, completeness_score).
    """
    categories = {item.category.value for item in items}
    templates = OUTFIT_TEMPLATES.get(occasion, OUTFIT_TEMPLATES["casual"])

    for template in templates:
        template_cats = {c.value for c in template}
        if template_cats.issubset(categories):
            # Bonus for having shoes/accessories
            extras = categories - template_cats
            bonus = min(0.1 * len(extras), 0.15)
            return True, min(1.0, 0.85 + bonus)

    # Partial completion
    all_needed = set()
    for template in templates:
        all_needed.update(c.value for c in template)

    overlap = categories.intersection(all_needed)
    if not all_needed:
        return True, 1.0

    score = len(overlap) / max(min(len(t) for t in templates), 1)
    return False, round(score * 0.70, 3)


def weather_appropriate(items: List[ClothingItem], temperature: Optional[float]) -> Tuple[float, str]:
    """Check if outfit is appropriate for weather."""
    if temperature is None:
        return 0.85, ""

    has_outerwear = any(item.category == Category.outerwear for item in items)

    if temperature < 10:  # Cold
        if has_outerwear:
            return 1.0, "Layered appropriately for cold weather"
        seasons = [item.season.value for item in items]
        if "winter" in seasons:
            return 0.80, "Warm fabrics for cold weather"
        return 0.50, "Consider adding a coat for cold weather"

    elif temperature > 25:  # Hot
        if has_outerwear:
            return 0.60, "Outerwear may be too warm for hot weather"
        seasons = [item.season.value for item in items]
        if "summer" in seasons:
            return 1.0, "Light and breezy for warm weather"
        return 0.80, "Suitable for warm weather"

    else:  # Moderate
        return 0.90, "Appropriate for mild weather"
