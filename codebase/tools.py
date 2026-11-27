"""Công cụ chỉ đọc cho Track C1 — sử dụng bộ dữ liệu VinWonders Nha Trang (data/park/*.json).

Mỗi công cụ gắn @tool để tracing.py tự ghi lại input, output, độ trễ và lỗi.
Không công cụ nào có tác động ra ngoài (chỉ đọc dữ liệu và kiểm tra ràng buộc bằng code).
"""
from __future__ import annotations

import functools
import json
import os
from typing import Any

from tracing import tool

PARK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "park")
WATERPARK_ZONE, WATERPARK_BUFFER_MIN = "TROPICAL_PARADISE", 20


@functools.lru_cache(maxsize=1)
def _load_park_bundle() -> dict[str, Any]:
    """Đọc và cache toàn bộ 7 file JSON trong data/park/."""
    bundle: dict[str, Any] = {}
    for name in ("park", "attractions", "shows", "tickets", "services", "travel_times", "weather"):
        path = os.path.join(PARK_DIR, f"{name}.json")
        with open(path, encoding="utf-8") as f:
            bundle[name] = json.load(f)
    return bundle


def _to_min(hhmm: str) -> int:
    """Chuyển chuỗi giờ 'HH:MM' thành số phút tính từ 00:00."""
    parts = hhmm.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Định dạng giờ không hợp lệ: {hhmm!r} (cần HH:MM)")
    hour, minute = int(parts[0]), int(parts[1])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Giờ nằm ngoài khoảng 00:00-23:59: {hhmm!r}")
    return hour * 60 + minute


def _add_min(hhmm: str, delta: int) -> str:
    """Cộng thêm số phút vào mốc HH:MM và trả về chuỗi HH:MM."""
    total = _to_min(hhmm) + delta
    return f"{total // 60:02d}:{total % 60:02d}"


def _overlaps_rain(rain_windows: list[dict[str, str]], s_min: int, e_min: int) -> bool:
    """Kiểm tra khoảng [s_min, e_min] có giao với khung giờ mưa nào không."""
    for w in rain_windows:
        ws, we = _to_min(w["from"]), _to_min(w["to"])
        if max(s_min, ws) < min(e_min, we):
            return True
    return False


def _classify_guest(guest: dict[str, Any]) -> str:
    """Phân nhóm vé khách theo đúng group_priority trong tickets.json."""
    tuoi = guest.get("tuoi")
    if tuoi is not None and int(tuoi) >= 60:
        return "SENIOR"
    cao = guest.get("cao_cm")
    if cao is None:
        return "ADULT"
    cao_int = int(cao)
    if cao_int < 100:
        return "INFANT"
    if cao_int < 140:
        return "CHILD"
    return "ADULT"


@tool
def tra_diem_choi(
    khu: str = "",
    chieu_cao_tre_cm: int | None = None,
    tuoi_lon_nhat: int | None = None,
    chi_trong_nha: bool = False,
    bao_gom_bao_tri: bool = False,
) -> dict[str, Any]:
    """Tra điểm chơi từ attractions.json theo khu, chiều cao/tuổi, trong nhà và trạng thái bảo trì.

    Input: khu (str), chieu_cao_tre_cm (int|None), tuoi_lon_nhat (int|None), chi_trong_nha (bool), bao_gom_bao_tri (bool).
    Output: dict gồm thông tin công viên, danh sách điểm chơi lọc được, bảng giá vé và dịch vụ lẻ.
    Tác động ra ngoài: Không (chỉ đọc).
    """
    b = _load_park_bundle()
    khu_up = khu.strip().upper()
    items: list[dict[str, Any]] = []
    for a in b["attractions"]["attractions"]:
        if khu_up and a["zone"].upper() != khu_up:
            continue
        if not bao_gom_bao_tri and a.get("status") == "maintenance":
            continue
        if chi_trong_nha and not a.get("indoor"):
            continue
        if chieu_cao_tre_cm is not None:
            if a["min_height_cm"] is not None and a["min_height_cm"] > chieu_cao_tre_cm:
                continue
            if a["max_height_cm"] is not None and a["max_height_cm"] < chieu_cao_tre_cm:
                continue
        if tuoi_lon_nhat is not None and a["max_age"] is not None and a["max_age"] < tuoi_lon_nhat:
            continue
        items.append(a)
    return {
        "cong_vien": b["park"]["park"]["name"],
        "gio_mo_cua": f"{b['park']['park']['open']}-{b['park']['park']['close']}",
        "tong_so": len(items),
        "diem_choi": items,
        "bang_gia_ve": b["tickets"]["ticket_types"],
        "dich_vu_le": b["services"]["services"],
        "ma_tran_di_chuyen": {"cung_khu_phut": b["travel_times"]["same_zone_min"], "dem_roi_cong_vien_nuoc_phut": WATERPARK_BUFFER_MIN, "khu_cong_vien_nuoc": WATERPARK_ZONE, "giua_cac_khu_phut": b["travel_times"]["minutes"]},
    }


