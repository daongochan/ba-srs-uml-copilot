"""Unit tests for Performance, Stability, LRU/TTL Cache, and Graceful Degradation (Lô C)."""

import time
from unittest.mock import patch, MagicMock
import pytest

from src.models.srs_schema import SRSDocument
from src.services.telemetry_cache import (
    DeterministicSRSCache,
    TelemetryMetrics,
    execute_with_exponential_backoff,
)
from src.services.ai_generator import generate_srs_with_telemetry
from src.validators.db_sandbox import _sanitize_ddl_for_sqlite, execute_and_audit_ddl
from src.validators.consistency_checker import extract_erd_entities, extract_ddl_tables


def _create_sample_doc(title: str = "Test System") -> SRSDocument:
    return SRSDocument(
        project_title=title,
        business_objective="Objective for performance testing",
        actors=["User"],
        functional_requirements=[],
        non_functional_requirements=[],
        sequence_diagram_mermaid="sequenceDiagram\nUser->>System: Ping",
        state_diagram_mermaid="stateDiagram-v2\n[*] --> Idle",
        state_machine_entity="Entity",
        er_diagram_mermaid="erDiagram\nUSERS {\n  int id PK\n}",
        sql_ddl_script="CREATE TABLE users (id INT PRIMARY KEY);",
        traceability_matrix=[],
        quality_audit=None,
    )


def _create_sample_metrics(content_hash: str = "hash123") -> TelemetryMetrics:
    return TelemetryMetrics(
        latency_ms=50.0,
        prompt_tokens=100,
        completion_tokens=200,
        total_tokens=300,
        cache_hit=False,
        retry_attempts=0,
        content_hash=content_hash,
    )


class TestDeterministicSRSCacheLRUAndTTL:
    """Kiểm thử cơ chế quản lý bộ nhớ đệm: LRU Eviction, TTL Expiration, và Snapshot Isolation."""

    def test_cache_lru_eviction(self):
        cache = DeterministicSRSCache(max_size=3, ttl_seconds=3600.0)
        doc1 = _create_sample_doc("Doc 1")
        doc2 = _create_sample_doc("Doc 2")
        doc3 = _create_sample_doc("Doc 3")
        doc4 = _create_sample_doc("Doc 4")

        cache.set("k1", doc1, _create_sample_metrics("k1"))
        cache.set("k2", doc2, _create_sample_metrics("k2"))
        cache.set("k3", doc3, _create_sample_metrics("k3"))
        assert cache.size() == 3

        # Truy xuất k1 -> k1 được đưa lên vị trí dùng gần đây nhất, k2 trở thành cũ nhất
        res1 = cache.get("k1")
        assert res1 is not None

        # Thêm k4 -> k2 phải bị thu hồi (evicted)
        cache.set("k4", doc4, _create_sample_metrics("k4"))
        assert cache.size() == 3
        assert cache.get("k2") is None
        assert cache.get("k1") is not None
        assert cache.get("k3") is not None
        assert cache.get("k4") is not None

    def test_cache_ttl_expiration(self):
        cache = DeterministicSRSCache(max_size=10, ttl_seconds=0.1)
        doc = _create_sample_doc("Expiring Doc")
        cache.set("temp_key", doc, _create_sample_metrics("temp_key"))

        # Truy xuất ngay lập tức -> còn tồn tại
        assert cache.get("temp_key") is not None

        # Đợi quá hạn TTL 0.1s
        time.sleep(0.15)
        assert cache.get("temp_key") is None
        assert cache.size() == 0

    def test_cache_prune_expired(self):
        cache = DeterministicSRSCache(max_size=10, ttl_seconds=0.1)
        cache.set("k1", _create_sample_doc("D1"), _create_sample_metrics("k1"))
        time.sleep(0.15)
        cache.set("k2", _create_sample_doc("D2"), _create_sample_metrics("k2"))

        # k1 hết hạn nhưng k2 còn hạn
        pruned_count = cache.prune_expired()
        assert pruned_count == 1
        assert cache.get("k1") is None
        assert cache.get("k2") is not None

    def test_cache_snapshot_isolation(self):
        """Đảm bảo việc sửa đổi đối tượng sau khi lấy từ cache không làm ô nhiễm bản sao gốc trong cache."""
        cache = DeterministicSRSCache(max_size=5)
        doc = _create_sample_doc("Original Title")
        cache.set("safe_key", doc, _create_sample_metrics("safe_key"))

        retrieved_1, _ = cache.get("safe_key")
        retrieved_1.project_title = "MUTATED TITLE"

        retrieved_2, _ = cache.get("safe_key")
        assert retrieved_2.project_title == "Original Title"


class TestGracefulDegradationAndRetry:
    """Kiểm thử tính năng phục hồi Exponential Backoff kèm Jitter và xử lý Rate Limit."""

    def test_exponential_backoff_success_with_jitter(self):
        counter = 0

        def flaky_func():
            nonlocal counter
            counter += 1
            if counter < 2:
                raise ConnectionError("503 Service Unavailable")
            return "SUCCESS"

        start_t = time.perf_counter()
        result, retries = execute_with_exponential_backoff(flaky_func, max_retries=3, base_delay=0.05)
        duration = time.perf_counter() - start_t

        assert result == "SUCCESS"
        assert retries == 1
        assert duration >= 0.05

    @patch("src.services.ai_generator.genai.Client")
    def test_ai_generator_rate_limit_friendly_guidance(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception(
            "HTTP 429: Resource has been exhausted (e.g. check quota)."
        )
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError) as exc_info:
            generate_srs_with_telemetry("Valid meeting notes", "AIzaFakeKey123456789012345678901234567", force_refresh=True)

        err_text = str(exc_info.value)
        assert "Gợi ý: Dịch vụ Gemini API đang quá tải hoặc đạt giới hạn hạn ngạch" in err_text


class TestValidatorPerformanceAndCaching:
    """Kiểm thử hiệu năng pre-compiled regex và caching trong validators."""

    def test_sanitize_ddl_for_sqlite_lru_cache(self):
        _sanitize_ddl_for_sqlite.cache_clear()
        sql = "CREATE TABLE users (id SERIAL PRIMARY KEY, created_at TIMESTAMP DEFAULT now());"

        # Lần 1: Cache Miss
        res1 = _sanitize_ddl_for_sqlite(sql)
        info1 = _sanitize_ddl_for_sqlite.cache_info()
        assert info1.misses >= 1

        # Lần 2: Cache Hit
        res2 = _sanitize_ddl_for_sqlite(sql)
        info2 = _sanitize_ddl_for_sqlite.cache_info()
        assert res1 == res2
        assert info2.hits >= 1

    def test_extract_erd_entities_precompiled(self):
        erd = """erDiagram
        CUSTOMERS ||--o{ ORDERS : places
        ORDERS ||--|{ ORDER_ITEMS : contains
        PRODUCTS ||--o{ ORDER_ITEMS : ordered_in
        """
        entities = extract_erd_entities(erd)
        assert entities == {"customers", "orders", "order_items", "products"}

    def test_extract_ddl_tables_precompiled(self):
        sql = """
        CREATE TABLE accounts (id INT PRIMARY KEY);
        CREATE TABLE transactions (id INT PRIMARY KEY, account_id INT);
        """
        tables = extract_ddl_tables(sql)
        assert tables == {"accounts", "transactions"}
