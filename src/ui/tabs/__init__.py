"""UI Tabs package for BA & System Architect Copilot."""

from src.ui.tabs.tab_srs import render_tab_srs_requirements
from src.ui.tabs.tab_dynamic_models import render_tab_dynamic_models
from src.ui.tabs.tab_database import render_tab_database_design
from src.ui.tabs.tab_export import render_tab_export_bundle

__all__ = [
    "render_tab_srs_requirements",
    "render_tab_dynamic_models",
    "render_tab_database_design",
    "render_tab_export_bundle",
]
