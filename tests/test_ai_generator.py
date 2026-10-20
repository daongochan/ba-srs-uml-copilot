"""Unit tests for AI Generator service."""

import pytest
from unittest.mock import MagicMock, patch
from src.services.ai_generator import generate_srs_from_notes
from src.models.srs_schema import SRSDocument


def test_generate_srs_empty_api_key_raises_error():
    with pytest.raises(ValueError) as exc:
        generate_srs_from_notes("Some notes", "")
    assert "GEMINI_API_KEY không được để trống" in str(exc.value)


def test_generate_srs_empty_notes_raises_error():
    with pytest.raises(ValueError) as exc:
        generate_srs_from_notes("   ", "fake_key")
    assert "Nội dung ghi chú họp khách hàng không được để trống" in str(exc.value)


@patch("src.services.ai_generator.genai.Client")
def test_generate_srs_from_notes_success_mock(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    sample_json = """{
        "project_title": "Test Cinema System",
        "business_objective": "Test Objective",
        "actors": ["Customer", "Admin"],
        "functional_requirements": [
            {
                "req_id": "FR-01",
                "title": "Select Seat",
                "user_story": "As a customer, I want to select a seat...",
                "priority": "High",
                "acceptance_criteria": [
                    {
                        "given": "User is on booking page",
                        "when": "User clicks seat A1",
                        "then": "Seat status changes to locked"
                    }
                ]
            }
        ],
        "non_functional_requirements": [
            {
                "category": "Performance",
                "description": "Fast response time",
                "metric": "Response time < 200ms"
            }
        ],
        "sequence_diagram_mermaid": "sequenceDiagram\\n  autonumber\\n  User->>Server: Lock seat",
        "er_diagram_mermaid": "erDiagram\\n  USER ||--o{ BOOKING : makes",
        "sql_ddl_script": "CREATE TABLE bookings (id SERIAL PRIMARY KEY);"
    }"""

    mock_response = MagicMock()
    mock_response.text = sample_json
    mock_client.models.generate_content.return_value = mock_response

    doc = generate_srs_from_notes("Meeting notes content...", "fake_api_key_123")

    assert isinstance(doc, SRSDocument)
    assert doc.project_title == "Test Cinema System"
    assert len(doc.functional_requirements) == 1
    assert doc.sequence_diagram_mermaid.startswith("sequenceDiagram")
    assert doc.er_diagram_mermaid.startswith("erDiagram")
    assert "CREATE TABLE bookings" in doc.sql_ddl_script