@tool
def tra_lich_show(kich_ban_thoi_tiet: str = "SUNNY", chi_trong_nha: bool = False) -> dict[str, Any]:
    """Tra danh sách show từ shows.json và đánh dấu suất bị huỷ theo kịch bản thời tiết.

    Input: kich_ban_thoi_tiet (str: SUNNY/AFTERNOON_RAIN/EVENING_RAIN/ALL_DAY_RAIN), chi_trong_nha (bool).
    Output: dict gồm kịch bản thời tiết và danh sách show kèm danh sách suất hoạt động / bị huỷ.
    Tác động ra ngoài: Không (chỉ đọc).
    """
    b = _load_park_bundle()
    sc_id = kich_ban_thoi_tiet.strip().upper()
    scenario = next((s for s in b["weather"]["scenarios"] if s["id"] == sc_id), None)
    if scenario is None:
        return {"co_du_lieu": False, "loi": f"Không có kịch bản thời tiết {kich_ban_thoi_tiet!r}.", "shows": []}
    rain_windows = scenario["rain_windows"]
    out: list[dict[str, Any]] = []
    for sh in b["shows"]["shows"]:
        if chi_trong_nha and not sh.get("indoor"):
            continue
        active_times: list[str] = []
        cancelled_times: list[str] = []
        for t in sh["times"]:
            s_m = _to_min(t)
            e_m = s_m + int(sh["duration_min"])
            if sh.get("cancel_in_rain") and _overlaps_rain(rain_windows, s_m, e_m):
                cancelled_times.append(t)
            else:
                active_times.append(t)
        item = dict(sh)
        item["suat_hoat_dong"] = active_times
        item["suat_bi_huy"] = cancelled_times
        out.append(item)
    return {"co_du_lieu": True, "kich_ban": scenario["id"], "mo_ta": scenario["label"], "shows": out}


@tool
def tra_thoi_tiet(kich_ban: str = "SUNNY") -> dict[str, Any]:
    """Tra khung giờ mưa và quy tắc đóng trò/huỷ show từ weather.json.

    Input: kich_ban (str: SUNNY | AFTERNOON_RAIN | EVENING_RAIN | ALL_DAY_RAIN).
    Output: dict gồm trạng thái có dữ liệu, nhãn kịch bản, rain_windows và rain_rules.
    Tác động ra ngoài: Không (chỉ đọc).
    """
    b = _load_park_bundle()
    sc_id = kich_ban.strip().upper()
    scenario = next((s for s in b["weather"]["scenarios"] if s["id"] == sc_id), None)
    if scenario is None:
        return {"co_du_lieu": False, "loi": f"Không có kịch bản thời tiết {kich_ban!r}."}
    return {
        "co_du_lieu": True,
        "id": scenario["id"],
        "nhan": scenario["label"],
        "rain_windows": scenario["rain_windows"],
        "rain_rules": b["weather"]["rain_rules"],
    }


