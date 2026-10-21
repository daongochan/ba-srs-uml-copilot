"""Design Tokens for BA & System Architect Copilot.

Single Source of Truth for colors, typography, spacing scale, border radii,
and component variables under Direction 3: Editorial Craft (Tài Liệu Biên Tập).
"""

from typing import Dict, Final

# ==============================================================================
# 1. COLOR PALETTE: EDITORIAL CRAFT (Deep Teal & Warm Paper)
# ==============================================================================

# Primary Brand Accent (Deep Teal)
TEAL_50: Final[str] = "#F0FDFA"
TEAL_100: Final[str] = "#CCFBF1"
TEAL_200: Final[str] = "#99F6E4"
TEAL_300: Final[str] = "#5EEAD4"
TEAL_400: Final[str] = "#2DD4BF"
TEAL_500: Final[str] = "#14B8A6"
TEAL_600: Final[str] = "#0D9488"  # Core Brand Primary Accent
TEAL_700: Final[str] = "#0F766E"  # Active / Hover Accent
TEAL_800: Final[str] = "#115E59"  # Deep Text on Light Teal
TEAL_900: Final[str] = "#134E4A"

# Warm Neutral Scale (Stone / Warm Paper)
STONE_50: Final[str] = "#FAFAF9"   # Page Background (Warm Paper)
STONE_100: Final[str] = "#F5F5F4"  # Secondary Background / Card Base
STONE_200: Final[str] = "#E7E5E4"  # Subtle Border
STONE_300: Final[str] = "#D6D3D1"  # Active Border / Divider
STONE_400: Final[str] = "#A8A29E"  # Placeholder / Muted Icon
STONE_500: Final[str] = "#78716C"  # Muted Text / Captions
STONE_600: Final[str] = "#57534E"  # Secondary Text
STONE_700: Final[str] = "#44403C"  # Dark Neutral
STONE_800: Final[str] = "#292524"  # Deep Charcoal
STONE_900: Final[str] = "#1C1917"  # Primary Text (High Contrast)
WHITE: Final[str] = "#FFFFFF"

# Semantic Status Colors (WCAG AAA compliant pairings)
# Success (Forest Green)
SUCCESS_BG: Final[str] = "#F0FDF4"
SUCCESS_BORDER: Final[str] = "#BBF7D0"
SUCCESS_TEXT: Final[str] = "#15803D"

# Warning (Ochre Amber)
WARNING_BG: Final[str] = "#FFFBEB"
WARNING_BORDER: Final[str] = "#FDE68A"
WARNING_TEXT: Final[str] = "#B45309"

# Danger / Error (Crimson)
DANGER_BG: Final[str] = "#FEF2F2"
DANGER_BORDER: Final[str] = "#FECACA"
DANGER_TEXT: Final[str] = "#B91C1C"

# Info (Teal Tint)
INFO_BG: Final[str] = "#F0FDFA"
INFO_BORDER: Final[str] = "#99F6E4"
INFO_TEXT: Final[str] = "#0F766E"

# Quick semantic lookup
SEMANTIC_COLORS: Final[Dict[str, Dict[str, str]]] = {
    "success": {"bg": SUCCESS_BG, "border": SUCCESS_BORDER, "text": SUCCESS_TEXT},
    "warning": {"bg": WARNING_BG, "border": WARNING_BORDER, "text": WARNING_TEXT},
    "danger": {"bg": DANGER_BG, "border": DANGER_BORDER, "text": DANGER_TEXT},
    "error": {"bg": DANGER_BG, "border": DANGER_BORDER, "text": DANGER_TEXT},
    "info": {"bg": INFO_BG, "border": INFO_BORDER, "text": INFO_TEXT},
    "primary": {"bg": TEAL_50, "border": TEAL_200, "text": TEAL_700},
}

# ==============================================================================
# 2. TYPOGRAPHY (Be Vietnam Pro & JetBrains Mono)
# ==============================================================================
FONT_PRIMARY: Final[str] = "'Be Vietnam Pro', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
FONT_MONO: Final[str] = "'JetBrains Mono', 'Fira Code', 'SFMono-Regular', Consolas, monospace"

# Typography Scale
FONT_SIZE_XS: Final[str] = "11px"
FONT_SIZE_SM: Final[str] = "12.5px"
FONT_SIZE_BASE: Final[str] = "14px"
FONT_SIZE_MD: Final[str] = "16px"
FONT_SIZE_LG: Final[str] = "18px"
FONT_SIZE_XL: Final[str] = "22px"
FONT_SIZE_2XL: Final[str] = "28px"

# ==============================================================================
# 3. SPACING SCALE (4 / 8 / 16 / 24 / 32)
# ==============================================================================
SPACE_XS: Final[str] = "4px"
SPACE_SM: Final[str] = "8px"
SPACE_MD: Final[str] = "16px"
SPACE_LG: Final[str] = "24px"
SPACE_XL: Final[str] = "32px"

# ==============================================================================
# 4. BORDER RADII (Editorial subtle curves)
# ==============================================================================
RADIUS_SM: Final[str] = "4px"
RADIUS_MD: Final[str] = "6px"
RADIUS_LG: Final[str] = "8px"
RADIUS_PILL: Final[str] = "9999px"

# ==============================================================================
# 5. SHADOWS & ELEVATIONS
# ==============================================================================
SHADOW_SUBTLE: Final[str] = "0 1px 2px 0 rgba(28, 25, 23, 0.04)"
SHADOW_CARD: Final[str] = "0 1px 3px 0 rgba(28, 25, 23, 0.05), 0 1px 2px -1px rgba(28, 25, 23, 0.03)"
SHADOW_HOVER: Final[str] = "0 4px 6px -1px rgba(28, 25, 23, 0.06), 0 2px 4px -2px rgba(28, 25, 23, 0.04)"

# ==============================================================================
# 6. MERMAID DIAGRAM THEME
# ==============================================================================
MERMAID_THEME_VARIABLES: Final[Dict[str, str]] = {
    "darkMode": "false",
    "background": "#FAFAF9",
    "primaryColor": "#F0FDFA",
    "primaryTextColor": "#134E4A",
    "primaryBorderColor": "#0D9488",
    "lineColor": "#57534E",
    "secondaryColor": "#F5F5F4",
    "tertiaryColor": "#FFFFFF",
    "fontFamily": "Be Vietnam Pro, sans-serif",
    "fontSize": "13px",
}
