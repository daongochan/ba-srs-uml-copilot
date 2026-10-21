"""Security sanitization and input guardrails for BA & System Architect Copilot."""

import re
from typing import Any, Optional

# Giới hạn an toàn đầu vào
MAX_MEETING_NOTES_LENGTH = 50_000
MAX_SQL_DDL_LENGTH = 65_536
MAX_SQL_STATEMENTS = 50

# Regex mẫu phát hiện khóa Google Gemini API (AIzaSy...)
_API_KEY_REGEX = re.compile(r"AIza[0-9A-Za-z\-_]{35}")

# Regex phát hiện tham số query URL chứa API key hoặc token
_URL_KEY_PARAM_REGEX = re.compile(r"([?&](?:key|api_key|token|auth)=)[^&\s'\"]+", re.IGNORECASE)


def sanitize_error_message(error: Any, api_key: Optional[str] = None) -> str:
    """Loại bỏ thông tin nhạy cảm (API Keys, Token bí mật, URL params) khỏi thông báo lỗi.
    
    Args:
        error: Đối tượng Exception hoặc chuỗi thông báo lỗi.
        api_key: Khóa API hiện tại cần đảm bảo loại bỏ triệt để nếu xuất hiện.
        
    Returns:
        str: Chuỗi thông báo lỗi an toàn để hiển thị trên giao diện hoặc ghi log.
    """
    if error is None:
        return "Đã xảy ra lỗi không xác định."

    msg = str(error)

    # 1. Che giấu API key nếu được cung cấp cụ thể
    if api_key and api_key.strip():
        clean_key = api_key.strip()
        if len(clean_key) >= 8:
            msg = msg.replace(clean_key, "[REDACTED_API_KEY]")

    # 2. Quét và che giấu theo mẫu chuẩn Google API Key
    msg = _API_KEY_REGEX.sub("[REDACTED_API_KEY]", msg)

    # 3. Che giấu các query param dạng ?key=... hoặc &api_key=...
    msg = _URL_KEY_PARAM_REGEX.sub(r"\1[REDACTED]", msg)

    # 4. Giới hạn độ dài chuỗi lỗi hiển thị người dùng (tránh flooding/reflection)
    if len(msg) > 1000:
        msg = msg[:1000] + "... [nội dung lỗi được rút gọn để bảo vệ an toàn]"

    return msg
