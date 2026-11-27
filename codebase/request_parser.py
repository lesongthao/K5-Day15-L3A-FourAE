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
    m_half = re.search(r"(?<![\.,\d])(\d+)\s*(?:tr|triệu|trieu)\s*rưỡi\b", norm)
    if m_half:
        return int(m_half.group(1)) * 1_000_000 + 500_000
    m_tr_k = re.search(r"(?<![\.,\d])(\d+)\s*(?:tr|triệu|trieu)\s*(\d{3})(?:\s*(?:k|nghìn|nghin|ngàn|ngan))?\b", norm)
    if m_tr_k:
        return int(m_tr_k.group(1)) * 1_000_000 + int(m_tr_k.group(2)) * 1_000
    m_tr_short = re.search(
        r"(?<![\.,\d])(\d+)\s*(?:tr|triệu|trieu)\s+(\d{1,2})\b(?!\s*(?:người|nguoi|bé|trẻ|con|giờ|gio|h\b|tuổi|trò|khu|show|vé|tiếng|phút|cm|m\b|m\d))",
        norm,
    )
    if m_tr_short:
        return int(m_tr_short.group(1)) * 1_000_000 + int(m_tr_short.group(2).ljust(2, "0")) * 10_000
    m_tr = re.search(r"(\d+(?:\.\d+)?)\s*(?:tr|triệu|trieu)", norm)
    if m_tr:
        return int(float(m_tr.group(1)) * 1_000_000)
    m_k = re.search(r"(\d+(?:\.\d+)?)\s*(?:k|nghìn|nghin|ngàn|ngan)\b", norm)
    if m_k:
        return int(float(m_k.group(1)) * 1_000)
    cleaned_vnd = re.sub(r"\b\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?\b", " ", text.lower())
    m_vnd = re.search(r"(\d[\d\.,]{4,})\s*(?:đ|d|vnđ|vnd)?", cleaned_vnd.replace(" ", ""))
    if m_vnd:
        digits = re.sub(r"[^\d]", "", m_vnd.group(1))
        return int(digits) if digits else None
    return None


def extract_heights(text: str) -> list[int]:
    """Trích xuất chiều cao (cm) từ các dạng '115cm', '1m15', '1 mét 2', 'cao 1 mét', 'dưới 1 mét'."""
    low = text.lower()
    heights = [int(h) for h in re.findall(r"(\d{2,3})\s*cm", low)]
    for m in re.finditer(r"\b(\d)m(\d{1,2})\b", low):
        heights.append(int(m.group(1)) * 100 + int(m.group(2).ljust(2, "0")))
    for m in re.finditer(r"\b(\d)\s*(?:mét|met)\s*(\d{1,2})\b", low):
        heights.append(int(m.group(1)) * 100 + int(m.group(2).ljust(2, "0")))
    under_1m = re.findall(r"(?:dưới|<)\s*1\s*(?:mét|met|m(?![\d]))", low)
    heights.extend([95] * len(under_1m))
    for m in re.finditer(r"\b(?:cao|tầm|khoảng)\s+(\d)\s*(?:mét|met|m)\b", low):
        prefix = low[max(0, m.start() - 12):m.start()]
        if "dưới" not in prefix and "<" not in prefix:
            heights.append(int(m.group(1)) * 100)
    return heights