@tool
def uoc_thoi_gian_di(khu_a: str, khu_b: str) -> dict[str, Any]:
    """Tra số phút đi bộ giữa hai khu cho gia đình có trẻ nhỏ từ travel_times.json.

    Input: khu_a (str), khu_b (str).
    Output: dict {hop_le, khu_a, khu_b, phut} (cùng khu trả same_zone_min=5).
    Tác động ra ngoài: Không (chỉ đọc).
    """
    tt = _load_park_bundle()["travel_times"]
    nodes = {n.upper(): n for n in tt["nodes"]}
    za, zb = nodes.get(khu_a.strip().upper()), nodes.get(khu_b.strip().upper())
    if not za or not zb:
        return {"hop_le": False, "phut": 15, "loi": f"Khu không hợp lệ ({khu_a!r}, {khu_b!r})."}
    phut = int(tt["same_zone_min"]) if za == zb else int(tt["minutes"][za][zb])
    return {"hop_le": True, "khu_a": za, "khu_b": zb, "phut": phut}


def _calc_ticket_cost(tickets_data: dict[str, Any], loai_ve: str, nhom_khach: list[dict[str, Any]]) -> tuple[int, dict[str, int], str | None]:
    """Tính tiền vé cổng theo nhóm chiều cao/tuổi từ tickets.json."""
    t_info = next((t for t in tickets_data["ticket_types"] if t["id"] == loai_ve), None)
    if t_info is None:
        return 0, {}, f"Không có loại vé {loai_ve!r} trong dữ liệu."
    counts: dict[str, int] = {"ADULT": 0, "CHILD": 0, "SENIOR": 0, "INFANT": 0}
    total = 0
    for guest in nhom_khach:
        grp = _classify_guest(guest)
        counts[grp] += 1
        total += int(t_info["price_vnd"][grp])
    return total, counts, t_info["entry_from"]


