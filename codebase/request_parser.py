"""Bộ phân tích yêu cầu người dùng và kiểm tra an toàn đầu vào cho Track C1."""
from __future__ import annotations

import re
from typing import Any

from tracing import note


def check_safety(text: str) -> str | None:
    """Chặn yêu cầu ngoài phạm vi, xin thẻ/OTP/CCCD và các kịch bản tấn công ở spec.md §5."""
    low = text.lower()
    if any(k in low for k in (
        "số thẻ", "cvv", "otp", "cccd", "mật khẩu", "chuyển khoản",
        "thanh toán giúp", "đặt vé luôn", "xuất vé", "đặt vé hộ",
    )):
        note("tu_choi: ngoai pham vi thanh toan / du lieu nhay cam")
        return (
            "Xin lỗi, trợ lý chỉ gợi ý và kiểm tra lịch trình tham quan; không hỗ trợ đặt vé, thanh toán "
            "hay thu thập số thẻ/OTP/CCCD. Phụ huynh vui lòng kiểm tra lại và tự đặt vé trên kênh chính thức."
        )
    if any(k in low for k in (
        "bỏ qua giới hạn", "kệ quy định", "cho bé vào luôn", "lách quy định", "quản lý yêu cầu",
        "nhân viên hãng", "ignore all", "bỏ qua hướng dẫn", "đặt giá vé 0", "giá vé 0đ", "mở lại trò bảo trì",
    )):
        note("tu_choi: tan cong vuot quyen / bo qua an toan tre nho")
        return (
            "Không thể đáp ứng yêu cầu ghi đè dữ liệu hệ thống, thay đổi giá vé hay bỏ qua giới hạn "
            "chiều cao/độ tuổi hoặc trạng thái bảo trì. Mọi trò chơi đều phải tuân thủ quy định tại cổng để đảm bảo an toàn."
        )
    if any(k in low for k in ("đặt phòng", "nâng hạng phòng", "hoàn vé máy bay", "đổi chuyến bay", "khách sạn")):
        note("tu_choi: ngoai pham vi C1")
        return "Trợ lý hiện chỉ hỗ trợ lập lịch trình 1 ngày tại khu vui chơi (chưa hỗ trợ đặt phòng khách sạn hoặc đổi/hoàn vé máy bay)."
    return None


def extract_budget(text: str) -> int | None:
    """Trích xuất ngân sách tối đa (VNĐ) từ câu tiếng Việt tự nhiên."""
    norm = text.lower().replace(",", ".")
    m_tr = re.search(r"(\d+(?:\.\d+)?)\s*(?:tr|triệu|trieu)", norm)
    if m_tr:
        return int(float(m_tr.group(1)) * 1_000_000)
    m_k = re.search(r"(\d+(?:\.\d+)?)\s*(?:k|nghìn|nghin|ngàn|ngan)\b", norm)
    if m_k:
        return int(float(m_k.group(1)) * 1_000)
    m_vnd = re.search(r"(\d[\d\.,]{4,})\s*(?:đ|d|vnđ|vnd)?", text.lower().replace(" ", ""))
    if m_vnd:
        digits = re.sub(r"[^\d]", "", m_vnd.group(1))
        return int(digits) if digits else None
    return None


def extract_heights(text: str) -> list[int]:
    """Trích xuất chiều cao (cm) từ các dạng '115cm', '1m15', '1m2'."""
    low = text.lower()
    heights = [int(h) for h in re.findall(r"(\d{2,3})\s*cm", low)]
    for m in re.finditer(r"\b(\d)m(\d{1,2})\b", low):
        heights.append(int(m.group(1)) * 100 + int(m.group(2).ljust(2, "0")))
    return heights


def parse_request(text: str) -> dict[str, Any]:
    """Trích xuất thành phần đoàn khách, khung giờ, loại vé, thời tiết và dịch vụ lẻ."""
    low = text.lower()
    m_adults = re.search(r"(\d+)\s*(?:người lớn|nguoi lon|bố mẹ|ba mẹ|phụ huynh)", low)
    adults = int(m_adults.group(1)) if m_adults else (2 if ("gia đình" in low or "vợ chồng" in low) else None)
    m_seniors = re.search(r"(\d+)\s*(?:người cao tuổi|ông bà|cụ|người già)", low)
    seniors = int(m_seniors.group(1)) if m_seniors else 0
    senior_ages = [int(a) for a in re.findall(r"(?:ông|bà|cụ|người cao tuổi)[^\d]{0,12}(\d{2})\s*tuổi", low)]
    if senior_ages and seniors == 0:
        seniors = len(senior_ages)

    child_heights = extract_heights(text)
    child_ages = [int(a) for a in re.findall(r"(?:bé|trẻ|con)\s*(?:gái|trai)?\s*(\d{1,2})\s*tuổi", low)]
    has_child_mention = bool(child_heights or child_ages or re.search(r"\b(?:bé|trẻ nhỏ|trẻ em|con nhỏ)\b", low))

    m_time = re.search(r"(\d{1,2})[:h](\d{0,2})\s*(?:-|đến|tới)\s*(\d{1,2})[:h](\d{0,2})", low)
    if m_time:
        start = f"{int(m_time.group(1)):02d}:{int(m_time.group(2) or 0):02d}"
        end = f"{int(m_time.group(3)):02d}:{int(m_time.group(4) or 0):02d}"
    elif "3 tiếng" in low or "ba tiếng" in low:
        start, end = "14:00", "17:00"
    elif "sau 16" in low or "sau 4h" in low or "buổi tối" in low:
        start, end = "16:00", "20:00"
    else:
        start, end = "09:00", "20:00"

    loai_ve = "AFTER_16H" if (start >= "16:00" or "after_16h" in low or "sau 16" in low) else "STANDARD"
    kich_ban = "SUNNY"
    if "mưa cả ngày" in low or "mưa to" in low or "all_day_rain" in low:
        kich_ban = "ALL_DAY_RAIN"
    elif "mưa tối" in low or "mưa buổi tối" in low or "evening_rain" in low:
        kich_ban = "EVENING_RAIN"
    elif "mưa" in low or "afternoon_rain" in low:
        kich_ban = "AFTERNOON_RAIN"

    services: list[dict[str, Any]] = []
    if "cho thú ăn" in low:
        services.append({"id": "SV01", "so_luong": 1})
    if "tủ đồ" in low or "locker" in low:
        services.append({"id": "SV03", "so_luong": 1})
    if "áo mưa" in low:
        services.append({"id": "SV04", "so_luong": 1})

    nhom_khach: list[dict[str, Any]] = [{"tuoi": 32, "cao_cm": 165} for _ in range(adults or 0)]
    for i in range(seniors):
        nhom_khach.append({"tuoi": senior_ages[i] if i < len(senior_ages) else 65, "cao_cm": 160})
    for idx, h in enumerate(child_heights):
        nhom_khach.append({"tuoi": child_ages[idx] if idx < len(child_ages) else 6, "cao_cm": h})

    return {
        "ngan_sach_vnd": extract_budget(text),
        "adults": adults,
        "has_child_mention": has_child_mention,
        "child_heights": child_heights,
        "nhom_khach": nhom_khach,
        "loai_ve": loai_ve,
        "gio_bat_dau": start,
        "gio_ket_thuc": end,
        "kich_ban": kich_ban,
        "chi_trong_nha": "trong nhà" in low,
        "dich_vu_le": services,
        "asks_unpriced": any(k in low for k in ("combo", "buffet", "wonder15", "vip", "zipline", "buggy", "xe điện")),
    }
