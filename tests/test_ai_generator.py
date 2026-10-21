"""Unit tests for AI Generator service."""

import pytest
from unittest.mock import MagicMock, patch
from src.services.ai_generator import (
    generate_srs_from_notes,
    generate_srs_with_telemetry,
)
from src.services.telemetry_cache import default_srs_cache, TelemetryMetrics
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
    mock_response.usage_metadata = MagicMock(
        prompt_token_count=120,
        candidates_token_count=350,
        total_token_count=470,
    )
    mock_client.models.generate_content.return_value = mock_response

    doc, telemetry = generate_srs_with_telemetry(
        "Unique meeting notes for testing 1...",
        "fake_api_key_123",
        force_refresh=True,
    )

    assert isinstance(doc, SRSDocument)
    assert doc.project_title == "Test Cinema System"
    assert len(doc.functional_requirements) == 1
    assert doc.sequence_diagram_mermaid.startswith("sequenceDiagram")
    assert doc.er_diagram_mermaid.startswith("erDiagram")
    assert "CREATE TABLE bookings" in doc.sql_ddl_script
    assert telemetry.total_tokens == 470
    assert not telemetry.cache_hit


def test_generate_srs_with_telemetry_cache_hit():
    """Verify that when content hash is already cached, no API call is made."""
    doc = SRSDocument(
        project_title="Cached System",
        business_objective="Cached Objective",
        actors=["Actor1"],
        functional_requirements=[],
        non_functional_requirements=[],
        sequence_diagram_mermaid="sequenceDiagram\n  A->>B: hi",
        er_diagram_mermaid="erDiagram\n  A ||--o{ B : rel",
        sql_ddl_script="CREATE TABLE a (id INT PRIMARY KEY);",
    )
    telemetry = TelemetryMetrics(
        latency_ms=10.0,
        prompt_tokens=100,
        completion_tokens=200,
        total_tokens=300,
        cache_hit=False,
        retry_attempts=0,
        content_hash="mock_cached_hash_val",
    )

    from src.services.telemetry_cache import compute_content_hash
    notes = "Notes for testing cache hit behavior..."
    c_hash = compute_content_hash(notes, model_name="gemini-3.8-flash")
    default_srs_cache.set(c_hash, doc, telemetry)

    cached_doc, cached_telemetry = generate_srs_with_telemetry(
        notes,
        "dummy_key",
        force_refresh=False,
        model_name="gemini-3.8-flash",
    )

    assert cached_doc.project_title == "Cached System"
    assert cached_telemetry.cache_hit is True
    assert cached_telemetry.total_tokens == 300


@patch("src.services.ai_generator.genai.Client")
def test_generate_srs_empty_response_text_raises_error(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_response = MagicMock()
    mock_response.text = ""
    mock_client.models.generate_content.return_value = mock_response

    with pytest.raises(ValueError) as exc:
        generate_srs_with_telemetry("Some random notes 2...", "fake_key", force_refresh=True)
    assert "Không nhận được phản hồi hợp lệ" in str(exc.value)


@patch("src.services.ai_generator.genai.Client")
def test_generate_srs_missing_token_metadata_fallback(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    sample_json = """{
        "project_title": "Fallback Token System",
        "business_objective": "Test Objective",
        "actors": [],
        "functional_requirements": [],
        "non_functional_requirements": [],
        "sequence_diagram_mermaid": "sequenceDiagram\\n  A->>B: hi",
        "er_diagram_mermaid": "erDiagram\\n  A ||--o{ B : rel",
        "sql_ddl_script": "CREATE TABLE t (id INT);"
    }"""
    mock_response = MagicMock()
    mock_response.text = sample_json
    mock_response.usage_metadata = None  # Missing token count
    mock_client.models.generate_content.return_value = mock_response

    doc, telemetry = generate_srs_with_telemetry(
        "Notes without token usage...",
        "fake_key",
        force_refresh=True,
    )

    assert doc.project_title == "Fallback Token System"
    assert telemetry.total_tokens > 0
    assert telemetry.prompt_tokens > 0
    assert telemetry.completion_tokens > 0


@patch("src.services.ai_generator.genai.Client")
def test_generate_srs_invalid_mermaid_fallback_resilience(mock_client_class):
    """Verify that if LLM produces invalid mermaid syntax, it is retained rather than crashing."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    sample_json = """{
        "project_title": "Resilient System",
        "business_objective": "Test",
        "actors": [],
        "functional_requirements": [],
        "non_functional_requirements": [],
        "sequence_diagram_mermaid": "invalidDiagramSyntaxWithoutKeyword",
        "er_diagram_mermaid": "invalidErSyntax",
        "state_diagram_mermaid": "invalidStateSyntax",
        "sql_ddl_script": "CREATE TABLE t (id INT);"
    }"""
    mock_response = MagicMock()
    mock_response.text = sample_json
    mock_response.usage_metadata = MagicMock(total_token_count=100)
    mock_client.models.generate_content.return_value = mock_response

    doc, telemetry = generate_srs_with_telemetry(
        "Notes with invalid mermaid...",
        "fake_key",
        force_refresh=True,
    )

    assert doc.project_title == "Resilient System"
    assert doc.sequence_diagram_mermaid == "invalidDiagramSyntaxWithoutKeyword"