@tool
def kiem_lich_trinh(
    lich: list[dict[str, Any]],
    ngan_sach_vnd: int,
    nhom_khach: list[dict[str, Any]],
    kich_ban_thoi_tiet: str = "SUNNY",
    loai_ve: str = "STANDARD",
    gio_bat_dau: str = "09:00",
    gio_ket_thuc: str = "20:00",
    dich_vu_le: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Kiểm tra toàn bộ ràng buộc lịch trình (giờ, di chuyển, đệm CVN, bảo trì, chiều cao/tuổi, mưa, tiền) bằng code.

    Input: lich (list[{id, start, end}]), ngan_sach_vnd (int), nhom_khach (list[{tuoi, cao_cm}]),
           kich_ban_thoi_tiet (str), loai_ve (str), gio_bat_dau (str), gio_ket_thuc (str), dich_vu_le (list|None).
    Output: dict {hop_le, tong_tien_vnd, chi_tiet_chi_phi, muc_khong_co_gia, vi_pham, goi_y_noi_rang_buoc}.
    Tác động ra ngoài: Không (chỉ đọc và tính toán).
    """
    b = _load_park_bundle()
    vi_pham: list[str] = []
    goi_y: list[str] = []
    khong_co_gia: list[str] = []

    ve_cong, dem_nhom, entry_from = _calc_ticket_cost(b["tickets"], loai_ve, nhom_khach)
    if entry_from is None:
        return {"hop_le": False, "tong_tien_vnd": 0, "chi_tiet_chi_phi": {}, "muc_khong_co_gia": [], "vi_pham": [f"Loại vé {loai_ve!r} không tồn tại."], "goi_y_noi_rang_buoc": []}
    if dem_nhom.get("ADULT", 0) + dem_nhom.get("SENIOR", 0) == 0:
        vi_pham.append("Phải có ít nhất 1 người lớn/người cao tuổi đi cùng trẻ nhỏ.")

    scenario = next((s for s in b["weather"]["scenarios"] if s["id"] == kich_ban_thoi_tiet.strip().upper()), None)
    if scenario is None:
        vi_pham.append(f"Không có kịch bản thời tiết {kich_ban_thoi_tiet!r}.")
        return {"hop_le": False, "tong_tien_vnd": ve_cong, "chi_tiet_chi_phi": {"ve_cong": ve_cong, "phu_thu": 0, "dem_nhom": dem_nhom}, "muc_khong_co_gia": [], "vi_pham": vi_pham, "goi_y_noi_rang_buoc": []}

    catalog = {a["id"]: ("attraction", a) for a in b["attractions"]["attractions"]}
    for sh in b["shows"]["shows"]:
        catalog[sh["id"]] = ("show", sh)
    sv_map = {s["id"]: s for s in b["services"]["services"]}

    win_s = max(_to_min(gio_bat_dau), _to_min(entry_from), _to_min(b["park"]["park"]["open"]))
    win_e = min(_to_min(gio_ket_thuc), _to_min(b["park"]["park"]["close"]))
    heights = [int(g["cao_cm"]) for g in nhom_khach if g.get("cao_cm") is not None]
    child_heights = [int(g["cao_cm"]) for g in nhom_khach if g.get("cao_cm") is not None and int(g.get("tuoi", 30)) < 18]
    ages = [int(g["tuoi"]) for g in nhom_khach if g.get("tuoi") is not None]
    min_h = min(heights) if heights else None
    max_age = max(ages) if ages else None

    seen_ids: set[str] = set()
    slots: list[tuple[int, int, dict[str, Any], str]] = []
    rain_windows = scenario["rain_windows"]

    for idx, step in enumerate(lich, start=1):
        item_id = str(step.get("id", "")).strip().upper()
        if item_id not in catalog:
            vi_pham.append(f"Mục #{idx}: mã '{item_id}' không tồn tại trong dữ liệu VinWonders Nha Trang.")
            continue
        if item_id in seen_ids:
            vi_pham.append(f"Mục #{idx} ({item_id}): bị lặp lại trong lịch trình.")
        seen_ids.add(item_id)
        kind, meta = catalog[item_id]
        try:
            s_m, e_m = _to_min(str(step.get("start", ""))), _to_min(str(step.get("end", "")))
        except ValueError as err:
            vi_pham.append(f"{item_id}: {err}")
            continue
        if e_m <= s_m:
            vi_pham.append(f"{item_id} ({meta['name']}): giờ kết thúc phải sau giờ bắt đầu.")
        if s_m < win_s or e_m > win_e:
            vi_pham.append(f"{item_id} ({meta['name']}): ngoài khung giờ hợp lệ ({_add_min('00:00', win_s)}-{_add_min('00:00', win_e)}).")

        if kind == "attraction":
            if meta.get("status") == "maintenance":
                vi_pham.append(f"{item_id} ({meta['name']}): đang tạm đóng bảo trì.")
            if s_m < _to_min(meta["open"]) or e_m > _to_min(meta["close"]):
                vi_pham.append(f"{item_id} ({meta['name']}): ngoài giờ hoạt động ({meta['open']}-{meta['close']}).")
            if e_m - s_m < int(meta["duration_min"]):
                vi_pham.append(f"{item_id} ({meta['name']}): thời lượng {e_m - s_m}p < tối thiểu {meta['duration_min']}p.")
            if not meta.get("included_in_ticket", True) and meta.get("extra_fee_vnd") is None:
                khong_co_gia.append(f"{item_id} ({meta['name']}): không gồm trong vé và không có giá lẻ công khai")
                vi_pham.append(f"{item_id} ({meta['name']}): chưa có giá lẻ công khai, không thể tính tổng chi phí chính xác.")
            if meta.get("closes_in_rain") and _overlaps_rain(rain_windows, s_m, e_m):
                vi_pham.append(f"{item_id} ({meta['name']}): tạm đóng trong khung giờ mưa.")
        else:
            valid_slots = [(_to_min(t), _to_min(t) + int(meta["duration_min"])) for t in meta["times"]]
            if (s_m, e_m) not in valid_slots:
                vi_pham.append(f"{item_id} ({meta['name']}): không khớp suất diễn {meta['times']} ({meta['duration_min']}p).")
            if meta.get("cancel_in_rain") and _overlaps_rain(rain_windows, s_m, e_m):
                vi_pham.append(f"{item_id} ({meta['name']}): show bị huỷ do mưa.")

        if min_h is not None and meta.get("min_height_cm") is not None and min_h < int(meta["min_height_cm"]):
            vi_pham.append(f"{item_id} ({meta['name']}): yêu cầu cao tối thiểu {meta['min_height_cm']}cm (nhóm có người cao {min_h}cm).")
        if child_heights and meta.get("max_height_cm") is not None and all(h > int(meta["max_height_cm"]) for h in child_heights):
            vi_pham.append(f"{item_id} ({meta['name']}): chỉ dành cho trẻ cao tối đa {meta['max_height_cm']}cm.")
        if max_age is not None and meta.get("max_age") is not None and max_age > int(meta["max_age"]):
            vi_pham.append(f"{item_id} ({meta['name']}): giới hạn tối đa {meta['max_age']} tuổi (nhóm có người {max_age} tuổi).")
        slots.append((s_m, e_m, meta, item_id))

    slots.sort(key=lambda x: x[0])
    tt = b["travel_times"]
    for i in range(1, len(slots)):
        _, prev_e, prev_m, prev_id = slots[i - 1]
        cur_s, _, cur_m, cur_id = slots[i]
        za, zb = prev_m["zone"], cur_m["zone"]
        travel = int(tt["same_zone_min"]) if za == zb else int(tt["minutes"][za][zb])
        buffer_min = WATERPARK_BUFFER_MIN if (za == WATERPARK_ZONE and zb != WATERPARK_ZONE) else 0
        needed = travel + buffer_min
        if prev_e > cur_s:
            vi_pham.append(f"Chồng giờ giữa {prev_id} và {cur_id}.")
        elif prev_e + needed > cur_s:
            msg = f"Thiếu thời gian di chuyển từ {prev_id} ({za}) sang {cur_id} ({zb}): cần {needed}p"
            if buffer_min > 0:
                msg += f" ({travel}p đi bộ + {buffer_min}p đệm tắm tráng/thay đồ công viên nước)"
            vi_pham.append(msg + f", chỉ có {cur_s - prev_e}p.")

    phu_thu = 0
    for sv in (dich_vu_le or []):
        sv_id = str(sv.get("id", "")).strip().upper()
        qty = int(sv.get("so_luong", 1))
        sv_meta = sv_map.get(sv_id)
        if not sv_meta:
            vi_pham.append(f"Dịch vụ {sv_id} không có trong dữ liệu.")
        elif sv_meta["price_vnd"] is None:
            khong_co_gia.append(f"{sv_id} ({sv_meta['name']}): không có giá lẻ công khai")
            vi_pham.append(f"{sv_id} ({sv_meta['name']}): không có giá lẻ công khai, không thể cộng vào tổng tiền.")
        else:
            phu_thu += int(sv_meta["price_vnd"]) * qty

    tong_tien = ve_cong + phu_thu
    if tong_tien > ngan_sach_vnd:
        vi_pham.append(f"Vượt ngân sách {tong_tien - ngan_sach_vnd:,}đ (tổng {tong_tien:,}đ > {ngan_sach_vnd:,}đ).")
        if ve_cong > ngan_sach_vnd:
            goi_y.append(f"Vé cổng {loai_ve} tối thiểu cho nhóm là {ve_cong:,}đ; có thể cân nhắc vé AFTER_16H hoặc tăng ngân sách thêm {ve_cong - ngan_sach_vnd:,}đ.")
        else:
            goi_y.append("Giảm bớt dịch vụ phát sinh ngoài vé để tổng chi phí khớp ngân sách.")
    if any("bảo trì" in v for v in vi_pham):
        goi_y.append("Thay trò đang bảo trì (A16, A17) bằng trò đang mở phù hợp chiều cao (vd A03, A08, A12, A13).")
    if any("mưa" in v for v in vi_pham):
        goi_y.append("Chuyển các mục ngoài trời trong khung giờ mưa sang điểm trong nhà (A03, A08, A10, A13, S02, S03, S06).")

    return {
        "hop_le": len(vi_pham) == 0,
        "tong_tien_vnd": tong_tien,
        "chi_tiet_chi_phi": {"loai_ve": loai_ve, "ve_cong": ve_cong, "phu_thu": phu_thu, "dem_nhom": dem_nhom},
        "muc_khong_co_gia": khong_co_gia,
        "vi_pham": vi_pham,
        "goi_y_noi_rang_buoc": goi_y,
    }
