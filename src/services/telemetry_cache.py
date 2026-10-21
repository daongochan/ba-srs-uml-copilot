"""Telemetry, Content-Addressable Caching, and Exponential Backoff Retry for LLMOps."""

from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import random
import re
import time
from typing import Optional, Dict, Tuple, Any, Callable

from src.models.srs_schema import SRSDocument


@dataclass
class TelemetryMetrics:
    """Các chỉ số vận hành và đo lường hiệu năng của LLM (LLMOps Metrics)."""

    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cache_hit: bool
    retry_attempts: int
    content_hash: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# Pre-compiled regex for content hashing
_WHITESPACE_REGEX = re.compile(r"\s+")


def compute_content_hash(raw_text: str, model_name: str = "gemini-3.8-flash") -> str:
    """Chuẩn hóa khoảng trắng và tính toán mã băm SHA-256 (64 ký tự hex) đại diện cho nội dung.

    Đảm bảo 2 văn bản có nội dung ngữ nghĩa giống nhau (chỉ khác khoảng trắng thừa, tab, xuống dòng)
    sẽ sinh ra cùng một mã băm duy nhất (Idempotent Content-Addressable Key).
    """
    normalized_text = _WHITESPACE_REGEX.sub(" ", raw_text or "").strip()
    normalized_model = _WHITESPACE_REGEX.sub(" ", model_name or "").strip().lower()
    payload = f"{normalized_text}::{normalized_model}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class DeterministicSRSCache:
    """Bộ nhớ đệm trong RAM (In-Memory Cache) lưu trữ các tài liệu SRS dựa trên mã băm nội dung SHA-256.

    Tích hợp cơ chế giải phóng bộ nhớ LRU (Least Recently Used) và TTL (Time-To-Live)
    để ngăn ngừa rò rỉ bộ nhớ (Memory Leak) và cung cấp thời gian truy xuất O(1).
    """

    def __init__(self, max_size: int = 128, ttl_seconds: Optional[float] = 3600.0) -> None:
        self.max_size = max(1, max_size)
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Tuple[SRSDocument, TelemetryMetrics, float]] = OrderedDict()

    def get(self, content_hash: str) -> Optional[Tuple[SRSDocument, TelemetryMetrics]]:
        """Truy xuất tài liệu SRS và telemetry từ bộ nhớ đệm kèm kiểm tra TTL và cập nhật vị trí LRU."""
        if content_hash not in self._cache:
            return None

        doc, metrics, created_at = self._cache[content_hash]
        if self.ttl_seconds is not None and (time.time() - created_at) > self.ttl_seconds:
            del self._cache[content_hash]
            return None

        # Cập nhật vị trí LRU (đưa về cuối là mục dùng gần đây nhất)
        self._cache.move_to_end(content_hash)
        return doc.model_copy(deep=True), metrics

    def set(self, content_hash: str, doc: SRSDocument, metrics: TelemetryMetrics) -> None:
        """Lưu trữ tài liệu SRS vào cache, kích hoạt thu hồi LRU nếu vượt ngưỡng max_size."""
        if content_hash in self._cache:
            self._cache.move_to_end(content_hash)
        elif len(self._cache) >= self.max_size:
            # Thu hồi phần tử cũ nhất (đầu danh sách OrderedDict)
            self._cache.popitem(last=False)

        # Lưu bản sao độc lập trong cache để tránh ô nhiễm trạng thái
        self._cache[content_hash] = (doc.model_copy(deep=True), metrics, time.time())

    def clear(self) -> None:
        """Xóa toàn bộ dữ liệu trong bộ nhớ đệm."""
        self._cache.clear()

    def size(self) -> int:
        """Số lượng bản ghi hợp lệ (chưa hết hạn) hiện có trong bộ nhớ đệm."""
        self.prune_expired()
        return len(self._cache)

    def prune_expired(self) -> int:
        """Loại bỏ các bản ghi đã quá thời hạn TTL khỏi bộ nhớ đệm."""
        if self.ttl_seconds is None:
            return 0
        now = time.time()
        expired_keys = [k for k, (_, _, t) in self._cache.items() if (now - t) > self.ttl_seconds]
        for k in expired_keys:
            del self._cache[k]
        return len(expired_keys)


# Global Singleton Cache Instance
default_srs_cache = DeterministicSRSCache()


def execute_with_exponential_backoff(
    func: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> Tuple[Any, int]:
    """Thực thi hàm với cơ chế tự phục hồi Exponential Backoff Retry kèm Jitter khi gặp lỗi mạng/rate-limit.

    Quy tắc xử lý lỗi:
    - Thử lại khi gặp các lỗi tạm thời: HTTP 429 (Rate Limit), 500 (Internal Server Error),
      503 (Service Unavailable), Resource Exhausted, Timeout.
    - Dừng ngay lập tức (Fail-fast) khi gặp lỗi phía client hoặc xác thực: 400 (Bad Request),
      401 (Unauthorized / Invalid API Key), 403 (Forbidden), 404 (Not Found).

    Args:
        func: Hàm cần thực thi (không nhận tham số).
        max_retries: Số lần thử lại tối đa.
        base_delay: Thời gian chờ cơ sở tính bằng giây.

    Returns:
        Tuple[Any, int]: Kết quả của hàm và số lần đã thử lại (retry_attempts).
    """
    attempts = 0
    while True:
        try:
            result = func()
            return result, attempts
        except Exception as e:
            err_str = str(e).upper()

            # Dừng ngay lập tức (Fail-fast) với các lỗi xác thực/cú pháp client
            client_fatal_errors = [
                "400",
                "401",
                "403",
                "404",
                "INVALID_ARGUMENT",
                "UNAUTHENTICATED",
                "PERMISSION_DENIED",
                "NOT_FOUND",
            ]
            if any(err_code in err_str for err_code in client_fatal_errors):
                raise e

            attempts += 1
            if attempts > max_retries:
                raise e

            # Tính toán thời gian chờ theo hàm mũ kèm Jitter ngẫu nhiên để tránh thundering herd
            jitter = random.uniform(0.05, 0.25)
            delay = (base_delay * (2 ** (attempts - 1))) + jitter
            time.sleep(delay)
