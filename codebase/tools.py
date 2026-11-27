"""Công cụ chỉ đọc cho bài toán Track C1 — Lịch trình khu vui chơi gia đình.

Mỗi công cụ gắn @tool để tracing.py tự ghi lại input, output, độ trễ và lỗi.
Không công cụ nào có tác động ra ngoài (chỉ đọc dữ liệu và kiểm tra logic).
"""
from __future__ import annotations

import functools
import json
import os
from typing import Any

from tracing import tool

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "park_data.json",
)


@functools.lru_cache(maxsize=1)
def _load_park_data() -> dict[str, Any]:
    """Đọc và cache dữ liệu khu vui chơi mẫu từ data/park_data.json."""
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _to_minutes(hhmm: str) -> int:
    """Chuyển chuỗi giờ 'HH:MM' thành tổng số phút tính từ 00:00."""
    parts = hhmm.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Định dạng giờ không hợp lệ: {hhmm!r} (cần HH:MM)")
    hour, minute = int(parts[0]), int(parts[1])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Giờ nằm ngoài khoảng 00:00-23:59: {hhmm!r}")
    return hour * 60 + minute


def _is_raining(weather: dict[str, Any], start_min: int, end_min: int) -> bool:
    """Kiểm tra khoảng [start_min, end_min] có giao với khung giờ mưa không."""
    for w in weather.get("windows", []):
        if w.get("condition") != "mua":
            continue
        ws, we = _to_minutes(w["start"]), _to_minutes(w["end"])
        if max(start_min, ws) < min(end_min, we):
            return True
    return False


def _match_zone(zone_value: str, filter_zone: str) -> bool:
    """So khớp tên khu không phân biệt hoa thường."""
    if not filter_zone:
        return True
    return zone_value.strip().lower() == filter_zone.strip().lower()


@tool
def tra_diem_choi(
    khu: str = "",
    do_tuoi_nho_nhat: int | None = None,
    chieu_cao_nho_nhat_cm: int | None = None,
    chi_trong_nha: bool = False,
    ngay: str = "2026-11-28",
) -> dict[str, Any]:
    """Tra điểm chơi theo khu, độ tuổi, chiều cao trẻ nhỏ, trong nhà và trạng thái bảo trì theo ngày.

    Input: khu (str), do_tuoi_nho_nhat (int|None), chieu_cao_nho_nhat_cm (int|None), chi_trong_nha (bool), ngay (str).
    Output: dict gồm danh sách điểm chơi phù hợp (kèm trang_thai), vé cổng và dịch vụ lẻ tham khảo.
    Tác động ra ngoài: Không (chỉ đọc).
    """
    data = _load_park_data()
    weather = data.get("weather_scenarios", {}).get(ngay, {})
    maintenance = set(weather.get("maintenance_attractions", []))
    items: list[dict[str, Any]] = []
    for attr in data.get("attractions", []):
        if not _match_zone(attr["zone"], khu):
            continue
        if chi_trong_nha and not attr["indoor"]:
            continue
        if do_tuoi_nho_nhat is not None and attr["min_age"] > do_tuoi_nho_nhat:
            continue
        if chieu_cao_nho_nhat_cm is not None and attr["min_height_cm"] > chieu_cao_nho_nhat_cm:
            continue
        item = dict(attr)
        item["trang_thai"] = "bao_tri" if attr["id"] in maintenance else "hoat_dong"
        items.append(item)
    return {
        "cong_vien": data["metadata"]["name"],
        "ve_cong_co_ban": data["metadata"]["entry_fee"],
        "dich_vu_le_tham_khao": data["metadata"].get("extra_services", {}),
        "tong_so": len(items),
        "diem_choi": items,
    }


