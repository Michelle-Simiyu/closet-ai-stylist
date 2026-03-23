"""
Color analysis and harmony rules for outfit compatibility.
"""
from typing import Dict, List, Tuple, Optional
import colorsys


# Color groups for harmony analysis
COLOR_GROUPS: Dict[str, List[str]] = {
    "neutral": ["white", "black", "gray", "grey", "beige", "cream", "ivory", "nude", "tan", "khaki"],
    "warm": ["red", "orange", "yellow", "coral", "salmon", "rust", "burgundy", "maroon", "gold", "amber"],
    "cool": ["blue", "purple", "violet", "indigo", "teal", "navy", "cobalt", "lavender", "lilac"],
    "green": ["green", "olive", "sage", "forest", "mint", "emerald", "lime"],
    "pink": ["pink", "blush", "rose", "fuchsia", "magenta", "hot pink"],
    "brown": ["brown", "camel", "chocolate", "coffee", "mocha", "walnut"],
}

# Named color to approximate RGB
COLOR_TO_RGB: Dict[str, Tuple[int, int, int]] = {
    "white": (255, 255, 255),
    "black": (10, 10, 10),
    "gray": (128, 128, 128),
    "grey": (128, 128, 128),
    "beige": (245, 245, 220),
    "cream": (255, 253, 208),
    "ivory": (255, 255, 240),
    "nude": (242, 203, 176),
    "tan": (210, 180, 140),
    "khaki": (195, 176, 145),
    "red": (220, 20, 60),
    "orange": (255, 140, 0),
    "yellow": (255, 215, 0),
    "coral": (255, 127, 80),
    "salmon": (250, 128, 114),
    "rust": (183, 65, 14),
    "burgundy": (128, 0, 32),
    "maroon": (128, 0, 0),
    "gold": (255, 215, 0),
    "blue": (70, 130, 180),
    "navy": (0, 0, 128),
    "cobalt": (0, 71, 171),
    "teal": (0, 128, 128),
    "purple": (128, 0, 128),
    "violet": (138, 43, 226),
    "lavender": (230, 230, 250),
    "indigo": (75, 0, 130),
    "green": (0, 128, 0),
    "olive": (128, 128, 0),
    "sage": (143, 151, 121),
    "forest": (34, 85, 34),
    "mint": (189, 252, 201),
    "emerald": (0, 201, 87),
    "pink": (255, 192, 203),
    "blush": (255, 229, 225),
    "rose": (255, 0, 127),
    "fuchsia": (255, 0, 255),
    "brown": (139, 69, 19),
    "camel": (193, 154, 107),
    "chocolate": (210, 105, 30),
    "white": (255, 255, 255),
    "silver": (192, 192, 192),
    "denim": (21, 96, 189),
    "charcoal": (54, 69, 79),
}

# Complementary color pairs (high harmony)
COMPLEMENTARY_PAIRS = [
    ("red", "green"),
    ("blue", "orange"),
    ("yellow", "purple"),
    ("teal", "coral"),
    ("navy", "gold"),
    ("burgundy", "sage"),
    ("forest", "blush"),
]

# Analogous groups (similar hues - also harmonious)
ANALOGOUS_GROUPS = [
    ["red", "orange", "coral", "salmon"],
    ["blue", "teal", "navy", "cobalt"],
    ["purple", "violet", "lavender", "indigo"],
    ["green", "olive", "sage", "forest"],
    ["yellow", "gold", "orange"],
]

# Classic always-works combinations
CLASSIC_COMBOS = [
    ("navy", "white"),
    ("black", "white"),
    ("gray", "white"),
    ("black", "gray"),
    ("navy", "gray"),
    ("camel", "white"),
    ("beige", "white"),
    ("navy", "beige"),
    ("black", "beige"),
]


def get_color_group(color: str) -> str:
    """Return the group a color belongs to."""
    color_lower = color.lower()
    for group, colors in COLOR_GROUPS.items():
        if any(c in color_lower for c in colors):
            return group
    return "other"


def is_neutral(color: str) -> bool:
    """Check if a color is neutral."""
    return get_color_group(color) == "neutral"


def color_harmony_score(color1: str, color2: str) -> float:
    """
    Calculate harmony score between two colors.
    Returns 0.0 to 1.0.
    """
    c1 = color1.lower()
    c2 = color2.lower()

    # Same color: moderate score (monochrome works but can be boring)
    if c1 == c2:
        return 0.75

    # At least one neutral: always good
    if is_neutral(c1) or is_neutral(c2):
        return 0.90

    # Both neutrals: excellent
    if is_neutral(c1) and is_neutral(c2):
        return 0.95

    # Check classic combos
    for a, b in CLASSIC_COMBOS:
        if (c1 == a and c2 == b) or (c1 == b and c2 == a):
            return 0.95

    # Check complementary
    for a, b in COMPLEMENTARY_PAIRS:
        if (a in c1 and b in c2) or (b in c1 and a in c2):
            return 0.85

    # Check analogous
    for group in ANALOGOUS_GROUPS:
        if any(g in c1 for g in group) and any(g in c2 for g in group):
            return 0.80

    # Same color group
    g1 = get_color_group(c1)
    g2 = get_color_group(c2)
    if g1 == g2 and g1 != "other":
        return 0.70

    # Warm + cool: generally avoid
    if (g1 == "warm" and g2 == "cool") or (g1 == "cool" and g2 == "warm"):
        return 0.50

    return 0.60


def outfit_color_harmony(colors: List[str]) -> Tuple[float, List[str]]:
    """
    Calculate color harmony for an entire outfit.
    Returns (score, feedback_messages).
    """
    if not colors:
        return 0.5, []

    feedback = []
    neutral_count = sum(1 for c in colors if is_neutral(c))
    non_neutral = [c for c in colors if not is_neutral(c)]

    # All neutrals is safe and elegant
    if neutral_count == len(colors):
        feedback.append("Classic neutral palette — effortlessly elegant")
        return 0.92, feedback

    # 1 accent + neutrals: great
    if len(non_neutral) == 1 and neutral_count >= 1:
        feedback.append(f"Perfect neutral base with {non_neutral[0]} accent")
        return 0.90, feedback

    # 2 non-neutrals: check harmony
    scores = []
    if len(colors) > 1:
        for i in range(len(colors)):
            for j in range(i + 1, len(colors)):
                scores.append(color_harmony_score(colors[i], colors[j]))

    if not scores:
        return 0.70, feedback

    avg_score = sum(scores) / len(scores)

    if avg_score >= 0.85:
        feedback.append("Excellent color combination")
    elif avg_score >= 0.75:
        feedback.append("Good color harmony")
    elif avg_score >= 0.60:
        feedback.append("Colors work together adequately")
    else:
        feedback.append("Color combination could be improved")

    if len(non_neutral) > 3:
        feedback.append("Consider reducing to 2-3 colors for a cleaner look")
        avg_score *= 0.85

    return round(avg_score, 3), feedback


def suggest_color_improvements(colors: List[str]) -> List[str]:
    """Suggest improvements for a color palette."""
    suggestions = []
    non_neutral = [c for c in colors if not is_neutral(c)]

    if len(non_neutral) > 2:
        suggestions.append("Reduce to 1-2 accent colors for better harmony")

    if not any(is_neutral(c) for c in colors):
        suggestions.append("Add a neutral piece (white, black, gray, beige) as an anchor")

    return suggestions
