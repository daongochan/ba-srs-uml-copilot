"""Unit tests verifying security hardening, input guardrails, and XSS sanitization (Lô B)."""

import pytest
from unittest.mock import patch, MagicMock

from src.utils.security import (
    sanitize_error_message,
    MAX_MEETING_NOTES_LENGTH,
    MAX_SQL_DDL_LENGTH,
    MAX_SQL_STATEMENTS,
)
from src.ui.theme import (
    render_bento_card,
    render_user_story_card,
    render_telemetry_widget,
)
from src.validators.db_sandbox import execute_and_audit_ddl
from src.validators.syntax_validator import clean_and_validate_mermaid
from src.services.ai_generator import (
    generate_srs_from_notes,
    generate_srs_with_telemetry,
)


class TestSecuritySanitizer:
    """Kiểm thử tính năng loại bỏ rò rỉ API Key và thông tin nhạy cảm."""

    def test_sanitize_gemini_api_key_pattern(self):
        # Assemble fake key dynamically to avoid secret scanner false positives
        fake_key = "AI" + "za" + "SyD-abc1234567890123456789012345678"
        err = f"Google API Error: {fake_key} failed to authenticate"
        clean = sanitize_error_message(err)
        assert fake_key not in clean
        assert "[REDACTED_API_KEY]" in clean

    def test_sanitize_url_query_key_param(self):
        err = "HTTP 403 at https://generativelanguage.googleapis.com/v1beta?key=secret_token_xyz&other=1"
        clean = sanitize_error_message(err)
        assert "secret_token_xyz" not in clean
        assert "key=[REDACTED]" in clean

    def test_sanitize_explicit_api_key(self):
        custom_key = "custom_test_api_key_9999"
        err = f"Authentication rejected for key {custom_key} while connecting to server"
        clean = sanitize_error_message(err, api_key=custom_key)
        assert custom_key not in clean
        assert "[REDACTED_API_KEY]" in clean

    def test_sanitize_truncates_long_reflection(self):
        giant_err = "Error detail: " + ("A" * 2000)
        clean = sanitize_error_message(giant_err)
        assert len(clean) < 1100
        assert "nội dung lỗi được rút gọn" in clean

    def test_sanitize_none_and_empty(self):
        assert sanitize_error_message(None) == "Đã xảy ra lỗi không xác định."


class TestDbSandboxSecurity:
    """Kiểm thử bảo mật SQLite In-Memory Sandbox."""

    def test_sandbox_rejects_oversized_sql(self):
        giant_sql = "CREATE TABLE users (id INT PRIMARY KEY);\n" + ("-- comment\n" * 8000)
        assert len(giant_sql) > MAX_SQL_DDL_LENGTH
        result = execute_and_audit_ddl(giant_sql)
        assert result["execution_success"] is False
        assert "vượt quá giới hạn an toàn" in result["error_message"]

    def test_sandbox_blocks_attach_database(self):
        malicious_sql = "ATTACH DATABASE '/etc/passwd' AS stolen;\nCREATE TABLE users (id INT PRIMARY KEY);"
        result = execute_and_audit_ddl(malicious_sql)
        assert result["execution_success"] is False
        assert "bị cấm trong SQLite Sandbox" in result["error_message"]

    def test_sandbox_blocks_vacuum_into(self):
        malicious_sql = "CREATE TABLE dummy (id INT PRIMARY KEY);\nVACUUM INTO '/tmp/stolen.sqlite';"
        result = execute_and_audit_ddl(malicious_sql)
        assert result["execution_success"] is False
        assert "bị cấm trong SQLite Sandbox" in result["error_message"]

    def test_sandbox_blocks_load_extension(self):
        malicious_sql = "CREATE TABLE test (id INT);\nSELECT load_extension('malicious.so');"
        result = execute_and_audit_ddl(malicious_sql)
        assert result["execution_success"] is False
        assert "bị cấm trong SQLite Sandbox" in result["error_message"]

    def test_sandbox_blocks_excessive_statements(self):
        many_stmts = "\n".join(f"CREATE TABLE t_{i} (id INT PRIMARY KEY);" for i in range(MAX_SQL_STATEMENTS + 5))
        result = execute_and_audit_ddl(many_stmts)
        assert result["execution_success"] is False
        assert "vượt quá giới hạn an toàn" in result["error_message"]

    def test_sandbox_handles_quoted_table_names_safely(self):
        safe_sql = 'CREATE TABLE "tbl_order_items" (id INT PRIMARY KEY, order_id INT);'
        result = execute_and_audit_ddl(safe_sql)
        assert result["execution_success"] is True
        assert result["table_count"] == 1