@tool
def tra_lich_show(ngay: str = "2026-11-28", chi_trong_nha: bool = False) -> dict[str, Any]:
    """Tra danh sách show biểu diễn và trạng thái hoạt động/bị huỷ theo ngày.

    Input: ngay (str, YYYY-MM-DD), chi_trong_nha (bool).
    Output: dict gồm ngày, trạng thái có dữ liệu và danh sách show kèm trạng thái.
    Tác động ra ngoài: Không (chỉ đọc).
    """
    data = _load_park_data()
    weather = data.get("weather_scenarios", {}).get(ngay)
    if weather is None:
        return {
            "ngay": ngay,
            "co_du_lieu": False,
            "loi": f"Chưa có dữ liệu lịch show cho ngày {ngay}. Các ngày có sẵn: {list(data.get('weather_scenarios', {}).keys())}",
            "shows": [],
        }
    cancelled = set(weather.get("cancelled_shows", []))
    shows_out: list[dict[str, Any]] = []
    for sh in data.get("shows", []):
        if chi_trong_nha and not sh["indoor"]:
            continue
        item = dict(sh)
        item["trang_thai"] = "bi_huy" if sh["id"] in cancelled else "hoat_dong"
        shows_out.append(item)
    return {"ngay": ngay, "co_du_lieu": True, "shows": shows_out}


@tool
def tra_thoi_tiet(ngay: str = "2026-11-28") -> dict[str, Any]:
    """Tra dự báo thời tiết theo khung giờ và danh sách show bị huỷ trong ngày.

    Input: ngay (str, YYYY-MM-DD).
    Output: dict gồm trạng thái có dữ liệu, mô tả thời tiết, các khung giờ và show bị huỷ.
    Tác động ra ngoài: Không (chỉ đọc).
    """
    data = _load_park_data()
    weather = data.get("weather_scenarios", {}).get(ngay)
    if weather is None:
        return {
            "ngay": ngay,
            "co_du_lieu": False,
            "loi": f"Chưa có dữ liệu thời tiết cho ngày {ngay}.",
        }
    return {
        "ngay": ngay,
        "co_du_lieu": True,
        "tom_tat": weather["summary"],
        "khung_gio": weather["windows"],
        "show_bi_huy": weather.get("cancelled_shows", []),
    }


@tool
def uoc_thoi_gian_di(khu_a: str, khu_b: str) -> dict[str, Any]:
    """Ước lượng thời gian di chuyển bộ giữa hai khu vực (đã cộng biên đi cùng trẻ nhỏ).

    Input: khu_a (str), khu_b (str).
    Output: dict gồm số phút di chuyển hoặc thông báo lỗi nếu tên khu không tồn tại.
    Tác động ra ngoài: Không (chỉ đọc).
    """
    data = _load_park_data()
    matrix: dict[str, dict[str, int]] = data.get("travel_times_min", {})
    zone_map = {z.lower(): z for z in matrix}
    za = zone_map.get(khu_a.strip().lower())
    zb = zone_map.get(khu_b.strip().lower())
    if not za or not zb:
        return {
            "hop_le": False,
            "phut": 15,
            "loi": f"Không tìm thấy khu vực ({khu_a!r}, {khu_b!r}). Khu hợp lệ: {list(matrix.keys())}",
        }
    return {"hop_le": True, "khu_a": za, "khu_b": zb, "phut": matrix[za][zb]}


def _calc_entry_fee(
    entry_fee: dict[str, int],
    so_nguoi_lon: int,
    danh_sach_tuoi_tre: list[int],
) -> tuple[int, int]:
    """Tính tiền vé cổng và trả về (tổng vé cổng, số trẻ >= 3 tuổi phải mua vé)."""
    paying_children = sum(1 for age in danh_sach_tuoi_tre if age >= 3)
    total = so_nguoi_lon * entry_fee["adult"] + paying_children * entry_fee["child_3_10"]
    return total, paying_children


