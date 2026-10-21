"""Telemetry, Content-Addressable Caching, and Exponential Backoff Retry for LLMOps."""

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
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


def compute_content_hash(raw_text: str, model_name: str = "gemini-3.8-flash") -> str:
    """Chuẩn hóa khoảng trắng và tính toán mã băm SHA-256 (64 ký tự hex) đại diện cho nội dung.
    
    Đảm bảo 2 văn bản có nội dung ngữ nghĩa giống nhau (chỉ khác khoảng trắng thừa, tab, xuống dòng)
    sẽ sinh ra cùng một mã băm duy nhất (Idempotent Content-Addressable Key).
    """
    normalized_text = re.sub(r"\s+", " ", raw_text or "").strip()
    normalized_model = re.sub(r"\s+", " ", model_name or "").strip().lower()
    payload = f"{normalized_text}::{normalized_model}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class DeterministicSRSCache:
    """Bộ nhớ đệm trong RAM (In-Memory Cache) lưu trữ các tài liệu SRS dựa trên mã băm nội dung SHA-256.
    
    Cung cấp thời gian truy xuất O(1), triệt tiêu độ trễ mạng và tiết kiệm 100% chi phí token
    cho các yêu cầu phân tích có cùng nội dung đầu vào.
    """

    def __init__(self) -> None:
        self._cache: Dict[str, Tuple[SRSDocument, TelemetryMetrics]] = {}

    def get(self, content_hash: str) -> Optional[Tuple[SRSDocument, TelemetryMetrics]]:
        """Truy xuất tài liệu SRS và telemetry từ bộ nhớ đệm."""
        return self._cache.get(content_hash)

    def set(self, content_hash: str, doc: SRSDocument, metrics: TelemetryMetrics) -> None:
        """Lưu trữ tài liệu SRS và telemetry vào bộ nhớ đệm."""
        self._cache[content_hash] = (doc, metrics)

    def clear(self) -> None:
        """Xóa toàn bộ dữ liệu trong bộ nhớ đệm."""
        self._cache.clear()

    def size(self) -> int:
        """Số lượng bản ghi hiện có trong bộ nhớ đệm."""
        return len(self._cache)


# Global Singleton Cache Instance
default_srs_cache = DeterministicSRSCache()


def execute_with_exponential_backoff(
    func: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> Tuple[Any, int]:
    """Thực thi hàm với cơ chế tự phục hồi Exponential Backoff Retry khi gặp lỗi mạng/rate-limit.
    
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

            # Tính toán thời gian chờ theo hàm mũ: base_delay * 2^(attempts - 1)
            delay = base_delay * (2 ** (attempts - 1))
            time.sleep(delay)
