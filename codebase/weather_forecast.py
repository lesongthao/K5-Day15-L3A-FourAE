"""Dự báo thời tiết 7 ngày cho Đảo Hòn Tre (VinWonders Nha Trang) dùng thư viện chuẩn."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from typing import Any

_VN_TZ = timezone(timedelta(hours=7))
_LAT = 12.2236
_LON = 109.2392
_CACHE_TTL_S = 1800
_CACHE: dict[str, Any] = {"ts": 0.0, "data": None}

_WEEKDAY_VI = ("Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật")
_WEEKDAY_SHORT = ("T2", "T3", "T4", "T5", "T6", "T7", "CN")

_WEATHER_STYLES: dict[str, dict[str, str]] = {
    "SUNNY": {
        "scenario_id": "SUNNY",
        "label": "Nắng ráo",
        "short": "Nắng ráo",
        "icon": "sun",
        "hint": "",
        "advice": "Thuận lợi cả Công viên nước, cáp treo lẫn Tata Show 19:30.",
    },
    "MORNING_RAIN": {
        "scenario_id": "AFTERNOON_RAIN",
        "label": "Mưa sáng (09:00–12:00)",
        "short": "Mưa sáng",
        "icon": "rain_afternoon",
        "hint": ", dự báo mưa sáng 09:00-12:00",
        "advice": "Buổi sáng ưu tiên Thủy cung Sea World tránh mưa; chiều và tối tạnh ráo chơi ngoài trời.",
    },
    "AFTERNOON_RAIN": {
        "scenario_id": "AFTERNOON_RAIN",
        "label": "Mưa rào chiều 14:00–16:00",
        "short": "Mưa chiều",
        "icon": "rain_afternoon",
        "hint": ", dự báo mưa chiều 14:00-16:00",
        "advice": "Nên chơi ngoài trời buổi sáng; 14:00–16:00 chuyển vào Thủy cung Sea World tránh mưa.",
    },
    "EVENING_RAIN": {
        "scenario_id": "EVENING_RAIN",
        "label": "Mưa tối 18:30–20:00",
        "short": "Mưa tối",
        "icon": "rain_evening",
        "hint": ", dự báo mưa tối 18:30-20:00",
        "advice": "Ban ngày tạnh ráo; buổi tối có mưa có thể ảnh hưởng Tata Show 19:30.",
    },
    "ALL_DAY_RAIN": {
        "scenario_id": "ALL_DAY_RAIN",
        "label": "Mưa cả ngày",
        "short": "Mưa cả ngày",
        "icon": "rain_heavy",
        "hint": ", dự báo mưa cả ngày",
        "advice": "Ưu tiên Thủy cung, Rạp Phim Bay, Vườn bướm, Nhà bóng và show trong nhà.",
    },
}


def _day_labels(day_obj: date, idx: int) -> tuple[str, str]:
    """Tạo nhãn tương đối (Hôm nay/Ngày mai/Ngày kia) và thứ tiếng Việt."""
    wd = _WEEKDAY_VI[day_obj.weekday()]
    if idx == 0:
        return "Hôm nay", wd
    if idx == 1:
        return "Ngày mai", wd
    if idx == 2:
        return "Ngày kia", wd
    return _WEEKDAY_SHORT[day_obj.weekday()], wd


def _build_day_record(
    day_obj: date, idx: int, temp_min: int, temp_max: int, rain_prob: int, style_key: str,
) -> dict[str, Any]:
    """Đóng gói thông tin chuẩn hóa cho 1 ngày dùng chung giữa online và offline."""
    rel_label, weekday_vi = _day_labels(day_obj, idx)
    meta = _WEATHER_STYLES.get(style_key, _WEATHER_STYLES["SUNNY"])
    return {
        "date": day_obj.isoformat(), "display_date": day_obj.strftime("%d/%m"),
        "full_date": day_obj.strftime("%d/%m/%Y"), "weekday_vi": weekday_vi, "rel_label": rel_label,
        "temp_min": int(temp_min), "temp_max": int(temp_max),
        "rain_prob": max(0, min(100, int(rain_prob))), "icon": meta["icon"],
        "scenario_id": meta["scenario_id"], "weather_label": meta["label"], "short_label": meta["short"],
        "advice": meta["advice"], "prompt_hint": meta["hint"],
    }


def _build_offline_forecast(today: date | None = None) -> dict[str, Any]:
    """Tạo dự báo 7 ngày tham khảo đủ sắc thái nắng/mưa theo khung giờ khi chạy offline."""
    base = today or datetime.now(_VN_TZ).date()
    pattern = [
        ("SUNNY", 25, 31, 15), ("SUNNY", 25, 32, 20), ("MORNING_RAIN", 24, 30, 60),
        ("AFTERNOON_RAIN", 24, 30, 65), ("EVENING_RAIN", 24, 30, 60), ("SUNNY", 25, 31, 15),
        ("ALL_DAY_RAIN", 23, 28, 85),
    ]
    days = [_build_day_record(base + timedelta(days=i), i, mn, mx, p, sc) for i, (sc, mn, mx, p) in enumerate(pattern)]
    return {"location": "Đảo Hòn Tre, Nha Trang", "source": "offline_sample", "source_label": "Dự báo tham khảo (chế độ ngoại tuyến)", "days": days}


def _classify_day_scenario(
    day_iso: str, hourly_by_day: dict[str, dict[int, tuple[int, float, int]]],
) -> tuple[str, int]:
    """Quy đổi dữ liệu giờ 09:00-20:00 từ Open-Meteo sang sắc thái thời tiết & % mưa ban ngày."""
    hours = hourly_by_day.get(day_iso, {})

    def _slot_stats(h_start: int, h_end: int) -> tuple[float, int]:
        mm_sum = 0.0
        p_max = 0
        for hr in range(h_start, h_end + 1):
            prob, mm, _ = hours.get(hr, (0, 0.0, 0))
            mm_sum += mm
            if prob > p_max:
                p_max = prob
        return mm_sum, p_max

    m_mm, m_prob = _slot_stats(9, 13)
    a_mm, a_prob = _slot_stats(14, 17)
    e_mm, e_prob = _slot_stats(18, 20)
    park_mm = m_mm + a_mm + e_mm
    park_prob = max(m_prob, a_prob, e_prob)

    if park_mm >= 10.0 and m_mm >= 2.5 and a_mm >= 1.5:
        return "ALL_DAY_RAIN", park_prob
    if e_mm >= 2.5 and e_mm >= a_mm:
        return "EVENING_RAIN", park_prob
    if (park_mm < 2.5 and max(m_mm, a_mm, e_mm) < 1.5) or (a_mm < 0.5 and e_mm < 0.5 and m_mm < 4.0):
        return "SUNNY", min(park_prob, 35) if park_mm < 2.5 else park_prob
    if m_mm >= 2.5 and a_mm < 1.0:
        return "MORNING_RAIN", park_prob
    return "AFTERNOON_RAIN", park_prob


def _fetch_open_meteo(timeout_s: float = 3.0) -> dict[str, Any]:
    """Gọi Open-Meteo lấy dự báo 7 ngày theo giờ & ngày tại tọa độ Đảo Hòn Tre."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={_LAT}&longitude={_LON}"
        "&daily=temperature_2m_min,temperature_2m_max"
        "&hourly=precipitation_probability,precipitation,weather_code"
        "&timezone=Asia%2FHo_Chi_Minh&forecast_days=7"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "FourAE-VinWonders-Planner/1.0"})
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    daily = raw.get("daily") or {}
    hourly = raw.get("hourly") or {}
    hourly_by_day: dict[str, dict[int, tuple[int, float, int]]] = {}
    for ts, p_prob, p_mm, w_code in zip(
        hourly.get("time") or [],
        hourly.get("precipitation_probability") or [],
        hourly.get("precipitation") or [],
        hourly.get("weather_code") or [],
    ):
        if "T" not in str(ts):
            continue
        d_str, h_str = str(ts).split("T", 1)
        hourly_by_day.setdefault(d_str, {})[int(h_str[:2])] = (int(p_prob or 0), float(p_mm or 0.0), int(w_code or 0))

    days: list[dict[str, Any]] = []
    dates = daily.get("time") or []
    t_mins = daily.get("temperature_2m_min") or []
    t_maxs = daily.get("temperature_2m_max") or []

    for idx, d_str in enumerate(dates[:7]):
        day_obj = date.fromisoformat(str(d_str))
        t_min = round(float(t_mins[idx])) if idx < len(t_mins) and t_mins[idx] is not None else 25
        t_max = round(float(t_maxs[idx])) if idx < len(t_maxs) and t_maxs[idx] is not None else 31
        sc_id, prob = _classify_day_scenario(str(d_str), hourly_by_day)
        days.append(_build_day_record(day_obj, idx, t_min, t_max, prob, sc_id))

    if len(days) < 7:
        raise ValueError("Open-Meteo trả về thiếu dữ liệu 7 ngày.")
    return {
        "location": "Đảo Hòn Tre, Nha Trang",
        "source": "open-meteo",
        "source_label": "Dự báo Open-Meteo (Đảo Hòn Tre, Nha Trang)",
        "days": days,
    }


def get_7day_forecast(force_offline: bool = False) -> dict[str, Any]:
    """Trả về dự báo thời tiết 7 ngày tới (dùng cache 30 phút, tự fallback nếu mất mạng)."""
    if force_offline or os.environ.get("FOURAE_OFFLINE_WEATHER") == "1":
        return _build_offline_forecast()
    now = time.monotonic()
    cached = _CACHE.get("data")
    if cached and (now - float(_CACHE.get("ts", 0.0))) < _CACHE_TTL_S:
        return cached
    try:
        data = _fetch_open_meteo()
        _CACHE["ts"] = now
        _CACHE["data"] = data
        return data
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        return _build_offline_forecast()