@tool
def kiem_lich_trinh(
    lich: list[dict[str, Any]],
    ngan_sach_vnd: int,
    so_nguoi_lon: int,
    danh_sach_tuoi_tre: list[int],
    ngay: str = "2026-11-28",
    gio_bat_dau: str = "09:00",
    gio_ket_thuc: str = "17:30",
    chieu_cao_tre_cm: list[int] | None = None,
) -> dict[str, Any]:
    """Kiểm tra toàn bộ ràng buộc lịch trình (giờ, di chuyển, tuổi, chiều cao, mưa, tiền) bằng code.

    Input: lich (list[{id, start, end}]), ngan_sach_vnd (int), so_nguoi_lon (int),
           danh_sach_tuoi_tre (list[int]), ngay (str), gio_bat_dau (str), gio_ket_thuc (str), chieu_cao_tre_cm (list[int]|None).
    Output: dict {hop_le, tong_tien_vnd, chi_tiet_chi_phi, vi_pham, goi_y_noi_rang_buoc}.
    Tác động ra ngoài: Không (chỉ đọc và tính toán).
    """
    data = _load_park_data()
    vi_pham: list[str] = []
    goi_y: list[str] = []

    if so_nguoi_lon <= 0:
        vi_pham.append("Phải có ít nhất 1 người lớn đi cùng trẻ nhỏ.")

    entry_total, paying_children = _calc_entry_fee(
        data["metadata"]["entry_fee"], so_nguoi_lon, danh_sach_tuoi_tre
    )
    weather = data.get("weather_scenarios", {}).get(ngay)
    if weather is None:
        vi_pham.append(f"Không có dữ liệu thời tiết/lịch show cho ngày {ngay}.")
        return {
            "hop_le": False,
            "tong_tien_vnd": entry_total,
            "chi_tiet_chi_phi": {"ve_cong": entry_total, "phu_thu": 0},
            "vi_pham": vi_pham,
            "goi_y_noi_rang_buoc": ["Chọn ngày có dữ liệu: " + ", ".join(data["weather_scenarios"].keys())],
        }

    catalog = {a["id"]: ("attraction", a) for a in data.get("attractions", [])}
    for sh in data.get("shows", []):
        catalog[sh["id"]] = ("show", sh)

    win_start, win_end = _to_minutes(gio_bat_dau), _to_minutes(gio_ket_thuc)
    min_age_group = min(danh_sach_tuoi_tre) if danh_sach_tuoi_tre else 99
    min_height_group = min(chieu_cao_tre_cm) if chieu_cao_tre_cm else None
    cancelled = set(weather.get("cancelled_shows", []))
    maintenance = set(weather.get("maintenance_attractions", []))
    matrix = data.get("travel_times_min", {})

    surcharge_total = 0
    surcharge_items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    parsed_slots: list[tuple[int, int, dict[str, Any], str]] = []

    for idx, step in enumerate(lich, start=1):
        item_id = str(step.get("id", "")).strip().upper()
        if item_id not in catalog:
            vi_pham.append(f"Mục #{idx}: mã '{item_id}' không tồn tại trong dữ liệu công viên.")
            continue
        if item_id in seen_ids:
            vi_pham.append(f"Mục #{idx} ({item_id}): bị lặp lại trong cùng ngày.")
        seen_ids.add(item_id)

        kind, meta = catalog[item_id]
        try:
            s_min = _to_minutes(str(step.get("start", "")))
            e_min = _to_minutes(str(step.get("end", "")))
        except ValueError as err:
            vi_pham.append(f"{item_id}: {err}")
            continue

        if e_min <= s_min:
            vi_pham.append(f"{item_id} ({meta['name']}): giờ kết thúc phải sau giờ bắt đầu.")
        if s_min < win_start or e_min > win_end:
            vi_pham.append(f"{item_id} ({meta['name']}): nằm ngoài khung giờ gia đình ({gio_bat_dau}-{gio_ket_thuc}).")

        if kind == "attraction":
            if item_id in maintenance:
                vi_pham.append(f"{item_id} ({meta['name']}): đang tạm dừng bảo trì trong ngày {ngay}.")
            if s_min < _to_minutes(meta["open"]) or e_min > _to_minutes(meta["close"]):
                vi_pham.append(f"{item_id} ({meta['name']}): ngoài giờ mở cửa ({meta['open']}-{meta['close']}).")
            if e_min - s_min < meta["duration_min"]:
                vi_pham.append(f"{item_id} ({meta['name']}): thời lượng {e_min - s_min}p ngắn hơn tối thiểu {meta['duration_min']}p.")
        else:
            if item_id in cancelled:
                vi_pham.append(f"{item_id} ({meta['name']}): show bị huỷ trong ngày {ngay}.")
            if s_min != _to_minutes(meta["start"]) or e_min != _to_minutes(meta["end"]):
                vi_pham.append(f"{item_id} ({meta['name']}): phải khớp đúng giờ show {meta['start']}-{meta['end']}.")

        if meta["min_age"] > min_age_group:
            vi_pham.append(f"{item_id} ({meta['name']}): yêu cầu từ {meta['min_age']} tuổi, nhóm có bé {min_age_group} tuổi.")
        if min_height_group is not None and meta["min_height_cm"] > min_height_group:
            vi_pham.append(f"{item_id} ({meta['name']}): yêu cầu cao tối thiểu {meta['min_height_cm']}cm (bé cao {min_height_group}cm).")
        if not meta["indoor"] and _is_raining(weather, s_min, e_min):
            vi_pham.append(f"{item_id} ({meta['name']}): điểm ngoài trời không hoạt động khi trời mưa.")

        fee = meta["price_adult"] * so_nguoi_lon + meta["price_child"] * paying_children
        if fee > 0:
            surcharge_total += fee
            surcharge_items.append({"id": item_id, "name": meta["name"], "phi_vnd": fee})

        parsed_slots.append((s_min, e_min, meta, item_id))

    parsed_slots.sort(key=lambda x: x[0])
    for i in range(1, len(parsed_slots)):
        prev_s, prev_e, prev_m, prev_id = parsed_slots[i - 1]
        cur_s, cur_e, cur_m, cur_id = parsed_slots[i]
        travel = matrix.get(prev_m["zone"], {}).get(cur_m["zone"], 15)
        buffer_after = int(prev_m.get("buffer_after_min", 0))
        needed = travel + buffer_after
        if prev_e > cur_s:
            vi_pham.append(f"Chồng giờ giữa {prev_id} (kết thúc {prev_e//60:02d}:{prev_e%60:02d}) và {cur_id} (bắt đầu {cur_s//60:02d}:{cur_s%60:02d}).")
        elif prev_e + needed > cur_s:
            if buffer_after > 0:
                vi_pham.append(
                    f"Thiếu thời gian di chuyển + đệm tắm tráng/thay đồ từ {prev_id} ({prev_m['zone']}) sang {cur_id} ({cur_m['zone']}): "
                    f"cần {needed}p ({travel}p đi bộ + {buffer_after}p đệm), chỉ có {cur_s - prev_e}p."
                )
            else:
                vi_pham.append(
                    f"Thiếu thời gian di chuyển từ {prev_id} ({prev_m['zone']}) sang {cur_id} ({cur_m['zone']}): "
                    f"cần {travel}p, chỉ có {cur_s - prev_e}p."
                )

    tong_tien = entry_total + surcharge_total
    if tong_tien > ngan_sach_vnd:
        thieu = tong_tien - ngan_sach_vnd
        vi_pham.append(f"Vượt ngân sách {thieu:,}đ (tổng {tong_tien:,}đ > ngân sách {ngan_sach_vnd:,}đ).")
        if entry_total > ngan_sach_vnd:
            goi_y.append(f"Ngân sách tối thiểu cho vé cổng nhóm này là {entry_total:,}đ; cần tăng thêm ít nhất {entry_total - ngan_sach_vnd:,}đ.")
        else:
            goi_y.append("Bỏ bớt điểm/show có phụ thu (như Thủy Cung, Show Hải Cẩu hoặc Ăn uống trong công viên) để khớp ngân sách.")

    if not lich and not vi_pham:
        vi_pham.append("Lịch trình đang rỗng.")
    if any("mưa" in v for v in vi_pham):
        goi_y.append("Chuyển các khung giờ mưa sang điểm trong nhà (DC05, DC06, DC07, DC08, DC11, DC12, SH02, SH03).")
    if any("tuổi" in v or "cm" in v for v in vi_pham):
        goi_y.append("Thay các trò cảm giác mạnh bằng điểm phù hợp độ tuổi/chiều cao của bé nhỏ nhất.")
    if any("bảo trì" in v for v in vi_pham):
        goi_y.append("Loại bỏ điểm đang bảo trì và thay bằng điểm hoạt động cùng độ tuổi (vd DC01, DC03, DC05, DC06).")

    return {
        "hop_le": len(vi_pham) == 0,
        "tong_tien_vnd": tong_tien,
        "chi_tiet_chi_phi": {
            "ve_cong": entry_total,
            "phu_thu": surcharge_total,
            "cac_khoan_phu_thu": surcharge_items,
        },
        "vi_pham": vi_pham,
        "goi_y_noi_rang_buoc": goi_y,
    }
