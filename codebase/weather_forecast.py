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

_SCENARIO_META: dict[str, dict[str, str]] = {
    "SUNNY": {
        "label": "Nắng ráo",
        "short": "Nắng ráo",
        "icon": "sun",
        "hint": "",
        "advice": "Thuận lợi cả Công viên nước, cáp treo lẫn Tata Show 19:30.",
    },
    "AFTERNOON_RAIN": {
        "label": "Mưa rào chiều 14:00–16:00",
        "short": "Mưa chiều",
        "icon": "rain_afternoon",
        "hint": ", dự báo mưa chiều 14:00-16:00",
        "advice": "Nên chơi ngoài trời buổi sáng; 14:00–16:00 chuyển vào Thủy cung Sea World tránh mưa.",
    },
    "EVENING_RAIN": {
        "label": "Mưa tối 18:30–20:00",
        "short": "Mưa tối",
        "icon": "rain_evening",
        "hint": ", dự báo mưa tối 18:30-20:00",
        "advice": "Ban ngày tạnh ráo; buổi tối có mưa có thể ảnh hưởng Tata Show 19:30.",
    },
    "ALL_DAY_RAIN": {
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
    day_obj: date, idx: int, temp_min: int, temp_max: int, rain_prob: int, scenario_id: str,
) -> dict[str, Any]:
    """Đóng gói thông tin chuẩn hóa cho 1 ngày dùng chung giữa online và offline."""
    rel_label, weekday_vi = _day_labels(day_obj, idx)
    meta = _SCENARIO_META.get(scenario_id, _SCENARIO_META["SUNNY"])
    return {
        "date": day_obj.isoformat(), "display_date": day_obj.strftime("%d/%m"),
        "full_date": day_obj.strftime("%d/%m/%Y"), "weekday_vi": weekday_vi, "rel_label": rel_label,
        "temp_min": int(temp_min), "temp_max": int(temp_max),
        "rain_prob": max(0, min(100, int(rain_prob))), "icon": meta["icon"],
        "scenario_id": scenario_id, "weather_label": meta["label"], "short_label": meta["short"],
        "advice": meta["advice"], "prompt_hint": meta["hint"],
    }


def _build_offline_forecast(today: date | None = None) -> dict[str, Any]:
    """Tạo dự báo 7 ngày tham khảo theo khí hậu Nha Trang khi mất mạng hoặc chạy test."""
    base = today or datetime.now(_VN_TZ).date()
    pattern = [
        ("SUNNY", 25, 31, 15), ("SUNNY", 25, 32, 20), ("AFTERNOON_RAIN", 24, 30, 65),
        ("SUNNY", 25, 31, 10), ("EVENING_RAIN", 24, 30, 60), ("SUNNY", 25, 31, 15),
        ("ALL_DAY_RAIN", 23, 28, 85),
    ]
    days = [_build_day_record(base + timedelta(days=i), i, mn, mx, p, sc) for i, (sc, mn, mx, p) in enumerate(pattern)]
    return {"location": "Đảo Hòn Tre, Nha Trang", "source": "offline_sample", "source_label": "Dự báo tham khảo (chế độ ngoại tuyến)", "days": days}


def _classify_day_scenario(
    day_iso: str, wmo_code: int, rain_prob_max: int, precip_sum: float,
    hourly_by_day: dict[str, dict[int, tuple[int, float, int]]],
) -> str:
    """Quy đổi dữ liệu giờ/ngày từ Open-Meteo sang 1 trong 4 kịch bản weather.json."""
    hours = hourly_by_day.get(day_iso, {})

    def _slot_wet(h_start: int, h_end: int) -> bool:
        for hr in range(h_start, h_end + 1):
            prob, mm, code = hours.get(hr, (0, 0.0, 0))
            if prob >= 55 or mm >= 1.2 or code >= 51:
                return True
        return False

    wet_morning = _slot_wet(9, 13)
    wet_afternoon = _slot_wet(14, 17)
    wet_evening = _slot_wet(18, 20)

    if precip_sum >= 15.0 or (wet_morning and wet_afternoon) or (wmo_code >= 65 and rain_prob_max >= 70):
        return "ALL_DAY_RAIN"
    if wet_evening and not wet_morning and not wet_afternoon:
        return "EVENING_RAIN"
    if wet_afternoon or wet_morning or rain_prob_max >= 60 or wmo_code >= 51:
        return "AFTERNOON_RAIN"
    return "SUNNY"


def _fetch_open_meteo(timeout_s: float = 3.0) -> dict[str, Any]:
    """Gọi Open-Meteo lấy dự báo 7 ngày theo giờ & ngày tại tọa độ Đảo Hòn Tre."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={_LAT}&longitude={_LON}"
        "&daily=weather_code,temperature_2m_min,temperature_2m_max,precipitation_probability_max,precipitation_sum"
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
        hr = int(h_str[:2])
        hourly_by_day.setdefault(d_str, {})[hr] = (int(p_prob or 0), float(p_mm or 0.0), int(w_code or 0))

    days: list[dict[str, Any]] = []
    dates = daily.get("time") or []
    codes = daily.get("weather_code") or []
    t_mins = daily.get("temperature_2m_min") or []
    t_maxs = daily.get("temperature_2m_max") or []
    probs = daily.get("precipitation_probability_max") or []
    sums = daily.get("precipitation_sum") or []

    for idx, d_str in enumerate(dates[:7]):
        day_obj = date.fromisoformat(str(d_str))
        wmo = int(codes[idx]) if idx < len(codes) and codes[idx] is not None else 0
        t_min = round(float(t_mins[idx])) if idx < len(t_mins) and t_mins[idx] is not None else 25
        t_max = round(float(t_maxs[idx])) if idx < len(t_maxs) and t_maxs[idx] is not None else 31
        prob = int(probs[idx]) if idx < len(probs) and probs[idx] is not None else 20
        p_sum = float(sums[idx]) if idx < len(sums) and sums[idx] is not None else 0.0
        sc_id = _classify_day_scenario(str(d_str), wmo, prob, p_sum, hourly_by_day)
        days.append(_build_day_record(day_obj, idx, t_min, t_max, prob, sc_id))

    if len(days) < 7:
        raise ValueError("Open-Meteo trả về thiếu dữ liệu 7 ngày.")
    return {
        "location": "Đảo Hòn Tre, Nha Trang",
        "source": "open-meteo",
        "source_label": "Dự báo Open-Meteo · Đảo Hòn Tre, Nha Trang",
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