def _extract_time_window(low: str) -> tuple[str, str]:
    """Tách khung giờ đi chơi, bỏ qua cặp giờ mưa ngắn (vd 'mưa chiều 14:00-16:00') nếu đứng trước giờ đi."""
    time_pat = re.compile(
        r"(\d{1,2})\s*(?::|h|giờ|gio)\s*(\d{0,2})\s*(?:-|–|đến|tới)\s*(\d{1,2})\s*(?::|h|giờ|gio)\s*(\d{0,2})"
    )
    fallback_pair: tuple[str, str] | None = None
    for m in time_pat.finditer(low):
        s_h, s_m_val = int(m.group(1)), int(m.group(2) or 0)
        e_h, e_m_val = int(m.group(3)), int(m.group(4) or 0)
        if not (0 <= s_h <= 23 and 0 <= e_h <= 23):
            continue
        pair = (f"{s_h:02d}:{s_m_val:02d}", f"{e_h:02d}:{e_m_val:02d}")
        if fallback_pair is None:
            fallback_pair = pair
        clause = re.split(r"[,.;]", low[max(0, m.start() - 28):m.start()])[-1]
        is_travel = bool(re.search(r"\b(?:đi|chơi|tham\s*quan|vào\s*cổng|khung\s*giờ|lịch)\s*(?:từ)?\s*$", clause))
        span_min = (e_h * 60 + e_m_val) - (s_h * 60 + s_m_val)
        if "mưa" in clause and not is_travel and 0 < span_min <= 240:
            continue
        return pair

    m_start = re.search(r"từ\s*(\d{1,2})\s*(?::|h|giờ|gio)\s*(\d{0,2})", low)
    if m_start and 9 <= int(m_start.group(1)) <= 19:
        return f"{int(m_start.group(1)):02d}:{int(m_start.group(2) or 0):02d}", "20:00"
    if fallback_pair is not None:
        return fallback_pair
    if "3 tiếng" in low or "ba tiếng" in low:
        return "14:00", "17:00"
    if "sau 16" in low or "sau 4h" in low or "buổi tối" in low:
        return "16:00", "20:00"
    return "09:00", "20:00"


def _extract_services(low: str) -> list[dict[str, Any]]:
    """Tách dịch vụ lẻ ngoài vé và số lượng, không nhầm 'dự báo mưa' hoặc câu hỏi mang áo mưa cá nhân."""
    services: list[dict[str, Any]] = []
    if "cho thú ăn" in low:
        m_q = re.search(r"(\d+)\s*(?:phần|suất|lượt|gói)?\s*cho\s*thú\s*ăn", low)
        services.append({"id": "SV01", "so_luong": max(1, int(m_q.group(1))) if m_q else 1})
    if "tủ đồ" in low or "locker" in low:
        m_q = re.search(r"(\d+)\s*(?:cái|chiếc|tủ)?\s*(?:tủ\s*đồ|locker)", low)
        services.append({"id": "SV03", "so_luong": max(1, int(m_q.group(1))) if m_q else 1})
    m_raincoat = re.search(r"(?:(\d+)\s*(?:cái|chiếc)?\s*)?(?<!\w)áo\s*mưa(?:\s*giấy)?\b", low)
    if m_raincoat:
        has_personal_bring = bool(re.search(r"(?:mang|đem)\s*(?:theo\s*)?áo\s*mưa", low))
        has_buy_cue = bool(m_raincoat.group(1) or any(k in low for k in ("mua", "thêm", "thuê", "dự phòng", "sv04")))
        if has_buy_cue or not has_personal_bring:
            services.append({"id": "SV04", "so_luong": max(1, int(m_raincoat.group(1))) if m_raincoat.group(1) else 1})
    return services


