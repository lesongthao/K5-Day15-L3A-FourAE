"""Luồng chính bản chạy thử Track C1: Workflow Plan -> Verify (code) -> Repair.

Sử dụng dữ liệu VinWonders Nha Trang (data/park/*.json).
Hợp đồng: answer(text: str) -> {"output": str}.
"""
from __future__ import annotations

import json
import re
from typing import Any

from ai import call_model
from tools import (
    WATERPARK_BUFFER_MIN,
    WATERPARK_ZONE,
    kiem_lich_trinh,
    tra_diem_choi,
    tra_lich_show,
    tra_thoi_tiet,
    uoc_thoi_gian_di,
)
from tracing import note

MAX_REPAIR_ROUNDS = 2
SYSTEM = (
    "Bạn là trợ lý lập lịch trình 1 ngày tại VinWonders Nha Trang cho gia đình.\n"
    "CHỈ dùng các mã trò chơi (A01-A18), show (S01-S06), giờ mở cửa, giờ suất diễn và giá vé trong CĂN CỨ.\n"
    "KHÔNG tự bịa giá cho mục không có giá công khai (Zipline, Buggy, Combo/Buffet), KHÔNG chọn trò bảo trì (maintenance).\n"
    "CHỈ trả về đúng 1 khối JSON hợp lệ dạng:\n"
    '{"items": [{"id": "A08", "start": "09:15", "end": "10:15", "ly_do": "..."}], '
    '"khong_xep_duoc": false, "goi_y": ["..."]}'
)


def _check_safety(text: str) -> str | None:
    """Chặn yêu cầu ngoài phạm vi, xin thẻ/OTP/CCCD và 2 kịch bản tấn công ở spec.md §5."""
    low = text.lower()
    if any(k in low for k in ("số thẻ", "cvv", "otp", "cccd", "mật khẩu", "chuyển khoản", "thanh toán giúp", "đặt vé luôn", "xuất vé", "đặt vé hộ")):
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


def _extract_budget(text: str) -> int | None:
    """Trích xuất ngân sách (VNĐ) từ câu tiếng Việt tự nhiên."""
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


def _extract_heights(text: str) -> list[int]:
    """Trích xuất chiều cao (cm) từ các dạng '115cm', '1m15', '1m2'."""
    low = text.lower()
    heights = [int(h) for h in re.findall(r"(\d{2,3})\s*cm", low)]
    for m in re.finditer(r"\b(\d)m(\d{1,2})\b", low):
        cm = int(m.group(1)) * 100 + int(m.group(2).ljust(2, "0"))
        heights.append(cm)
    return heights


