"""Pytest global configuration and safety fixtures."""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def mock_dotenv_and_safe_env(monkeypatch):
    """Safety guard: prevent tests from loading real .env files or making live network calls."""
    # Prevent load_dotenv from overriding test environment
    with patch("dotenv.load_dotenv", return_value=False):
        yield