def parse_request(text: str) -> dict[str, Any]:
    """Trích xuất thành phần đoàn khách, khung giờ, loại vé, thời tiết và dịch vụ lẻ."""
    low = text.lower()
    primary_adults = re.findall(r"(\d+)\s*(?:người lớn|nguoi lon|bố mẹ|ba mẹ|phụ huynh|vợ chồng)\b", low)
    if primary_adults:
        adults: int | None = sum(int(x) for x in primary_adults)
    else:
        solo_adults = re.findall(r"(\d+)\s*(?:bố|ba|cha|mẹ|vợ|chồng)\b", low)
        if solo_adults:
            adults = sum(int(x) for x in solo_adults)
        elif re.search(r"\b(?:bố\s*mẹ|ba\s*mẹ|hai\s*vợ\s*chồng|vợ\s*chồng|gia\s*đình)\b", low):
            adults = 2
        elif re.search(r"\b(?:một\s*mình|1\s*mình|mình\s*tôi)\b", low):
            adults = 1
        else:
            adults = None

    m_seniors = re.search(r"(\d+)\s*(?:người cao tuổi|ông bà|cụ|người già)", low)
    seniors = int(m_seniors.group(1)) if m_seniors else 0
    senior_ages = [int(a) for a in re.findall(r"(?:ông|bà|cụ|người cao tuổi)[^\d]{0,24}(\d{2})\s*tuổi", low)]
    if senior_ages:
        seniors = max(seniors, len(senior_ages))

    child_heights = extract_heights(text)
    child_ages = [int(a) for a in re.findall(r"(?:bé|trẻ|con)\s*(?:gái|trai)?\s*(\d{1,2})\s*tuổi", low)]
    child_counts = [int(x) for x in re.findall(r"(\d+)\s*(?:bé|trẻ\s*nhỏ|trẻ\s*em|trẻ|con\s*nhỏ|con\s*trai|con\s*gái)\b", low)]
    explicit_kids = sum(child_counts)
    missing_other_height = False
    if explicit_kids > len(child_heights) and child_heights:
        partial_hint = bool(re.search(r"\b(?:bé\s*(?:lớn|nhỏ|đầu|út|thứ)|một\s*bé|1\s*bé)\b", low))
        diff_ages = len(child_ages) >= 2 and not any(w in low for w in ("đều", "cùng", "bằng nhau", "cả 2", "cả hai"))
        if len(child_heights) == 1 and not partial_hint and not diff_ages:
            child_heights = child_heights * explicit_kids
        else:
            missing_other_height = True
    has_child_mention = bool(child_heights or child_ages or re.search(r"\b(?:bé|trẻ nhỏ|trẻ em|con nhỏ)\b", low))

    start, end = _extract_time_window(low)
    loai_ve = "AFTER_16H" if (start >= "16:00" or "after_16h" in low or "sau 16" in low) else "STANDARD"

    weather_text = re.sub(r"(?<!\w)áo\s*mưa(?:\s*giấy)?\b", " ", low)
    has_negated_rain = bool(re.search(r"\b(?:không|chẳng|chưa|hết|tạnh|ít)\s+(?:có\s+)?mưa\b", weather_text))
    weather_text = re.sub(r"\b(?:không|chẳng|chưa|hết|tạnh|ít)\s+(?:có\s+)?mưa\b", " ", weather_text)
    has_morning_rain_range = bool(
        re.search(r"mưa[^\d]{0,16}(?:0?9|10|11)\s*(?::|h|giờ)?\s*(?:00)?\s*(?:-|–|đến|tới)\s*1[12]", weather_text)
    )
    kich_ban = "SUNNY"
    if "mưa cả ngày" in weather_text or "mưa to" in weather_text or "all_day_rain" in weather_text:
        kich_ban = "ALL_DAY_RAIN"
    elif "mưa tối" in weather_text or "mưa buổi tối" in weather_text or "evening_rain" in weather_text:
        kich_ban = "EVENING_RAIN"
    elif "mưa sáng" in weather_text or "mưa buổi sáng" in weather_text or "morning_rain" in weather_text or has_morning_rain_range:
        kich_ban = "MORNING_RAIN"
    elif "mưa" in weather_text or "afternoon_rain" in weather_text:
        kich_ban = "AFTERNOON_RAIN"
    weather_mentioned = bool(
        has_negated_rain
        or "mưa" in weather_text
        or any(k in low for k in ("sunny", "morning_rain", "afternoon_rain", "evening_rain", "all_day_rain"))
        or re.search(r"\b(?:nắng\s*ráo|trời\s*nắng|tạnh\s*ráo)\b", low)
    )

    nhom_khach: list[dict[str, Any]] = [{"tuoi": 32, "cao_cm": 165} for _ in range(adults or 0)]
    for i in range(seniors):
        nhom_khach.append({"tuoi": senior_ages[i] if i < len(senior_ages) else 65, "cao_cm": 160})
    for idx, h in enumerate(child_heights):
        age_val = child_ages[idx] if idx < len(child_ages) else (child_ages[0] if len(child_ages) == 1 else 6)
        nhom_khach.append({"tuoi": age_val, "cao_cm": h})

    return {
        "ngan_sach_vnd": extract_budget(text),
        "adults": adults,
        "has_child_mention": has_child_mention,
        "child_heights": child_heights,
        "thieu_chieu_cao_be_khac": missing_other_height,
        "nhom_khach": nhom_khach,
        "loai_ve": loai_ve,
        "gio_bat_dau": start,
        "gio_ket_thuc": end,
        "kich_ban": kich_ban,
        "co_nhac_thoi_tiet": weather_mentioned,
        "chi_trong_nha": "trong nhà" in low,
        "dich_vu_le": _extract_services(low),
        "asks_unpriced": any(k in low for k in ("combo", "buffet", "wonder15", "vip", "zipline", "buggy", "xe điện")),
    }
