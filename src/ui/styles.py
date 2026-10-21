"""Centralized CSS styles injection for BA & System Architect Copilot.

Direction 3: Editorial Craft (Tài Liệu Biên Tập - GitBook / Craft).
Uses tokens from src.ui.tokens.
"""

from typing import Final
import streamlit as st
from src.ui.tokens import (
    TEAL_50,
    TEAL_100,
    TEAL_200,
    TEAL_500,
    TEAL_600,
    TEAL_700,
    TEAL_800,
    TEAL_900,
    STONE_50,
    STONE_100,
    STONE_200,
    STONE_300,
    STONE_400,
    STONE_500,
    STONE_600,
    STONE_700,
    STONE_800,
    STONE_900,
    WHITE,
    SUCCESS_BG,
    SUCCESS_BORDER,
    SUCCESS_TEXT,
    WARNING_BG,
    WARNING_BORDER,
    WARNING_TEXT,
    DANGER_BG,
    DANGER_BORDER,
    DANGER_TEXT,
    FONT_PRIMARY,
    FONT_MONO,
    SPACE_XS,
    SPACE_SM,
    SPACE_MD,
    SPACE_LG,
    SPACE_XL,
    RADIUS_SM,
    RADIUS_MD,
    RADIUS_LG,
    RADIUS_PILL,
    SHADOW_CARD,
    SHADOW_SUBTLE,
)