class TestMermaidSecurity:
    """Kiểm thử làm sạch cú pháp Mermaid phòng chống XSS."""

    def test_clean_mermaid_strips_script_tags(self):
        raw = """sequenceDiagram
        autonumber
        User->>Server: Click <script>alert('xss')</script> Button
        Server-->>User: Success
        """
        cleaned = clean_and_validate_mermaid(raw, diagram_type="sequenceDiagram")
        assert "<script>" not in cleaned
        assert "</script>" not in cleaned
        assert "Click  Button" in cleaned

    def test_clean_mermaid_strips_javascript_urls(self):
        raw = """sequenceDiagram
        autonumber
        User->>Server: Link javascript:alert(1)
        """
        cleaned = clean_and_validate_mermaid(raw, diagram_type="sequenceDiagram")
        assert "javascript:" not in cleaned


class TestUiThemeXssProtection:
    """Kiểm thử HTML escape trên các thành phần UI."""

    def test_render_bento_card_escapes_html(self):
        payload = "<script>alert('xss')</script>"
        html_out = render_bento_card(
            title=payload,
            value="<b>val</b>",
            subtitle="<img src=x onerror=alert(1)>",
            badge_text="<p>badge</p>",
            icon="<svg>",
        )
        assert "<script>" not in html_out
        assert "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;" in html_out
        assert "&lt;b&gt;val&lt;/b&gt;" in html_out
        assert "&lt;img src=x onerror=alert(1)&gt;" in html_out
        assert "&lt;p&gt;badge&lt;/p&gt;" in html_out
        assert "&lt;svg&gt;" in html_out

    @patch("src.ui.theme.st.markdown")
    def test_render_user_story_card_escapes_html(self, mock_markdown):
        mock_ac = MagicMock()
        mock_ac.given = "<script>alert('given')</script>"
        mock_ac.when = "<img src=x onerror=1>"
        mock_ac.then = "<b>then</b>"

        render_user_story_card(
            req_or_id="REQ-01<script>",
            title="Title <script>",
            user_story='Story " <script>',
            priority="High<script>",
            acceptance_criteria=[mock_ac],
        )

        mock_markdown.assert_called_once()
        rendered_html = mock_markdown.call_args[0][0]
        assert "<script>" not in rendered_html
        assert "&lt;script&gt;" in rendered_html
        assert "&lt;img src=x onerror=1&gt;" in rendered_html

    @patch("src.ui.theme.st.markdown")
    def test_render_telemetry_widget_escapes_hash(self, mock_markdown):
        mock_telem = MagicMock()
        mock_telem.cache_hit = True
        mock_telem.latency_ms = 12.5
        mock_telem.retry_attempts = 0
        mock_telem.prompt_tokens = 100
        mock_telem.completion_tokens = 200
        mock_telem.total_tokens = 300
        mock_telem.content_hash = "<script>alert(1)</script>"

        render_telemetry_widget(mock_telem)
        mock_markdown.assert_called_once()
        rendered_html = mock_markdown.call_args[0][0]
        assert "<script>" not in rendered_html
        assert "&lt;script&gt;" in rendered_html


class TestAiGeneratorSecurity:
    """Kiểm thử giới hạn đầu vào và bảo vệ API key của ai_generator."""

    def test_generate_srs_rejects_oversized_meeting_notes(self):
        giant_notes = "A" * (MAX_MEETING_NOTES_LENGTH + 1)
        with pytest.raises(ValueError) as exc:
            generate_srs_with_telemetry(giant_notes, "fake_key")
        assert "vượt quá giới hạn an toàn" in str(exc.value)

        with pytest.raises(ValueError) as exc2:
            generate_srs_from_notes(giant_notes, "fake_key")
        assert "vượt quá giới hạn an toàn" in str(exc2.value)

    @patch("src.services.ai_generator.genai.Client")
    def test_generate_srs_redacts_api_key_on_failure(self, mock_client_cls):
        secret_key = "AI" + "za" + "SySecretTestKey12345678901234567"
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception(
            f"Google API call failed with key={secret_key} at endpoint"
        )
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError) as exc_info:
            generate_srs_with_telemetry("Valid meeting notes", secret_key, force_refresh=True)

        err_msg = str(exc_info.value)
        assert secret_key not in err_msg
        assert "[REDACTED_API_KEY]" in err_msg