def _parse_request(text: str) -> dict[str, Any]:
    """Trích xuất thành phần đoàn khách, khung giờ, loại vé, thời tiết và dịch vụ lẻ."""
    low = text.lower()
    m_adults = re.search(r"(\d+)\s*(?:người lớn|nguoi lon|bố mẹ|ba mẹ|phụ huynh)", low)
    adults = int(m_adults.group(1)) if m_adults else (2 if ("gia đình" in low or "vợ chồng" in low) else None)
    m_seniors = re.search(r"(\d+)\s*(?:người cao tuổi|ông bà|cụ|người già)", low)
    seniors = int(m_seniors.group(1)) if m_seniors else 0
    senior_ages = [int(a) for a in re.findall(r"(?:ông|bà|cụ|người cao tuổi)[^\d]{0,12}(\d{2})\s*tuổi", low)]
    if senior_ages and seniors == 0:
        seniors = len(senior_ages)

    child_heights = _extract_heights(text)
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
        t = child_ages[idx] if idx < len(child_ages) else 6
        nhom_khach.append({"tuoi": t, "cao_cm": h})

    return {
        "ngan_sach_vnd": _extract_budget(text),
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


def _to_m(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _fmt_m(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _build_fallback_schedule(
    parsed: dict[str, Any],
    attrs: list[dict[str, Any]],
    shows: list[dict[str, Any]],
    weather: dict[str, Any],
) -> list[dict[str, Any]]:
    """Dựng 1 lịch khung hợp lệ từ data/park/*.json khi chạy chế độ fake (chưa nối model thật)."""
    cur = _to_m(parsed["gio_bat_dau"])
    end_lim = _to_m(parsed["gio_ket_thuc"])
    rain_windows = weather.get("rain_windows", [])
    candidates: list[tuple[str, dict[str, Any]]] = [("show", s) for s in shows if s.get("suat_hoat_dong")]
    open_attrs = [a for a in attrs if a.get("status") == "open" and a.get("included_in_ticket", True)]
    candidates += [("attr", a) for a in sorted(open_attrs, key=lambda x: (-int(x.get("indoor", False)), -int(x["duration_min"])))]

    chosen: list[dict[str, Any]] = []
    prev_zone = "GATE"
    for kind, item in candidates:
        if len(chosen) >= 4:
            break
        travel = uoc_thoi_gian_di(prev_zone, item["zone"])["phut"]
        buf = WATERPARK_BUFFER_MIN if (prev_zone == WATERPARK_ZONE and item["zone"] != WATERPARK_ZONE) else 0
        earliest = cur + travel + buf
        if kind == "show":
            picked = next(
                (t for t in item["suat_hoat_dong"] if _to_m(t) >= earliest and _to_m(t) + int(item["duration_min"]) <= end_lim),
                None,
            )
            if not picked:
                continue
            s_m, e_m = _to_m(picked), _to_m(picked) + int(item["duration_min"])
        else:
            s_m = max(earliest, _to_m(item["open"]))
            e_m = s_m + int(item["duration_min"])
            if e_m > min(end_lim, _to_m(item["close"])):
                continue
            if item.get("closes_in_rain") and any(max(s_m, _to_m(w["from"])) < min(e_m, _to_m(w["to"])) for w in rain_windows):
                continue
        ly_do = item.get("caveat") or f"Phù hợp chiều cao/độ tuổi tại khu {item['zone']}."
        chosen.append({"id": item["id"], "start": _fmt_m(s_m), "end": _fmt_m(e_m), "ly_do": ly_do})
        cur, prev_zone = e_m, item["zone"]
    return chosen


def _parse_json_reply(raw: str) -> dict[str, Any] | None:
    """Tách JSON từ phản hồi của model (chịu được markdown code fence)."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
    m = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def _format_success(items: list[dict[str, Any]], check_res: dict[str, Any], catalog: dict[str, dict[str, Any]], weather: dict[str, Any], is_mock: bool) -> str:
    """Định dạng lịch trình từng khung giờ kèm chi phí tính bằng code."""
    head = "[CHẾ ĐỘ KHUNG / AI GIẢ — chưa nối model thật]" if is_mock else "LỊCH TRÌNH ĐỀ XUẤT (VinWonders Nha Trang — đã kiểm bằng code):"
    lines = [head, f"- Kịch bản thời tiết ({weather['id']}): {weather['nhan']}"]
    for it in items:
        meta = catalog.get(it["id"], {})
        loai = "Trong nhà" if meta.get("indoor") else "Ngoài trời"
        lines.append(f"• {it['start']}–{it['end']} | [{it['id']}] {meta.get('name', it['id'])} ({meta.get('zone', '')}, {loai}) — {it.get('ly_do', '')}")
    cost = check_res["chi_tiet_chi_phi"]
    lines.append(f"- Tổng chi phí (tính bằng code, vé {cost['loai_ve']}): {check_res['tong_tien_vnd']:,}đ (Vé cổng: {cost['ve_cong']:,}đ · Dịch vụ lẻ: {cost['phu_thu']:,}đ).")
    lines.append("- Lưu ý: Lịch trình mang tính gợi ý chờ phụ huynh duyệt và tự đặt vé; lịch show là dữ liệu mẫu tham khảo.")
    return "\n".join(lines)


def answer(text: str) -> dict[str, str]:
    """Điểm vào chuẩn cho run.py, eval và simulate."""
    blocked = _check_safety(text)
    if blocked:
        return {"output": blocked}

    parsed = _parse_request(text)
    if parsed["asks_unpriced"] and parsed["ngan_sach_vnd"] is None:
        tra_diem_choi(bao_gom_bao_tri=True)
        note("dung: muc khong co gia cong khai (lop 1)")
        return {
            "output": (
                "Trong dữ liệu hiện tại, các gói combo (buffet, Wonder15, VIP), vé xe điện buggy lẻ (SV02) "
                "và giá lẻ Zipline (A01/SV05) không có dữ liệu giá công khai nên hệ thống không tự đoán giá. "
                "Phụ huynh vui lòng kiểm tra trực tiếp trên trang VinWonders hoặc nhập ngân sách/nhóm khách để xếp lịch với vé tiêu chuẩn."
            )
        }

    missing: list[str] = []
    if parsed["ngan_sach_vnd"] is None:
        missing.append("ngân sách tối đa (VNĐ)")
    if parsed["adults"] is None:
        missing.append("số người lớn")
    if parsed["has_child_mention"] and not parsed["child_heights"]:
        missing.append("chiều cao của bé (cm, để áp dụng đúng hạng vé <100cm/100–140cm và an toàn trò chơi)")
    if missing:
        note("hoi_lai: thieu " + ", ".join(missing))
        return {
            "output": (
                f"Để xếp lịch chính xác và đúng hạng vé VinWonders Nha Trang, vui lòng bổ sung: {', '.join(missing)}. "
                "Ví dụ: '2 người lớn, 1 bé cao 115cm, ngân sách 3.5 triệu, đi từ 09:00 đến 18:00'."
            )
        }

    weather = tra_thoi_tiet(parsed["kich_ban"])
    min_child_h = min(parsed["child_heights"]) if parsed["child_heights"] else None
    max_age = max((g.get("tuoi", 30) for g in parsed["nhom_khach"]), default=None)
    attrs = tra_diem_choi(chieu_cao_tre_cm=min_child_h, tuoi_lon_nhat=max_age, chi_trong_nha=parsed["chi_trong_nha"])
    shows = tra_lich_show(kich_ban_thoi_tiet=parsed["kich_ban"], chi_trong_nha=parsed["chi_trong_nha"])
    catalog = {a["id"]: a for a in attrs["diem_choi"]} | {s["id"]: s for s in shows["shows"]}

    pre = kiem_lich_trinh([], parsed["ngan_sach_vnd"], parsed["nhom_khach"], parsed["kich_ban"], parsed["loai_ve"], parsed["gio_bat_dau"], parsed["gio_ket_thuc"], parsed["dich_vu_le"])
    if pre["chi_tiet_chi_phi"].get("ve_cong", 0) > parsed["ngan_sach_vnd"]:
        note("dung: ngan sach thap hon ve cong toi thieu")
        return {
            "output": (
                f"Không thể xếp lịch vì ngân sách {parsed['ngan_sach_vnd']:,}đ thấp hơn tiền vé cổng tối thiểu "
                f"({pre['chi_tiet_chi_phi']['ve_cong']:,}đ).\nGợi ý: " + "; ".join(pre["goi_y_noi_rang_buoc"])
            )
        }

    context = json.dumps({"yeu_cau": parsed, "thoi_tiet": weather, "diem_choi": attrs["diem_choi"], "shows": shows["shows"]}, ensure_ascii=False)
    prompt = f"Căn cứ dữ liệu công cụ:\n{context}\n\nYêu cầu người dùng:\n{text}"
    items: list[dict[str, Any]] = []
    check_res: dict[str, Any] = {"hop_le": False, "vi_pham": [], "goi_y_noi_rang_buoc": []}
    is_mock = False

    for round_idx in range(1 + MAX_REPAIR_ROUNDS):
        reply = call_model(SYSTEM, prompt)
        if reply["model"] == "fake":
            is_mock = True
            items = _build_fallback_schedule(parsed, attrs["diem_choi"], shows["shows"], weather)
            check_res = kiem_lich_trinh(items, parsed["ngan_sach_vnd"], parsed["nhom_khach"], parsed["kich_ban"], parsed["loai_ve"], parsed["gio_bat_dau"], parsed["gio_ket_thuc"], parsed["dich_vu_le"])
            note("dung: che do khung fake")
            break
        data_json = _parse_json_reply(reply["text"])
        if not data_json:
            prompt = f"Đầu ra vừa rồi không đúng JSON. Hãy chỉ trả về JSON hợp lệ.\n{prompt}"
            continue
        if data_json.get("khong_xep_duoc"):
            note("dung: model bao khong xep duoc")
            return {"output": "Không xếp được lịch trình phù hợp.\nGợi ý: " + "; ".join(data_json.get("goi_y", []))}
        items = data_json.get("items", [])
        check_res = kiem_lich_trinh(items, parsed["ngan_sach_vnd"], parsed["nhom_khach"], parsed["kich_ban"], parsed["loai_ve"], parsed["gio_bat_dau"], parsed["gio_ket_thuc"], parsed["dich_vu_le"])
        if check_res["hop_le"]:
            note(f"dung: lich hop le tai vong {round_idx + 1}")
            break
        prompt = "Lịch vừa tạo có vi phạm:\n" + "\n".join("- " + v for v in check_res["vi_pham"]) + f"\nHãy sửa lại JSON.\nDữ liệu gốc:\n{context}"

    if not check_res.get("hop_le"):
        note("dung: het vong sua van con vi pham")
        return {
            "output": (
                "Không xếp được lịch trình thỏa mãn toàn bộ ràng buộc.\nLý do:\n- "
                + "\n- ".join(check_res.get("vi_pham", ["Chưa tạo được lịch hợp lệ"]))
                + "\nGợi ý nới ràng buộc: " + "; ".join(check_res.get("goi_y_noi_rang_buoc", []))
            )
        }
    return {"output": _format_success(items, check_res, catalog, weather, is_mock)}
