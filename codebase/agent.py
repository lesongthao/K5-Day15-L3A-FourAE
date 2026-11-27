"""Luồng chính bản chạy thử Track C1: Workflow Plan -> Verify (code) -> Repair.

Sử dụng dữ liệu VinWonders Nha Trang (data/park/*.json).
Hợp đồng: answer(text: str) -> {"output": str}.
"""
from __future__ import annotations

import json
import re
from typing import Any

from ai import call_model
from request_parser import check_safety, parse_request
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
    "CHỈ dùng mã trò (A01-A18), show (S01-S06), giờ mở cửa, suat_hoat_dong và dữ liệu trong CĂN CỨ.\n"
    "1) Chi phí vé và dịch vụ có giá đã được code tính và xác nhận đủ ngân sách tại chi_phi_code_da_tinh — KHÔNG tự báo thiếu giá vé hay từ chối vì giá.\n"
    "2) Ưu tiên xếp đủ các điểm chơi và show hợp lệ khách yêu cầu; chọn tổng cộng 3–7 điểm hợp lý, không nhồi điểm phụ gây trễ giờ.\n"
    "3) Nếu khách nhắc mục bảo trì (status=maintenance), quá tuổi/chiều cao, chưa có giá lẻ (price_vnd=null) hoặc show bị huỷ do mưa: loại khỏi items, vẫn lập lịch thay thế hợp lệ và giải thích rõ từng mục đó trong \"ghi_chu\".\n"
    "4) Tuân thủ nghiêm di_chuyen_va_dem (cùng khu >=5p; khác khu theo giua_cac_khu_phut; rời TROPICAL_PARADISE sang khu khác cộng thêm 20p đệm) và đúng giờ suat_hoat_dong.\n"
    "5) CHỈ đặt \"khong_xep_duoc\": true khi yêu cầu bắt buộc bất khả thi (điểm không tồn tại trong dữ liệu hoặc các điểm khách bắt buộc trực tiếp xung đột giờ/di chuyển), kèm giải thích số phút từ di_chuyen_va_dem trong \"goi_y\".\n"
    "CHỈ trả về 1 JSON hợp lệ: "
    '{"items": [{"id": "A08", "start": "09:15", "end": "10:15", "ly_do": "..."}], '
    '"khong_xep_duoc": false, "ghi_chu": ["..."], "goi_y": ["..."]}'
)


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


def _format_success(
    items: list[dict[str, Any]],
    check_res: dict[str, Any],
    catalog: dict[str, dict[str, Any]],
    weather: dict[str, Any],
    is_mock: bool,
    notes: list[str] | None = None,
) -> str:
    """Định dạng lịch trình từng khung giờ kèm chi phí tính bằng code."""
    head = "[CHẾ ĐỘ KHUNG / AI GIẢ — chưa nối model thật]" if is_mock else "LỊCH TRÌNH ĐỀ XUẤT (VinWonders Nha Trang — đã kiểm bằng code):"
    lines = [head, f"- Kịch bản thời tiết ({weather['id']}): {weather['nhan']}"]
    for it in items:
        meta = catalog.get(it["id"], {})
        loai = "Trong nhà" if meta.get("indoor") else "Ngoài trời"
        lines.append(f"• {it['start']}–{it['end']} | [{it['id']}] {meta.get('name', it['id'])} ({meta.get('zone', '')}, {loai}) — {it.get('ly_do', '')}")
    clean_notes = [str(n).strip() for n in (notes or []) if str(n).strip()]
    if clean_notes:
        lines.append("- Ghi chú thêm: " + " | ".join(clean_notes))
    cost = check_res["chi_tiet_chi_phi"]
    lines.append(f"- Tổng chi phí (tính bằng code, vé {cost['loai_ve']}): {check_res['tong_tien_vnd']:,}đ (Vé cổng: {cost['ve_cong']:,}đ · Dịch vụ lẻ: {cost['phu_thu']:,}đ).")
    lines.append("- Lưu ý: Lịch trình mang tính gợi ý chờ phụ huynh duyệt và tự đặt vé; lịch show là dữ liệu mẫu tham khảo.")
    return "\n".join(lines)