EDITORIAL_CSS: Final[str] = f"""
<style>
/* 1. Google Fonts Import: Be Vietnam Pro, JetBrains Mono & Material Symbols */
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

:root {{
    --font-sans: {FONT_PRIMARY};
    --font-mono: {FONT_MONO};
    
    --color-teal-50: {TEAL_50};
    --color-teal-100: {TEAL_100};
    --color-teal-200: {TEAL_200};
    --color-teal-600: {TEAL_600};
    --color-teal-700: {TEAL_700};
    --color-teal-800: {TEAL_800};
    --color-teal-900: {TEAL_900};
    
    --color-stone-50: {STONE_50};
    --color-stone-100: {STONE_100};
    --color-stone-200: {STONE_200};
    --color-stone-300: {STONE_300};
    --color-stone-400: {STONE_400};
    --color-stone-500: {STONE_500};
    --color-stone-600: {STONE_600};
    --color-stone-700: {STONE_700};
    --color-stone-800: {STONE_800};
    --color-stone-900: {STONE_900};
    --color-white: {WHITE};
    
    --color-success-bg: {SUCCESS_BG};
    --color-success-border: {SUCCESS_BORDER};
    --color-success-text: {SUCCESS_TEXT};
    
    --color-warning-bg: {WARNING_BG};
    --color-warning-border: {WARNING_BORDER};
    --color-warning-text: {WARNING_TEXT};
    
    --color-danger-bg: {DANGER_BG};
    --color-danger-border: {DANGER_BORDER};
    --color-danger-text: {DANGER_TEXT};
}}

/* 2. Global Document & Typography Resets */
html, body, p, h1, h2, h3, h4, h5, h6, input, textarea, select, label {{
    font-family: var(--font-sans) !important;
    color: var(--color-stone-900);
}}

/* Explicitly preserve and style icon fonts for Streamlit expanders and buttons */
[data-testid*="Icon"], [data-testid*="icon"], [class*="e1vmumty0"], [class*="e1fmktau2"], [class*="material-symbols"], span[class*="material"], [data-testid="stIcon"], i[class*="material"], [data-testid="stExpanderToggleIcon"] {{
    font-family: 'Material Symbols Rounded' !important;
    font-weight: normal !important;
    font-style: normal !important;
    font-size: 20px !important;
    line-height: 1 !important;
    display: inline-block !important;
    text-transform: none !important;
    letter-spacing: normal !important;
    word-wrap: normal !important;
    white-space: nowrap !important;
    direction: ltr !important;
    -webkit-font-smoothing: antialiased !important;
    text-rendering: optimizeLegibility !important;
    font-feature-settings: 'liga' !important;
}}

/* Main container surface background */
.stApp {{
    background-color: var(--color-stone-50) !important;
}}

/* Sidebar background styling */
[data-testid="stSidebar"] {{
    background-color: var(--color-stone-100) !important;
    border-right: 1px solid var(--color-stone-200) !important;
}}

/* 3. Streamlit Primary Buttons (Teal Editorial) */
[data-testid="stBaseButton-primary"], button[kind="primary"] {{
    background-color: var(--color-teal-600) !important;
    color: #ffffff !important;
    border: 1px solid var(--color-teal-700) !important;
    border-radius: {RADIUS_MD} !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 8px 18px !important;
    box-shadow: {SHADOW_SUBTLE} !important;
    transition: all 0.15s ease-in-out !important;
}}
[data-testid="stBaseButton-primary"]:hover, button[kind="primary"]:hover {{
    background-color: var(--color-teal-700) !important;
    border-color: var(--color-teal-800) !important;
    box-shadow: 0 2px 4px rgba(13, 148, 136, 0.25) !important;
}}
[data-testid="stBaseButton-primary"] *, button[kind="primary"] * {{
    color: #ffffff !important;
}}

/* Secondary / Standard Buttons */
[data-testid="stBaseButton-secondary"], button[kind="secondary"] {{
    background-color: var(--color-white) !important;
    color: var(--color-stone-800) !important;
    border: 1px solid var(--color-stone-300) !important;
    border-radius: {RADIUS_MD} !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    box-shadow: {SHADOW_SUBTLE} !important;
    transition: all 0.15s ease-in-out !important;
}}
[data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover {{
    background-color: var(--color-teal-50) !important;
    color: var(--color-teal-800) !important;
    border-color: var(--color-teal-600) !important;
}}
[data-testid="stBaseButton-secondary"] *, button[kind="secondary"] * {{
    color: var(--color-stone-800) !important;
}}
[data-testid="stBaseButton-secondary"]:hover *, button[kind="secondary"]:hover * {{
    color: var(--color-teal-800) !important;
}}

/* 4. Streamlit Tabs Styling (Clean, No Pagination Wrap, High Contrast) */
div[data-testid="stTabs"] [role="tablist"] {{
    gap: 8px !important;
    border-bottom: 2px solid var(--color-stone-200) !important;
    padding-bottom: 2px !important;
}}

div[data-testid="stTabs"] [role="tab"] {{
    font-family: var(--font-sans) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: var(--color-stone-600) !important;
    padding: 8px 16px !important;
    border-radius: {RADIUS_MD} {RADIUS_MD} 0 0 !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    transition: all 0.15s ease-in-out !important;
}}

div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    color: var(--color-teal-800) !important;
    font-weight: 700 !important;
    background-color: var(--color-white) !important;
    border-color: var(--color-stone-200) var(--color-stone-200) transparent !important;
    border-top: 3px solid var(--color-teal-600) !important;
}}

div[data-testid="stTabs"] [role="tab"]:hover:not([aria-selected="true"]) {{
    color: var(--color-stone-900) !important;
    background-color: var(--color-stone-100) !important;
}}

/* 5. Custom Semantic Editorial Classes */

/* Editorial Hero Banner */
.editorial-banner {{
    background: linear-gradient(135deg, #134e4a 0%, #0f766e 100%);
    border-radius: {RADIUS_LG};
    padding: 20px 24px;
    color: #ffffff;
    box-shadow: {SHADOW_CARD};
    margin-bottom: 20px;
}}
.editorial-banner h1 {{
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 6px 0;
    letter-spacing: -0.01em;
}}
.editorial-banner p {{
    font-size: 13.5px;
    color: #ccfbf1;
    margin: 0;
    line-height: 1.5;
}}

/* Stepper Bar */
.editorial-stepper {{
    display: flex;
    align-items: center;
    background: var(--color-white);
    border: 1px solid var(--color-stone-200);
    border-radius: {RADIUS_MD};
    padding: 10px 16px;
    margin-bottom: 20px;
    gap: 8px;
    overflow-x: auto;
}}
.stepper-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: var(--color-stone-500);
    white-space: nowrap;
}}
.stepper-item.active {{
    color: var(--color-teal-800);
    font-weight: 700;
}}
.stepper-num {{
    width: 22px;
    height: 22px;
    border-radius: {RADIUS_PILL};
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    background: var(--color-stone-100);
    color: var(--color-stone-600);
}}
.stepper-item.active .stepper-num {{
    background: var(--color-teal-600);
    color: #ffffff;
}}
.stepper-sep {{
    color: var(--color-stone-300);
    font-size: 14px;
    margin: 0 4px;
}}

/* 1-Click Scenario Chips */
.editorial-chips-container {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 16px;
}}
.editorial-chip {{
    background: var(--color-white);
    border: 1px solid var(--color-stone-200);
    border-left: 3px solid var(--color-stone-400);
    border-radius: {RADIUS_MD};
    padding: 10px 12px;
    cursor: pointer;
    transition: all 0.15s ease;
    text-align: left;
}}
.editorial-chip:hover {{
    border-color: var(--color-teal-500);
    border-left: 3px solid var(--color-teal-600);
    background: var(--color-teal-50);
}}
.editorial-chip.active {{
    border-color: var(--color-teal-600);
    border-left: 4px solid var(--color-teal-600);
    background: var(--color-teal-50);
}}
.editorial-chip-title {{
    font-size: 13px;
    font-weight: 600;
    color: var(--color-stone-900);
    margin-bottom: 2px;
}}
.editorial-chip.active .editorial-chip-title {{
    color: var(--color-teal-900);
}}
.editorial-chip-desc {{
    font-size: 11px;
    color: var(--color-stone-500);
}}

/* Editorial KPI Grid */
.editorial-kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}}
.editorial-kpi-card {{
    background: var(--color-white);
    border: 1px solid var(--color-stone-200);
    border-left: 3px solid var(--color-teal-600);
    border-radius: {RADIUS_MD};
    padding: 12px 14px;
    box-shadow: {SHADOW_SUBTLE};
}}
.editorial-kpi-title {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--color-stone-500);
    margin-bottom: 4px;
}}
.editorial-kpi-val {{
    font-size: 22px;
    font-weight: 700;
    color: var(--color-teal-900);
    line-height: 1.1;
    margin-bottom: 4px;
}}
.editorial-kpi-subtitle {{
    font-size: 11.5px;
    color: var(--color-stone-600);
}}

/* Editorial Document Article Card (User Story) */
.editorial-card {{
    background: var(--color-white);
    border: 1px solid var(--color-stone-200);
    border-left: 3px solid var(--color-teal-600);
    border-radius: {RADIUS_MD};
    padding: 16px 18px;
    margin-bottom: 14px;
    box-shadow: {SHADOW_SUBTLE};
}}
.editorial-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--color-stone-100);
}}
.editorial-card-id {{
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 700;
    color: var(--color-teal-800);
    background: var(--color-teal-50);
    padding: 2px 8px;
    border-radius: {RADIUS_SM};
    border: 1px solid var(--color-teal-200);
}}
.editorial-card-title {{
    font-size: 15px;
    font-weight: 700;
    color: var(--color-stone-900);
}}

/* Status Badge */
.editorial-badge {{
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: {RADIUS_SM};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
.badge-must-have {{
    background: var(--color-danger-bg);
    color: var(--color-danger-text);
    border: 1px solid var(--color-danger-border);
}}
.badge-should-have {{
    background: var(--color-warning-bg);
    color: var(--color-warning-text);
    border: 1px solid var(--color-warning-border);
}}
.badge-could-have {{
    background: var(--color-stone-100);
    color: var(--color-stone-700);
    border: 1px solid var(--color-stone-200);
}}

/* Given-When-Then BDD Block */
.editorial-bdd-block {{
    background: var(--color-stone-50);
    border: 1px solid var(--color-stone-200);
    border-radius: {RADIUS_SM};
    padding: 10px 14px;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 8px;
}}
.bdd-kw {{
    font-weight: 700;
    color: var(--color-teal-800);
}}

/* Responsive rules for mobile screens <= 768px and 400px */
@media (max-width: 768px) {{
    .editorial-kpi-grid {{
        grid-template-columns: repeat(2, 1fr) !important;
    }}
    .editorial-chips-container {{
        grid-template-columns: 1fr !important;
    }}
}}
@media (max-width: 400px) {{
    .editorial-kpi-grid {{
        grid-template-columns: 1fr !important;
    }}
    .editorial-banner h1 {{
        font-size: 20px !important;
    }}
}}
</style>
"""


def apply_editorial_styles() -> None:
    """Inject centralized Editorial CSS styles into the current Streamlit app."""
    # Using st.markdown with unsafe_allow_html=True
    st.markdown(EDITORIAL_CSS, unsafe_allow_html=True)