def _build_context(parsed: dict[str, Any], pre: dict[str, Any], weather: dict[str, Any], attrs: dict[str, Any], shows: dict[str, Any]) -> str:
    """Tạo ngữ cảnh gọn nhưng đủ căn cứ giá vé, dịch vụ, bảo trì và ma trận di chuyển cho model."""
    all_attrs = tra_diem_choi(bao_gom_bao_tri=True)
    blocked_or_extra = [
        {"id": a["id"], "name": a["name"], "zone": a["zone"], "status": a.get("status"),
         "min_height_cm": a.get("min_height_cm"), "extra_fee_vnd": a.get("extra_fee_vnd"), "caveat": a.get("caveat", "")}
        for a in all_attrs["diem_choi"]
        if a.get("status") == "maintenance" or not a.get("included_in_ticket", True)
    ]
    compact_attrs = [
        {k: a[k] for k in ("id", "name", "zone", "open", "close", "duration_min", "indoor", "closes_in_rain", "min_height_cm", "max_height_cm", "max_age", "caveat") if a.get(k) is not None}
        for a in attrs["diem_choi"] if a.get("included_in_ticket", True)
    ]
    compact_shows = [
        {k: s[k] for k in ("id", "name", "zone", "duration_min", "indoor", "suat_hoat_dong", "suat_bi_huy")}
        for s in shows["shows"]
    ]
    cost = pre["chi_tiet_chi_phi"]
    return json.dumps({
        "yeu_cau": parsed,
        "chi_phi_code_da_tinh": {
            "loai_ve": cost["loai_ve"], "ve_cong": cost["ve_cong"], "phu_thu": cost["phu_thu"],
            "tong_tien_vnd": pre["tong_tien_vnd"], "ngan_sach_vnd": parsed["ngan_sach_vnd"], "du_ngan_sach": True,
        },
        "dich_vu_le_bang_gia": [{"id": s["id"], "name": s["name"], "price_vnd": s["price_vnd"], "price_note": s.get("price_note", "")} for s in attrs["dich_vu_le"]],
        "diem_bao_tri_va_ngoai_ve": blocked_or_extra,
        "di_chuyen_va_dem": attrs["ma_tran_di_chuyen"],
        "thoi_tiet": weather,
        "diem_choi": compact_attrs,
        "shows": compact_shows,
    }, ensure_ascii=False)


def answer(text: str) -> dict[str, str]:
    """Điểm vào chuẩn cho run.py, eval và simulate."""
    blocked = check_safety(text)
    if blocked:
        return {"output": blocked}

    parsed = parse_request(text)
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
    if pre["tong_tien_vnd"] > parsed["ngan_sach_vnd"]:
        cost = pre["chi_tiet_chi_phi"]
        vuot = pre["tong_tien_vnd"] - parsed["ngan_sach_vnd"]
        note("dung: ngan sach thap hon tong chi phi toi thieu")
        return {
            "output": (
                f"Không thể xếp lịch vì ngân sách {parsed['ngan_sach_vnd']:,}đ thấp hơn tổng chi phí tối thiểu "
                f"{pre['tong_tien_vnd']:,}đ (Vé cổng: {cost['ve_cong']:,}đ · Dịch vụ lẻ: {cost['phu_thu']:,}đ; "
                f"vượt {vuot:,}đ).\nGợi ý: " + "; ".join(pre["goi_y_noi_rang_buoc"])
            )
        }

    context = _build_context(parsed, pre, weather, attrs, shows)
    prompt = f"Căn cứ dữ liệu công cụ:\n{context}\n\nYêu cầu người dùng:\n{text}"
    items: list[dict[str, Any]] = []
    notes: list[str] = []
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
        notes = data_json.get("ghi_chu", []) if isinstance(data_json.get("ghi_chu"), list) else []
        check_res = kiem_lich_trinh(items, parsed["ngan_sach_vnd"], parsed["nhom_khach"], parsed["kich_ban"], parsed["loai_ve"], parsed["gio_bat_dau"], parsed["gio_ket_thuc"], parsed["dich_vu_le"])
        if check_res["hop_le"]:
            note(f"dung: lich hop le tai vong {round_idx + 1}")
            break
        prompt = (
            "Lịch vừa tạo có vi phạm:\n" + "\n".join("- " + v for v in check_res["vi_pham"])
            + f"\nHãy sửa lại giờ hoặc bỏ bớt điểm bạn tự thêm gây vi phạm, vẫn giữ đủ điểm hợp lệ khách mong muốn; "
            f"KHÔNG đặt khong_xep_duoc=true nếu vẫn xếp được lịch hợp lệ.\nYêu cầu gốc: {text}\nDữ liệu gốc:\n{context}"
        )

    if not check_res.get("hop_le"):
        note("dung: het vong sua van con vi pham")
        return {
            "output": (
                "Không xếp được lịch trình thỏa mãn toàn bộ ràng buộc.\nLý do:\n- "
                + "\n- ".join(check_res.get("vi_pham", ["Chưa tạo được lịch hợp lệ"]))
                + "\nGợi ý nới ràng buộc: " + "; ".join(check_res.get("goi_y_noi_rang_buoc", []))
            )
        }
    return {"output": _format_success(items, check_res, catalog, weather, is_mock, notes)}
