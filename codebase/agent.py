"""Luồng chính bản chạy thử Track C1: Workflow Plan -> Verify (code) -> Repair.

Hợp đồng: answer(text: str) -> {"output": str}.
Chỉ gợi ý lịch trình đọc từ data/park_data.json; không tự đặt vé, không thu thẻ/OTP.
"""
from __future__ import annotations

import json
import re
from typing import Any

from ai import call_model
from tools import kiem_lich_trinh, tra_diem_choi, tra_lich_show, tra_thoi_tiet, uoc_thoi_gian_di
from tracing import note

MAX_REPAIR_ROUNDS = 2
SYSTEM = (
    "Bạn là trợ lý lập lịch trình 1 ngày tại Khu vui chơi Mẫu WonderPark cho gia đình có trẻ nhỏ.\n"
    "CHỈ dùng các mã điểm chơi/show, giờ mở cửa, giờ show và giá vé có trong CĂN CỨ được cung cấp.\n"
    "KHÔNG tự bịa điểm mới, KHÔNG bỏ qua giới hạn tuổi/chiều cao, thời tiết mưa hoặc ngân sách.\n"
    "CHỈ trả về đúng 1 khối JSON hợp lệ dạng:\n"
    '{"items": [{"id": "DC01", "start": "09:00", "end": "10:00", "ly_do": "..."}], '
    '"khong_xep_duoc": false, "goi_y": ["..."]}'
)


def _check_safety(text: str) -> str | None:
    """Chặn yêu cầu ngoài phạm vi, xin thông tin nhạy cảm hoặc giả mạo bỏ qua quy định an toàn."""
    low = text.lower()
    if any(k in low for k in ("số thẻ", "cvv", "otp", "cccd", "mật khẩu", "chuyển khoản", "thanh toán giúp", "đặt vé luôn", "xuất vé", "đặt vé hộ")):
        note("tu_choi: ngoai pham vi thanh toan / du lieu nhay cam")
        return (
            "Xin lỗi, trợ lý chỉ hỗ trợ gợi ý lịch trình tham quan dựa trên dữ liệu khu vui chơi; "
            "không hỗ trợ đặt vé, thanh toán hay nhận số thẻ/OTP/CCCD. "
            "Sau khi chốt lịch trình, phụ huynh vui lòng kiểm tra lại và tự đặt vé trên kênh chính thức."
        )
    if any(k in low for k in (
        "bỏ qua giới hạn", "kệ quy định", "cho bé vào luôn", "lách quy định", "quản lý yêu cầu",
        "nhân viên hãng", "ignore all", "bỏ qua hướng dẫn", "đặt giá vé 0", "giá vé 0đ", "mở lại trò bảo trì",
    )):
        note("tu_choi: tan cong vuot quyen / bo qua an toan tre nho")
        return (
            "Không thể đáp ứng yêu cầu ghi đè dữ liệu hệ thống, thay đổi giá vé hay bỏ qua giới hạn độ tuổi/chiều cao hoặc quy định bảo trì. "
            "Mọi trò chơi đều bắt buộc tuân thủ quy định tại cổng để đảm bảo an toàn cho trẻ nhỏ."
        )
    if any(k in low for k in ("đặt phòng", "nâng hạng phòng", "hoàn vé máy bay", "đổi chuyến bay", "khách sạn")):
        note("tu_choi: ngoai pham vi C1")
        return "Trợ lý hiện chỉ hỗ trợ lập lịch trình vui chơi 1 ngày tại khu vui chơi (chưa hỗ trợ đặt phòng khách sạn hoặc đổi/hoàn vé máy bay)."
    return None


def _extract_budget(text: str) -> int | None:
    """Trích xuất ngân sách (VND) từ chuỗi tiếng Việt tự nhiên."""
    low = text.lower().replace(",", ".").replace(" ", "")
    m_tr = re.search(r"(\d+(?:\.\d+)?)\s*(?:tr|triệu|trieu)", text.lower().replace(",", "."))
    if m_tr:
        return int(float(m_tr.group(1)) * 1_000_000)
    m_k = re.search(r"(\d+(?:\.\d+)?)\s*(?:k|nghìn|nghin|ngàn|ngan)\b", text.lower().replace(",", "."))
    if m_k:
        return int(float(m_k.group(1)) * 1_000)
    m_vnd = re.search(r"(\d[\d\.,]{4,})\s*(?:đ|d|vnđ|vnd)?", low)
    if m_vnd:
        digits = re.sub(r"[^\d]", "", m_vnd.group(1))
        if digits:
            return int(digits)
    return None


def _parse_request(text: str) -> dict[str, Any]:
    """Trích xuất thông số gia đình, khung giờ và điều kiện ngày từ câu hỏi người dùng."""
    low = text.lower()
    m_adults = re.search(r"(\d+)\s*(?:người lớn|nguoi lon|bố mẹ|ba mẹ|phụ huynh)", low)
    adults = int(m_adults.group(1)) if m_adults else (2 if ("gia đình" in low or "vợ chồng" in low) else None)

    ages = [int(a) for a in re.findall(r"(?:bé|trẻ|con)\s*(?:gái|trai)?\s*(\d{1,2})\s*tuổi", low)]
    if not ages:
        m_age_list = re.search(r"(\d+)\s*(?:bé|trẻ em|trẻ nhỏ|con nhỏ)\s*\(([^)]+)\)", low)
        if m_age_list:
            ages = [int(x) for x in re.findall(r"\d{1,2}", m_age_list.group(2))]
    heights = [int(h) for h in re.findall(r"(\d{2,3})\s*cm", low)]

    ngay = "2026-11-28"
    if "mưa cả ngày" in low or "2026-11-30" in low:
        ngay = "2026-11-30"
    elif "mưa" in low or "2026-11-29" in low:
        ngay = "2026-11-29"
    elif "bảo trì" in low or "huỷ show" in low or "hủy show" in low or "2026-12-01" in low:
        ngay = "2026-12-01"

    m_time = re.search(r"(\d{1,2})[:h](\d{0,2})\s*(?:-|đến|tới)\s*(\d{1,2})[:h](\d{0,2})", low)
    if m_time:
        start = f"{int(m_time.group(1)):02d}:{int(m_time.group(2) or 0):02d}"
        end = f"{int(m_time.group(3)):02d}:{int(m_time.group(4) or 0):02d}"
    elif "3 tiếng" in low or "ba tiếng" in low:
        start, end = "14:00", "17:00"
    else:
        start, end = "09:00", "17:30"

    return {
        "ngan_sach_vnd": _extract_budget(text),
        "so_nguoi_lon": adults,
        "danh_sach_tuoi_tre": ages,
        "chieu_cao_tre_cm": heights or None,
        "ngay": ngay,
        "gio_bat_dau": start,
        "gio_ket_thuc": end,
        "chi_trong_nha": "trong nhà" in low,
    }


def _to_min(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _fmt_hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _build_fallback_schedule(
    parsed: dict[str, Any],
    attractions: list[dict[str, Any]],
    shows: list[dict[str, Any]],
    weather: dict[str, Any],
) -> list[dict[str, Any]]:
    """Tạo lịch khung hợp lệ bằng code khi chạy ở chế độ giả (chưa nối model thật)."""
    cur = _to_min(parsed["gio_bat_dau"])
    end_limit = _to_min(parsed["gio_ket_thuc"])
    budget = parsed["ngan_sach_vnd"]
    adults = parsed["so_nguoi_lon"]
    paying_kids = sum(1 for a in parsed["danh_sach_tuoi_tre"] if a >= 3)
    entry_est = adults * 350_000 + paying_kids * 250_000
    remaining_extra = max(0, budget - entry_est)

    rain_windows = [w for w in weather.get("khung_gio", []) if w.get("condition") == "mua"]
    candidates: list[tuple[str, dict[str, Any]]] = [("show", s) for s in shows if s.get("trang_thai") == "hoat_dong"]
    # Ưu tiên miễn phí hoặc phụ thu vừa túi tiền trước
    sorted_attrs = sorted(
        [a for a in attractions if a.get("trang_thai", "hoat_dong") == "hoat_dong"],
        key=lambda x: (x["price_adult"] + x["price_child"], -x["duration_min"]),
    )
    candidates += [("attraction", a) for a in sorted_attrs]

    chosen: list[dict[str, Any]] = []
    prev_zone: str | None = None
    prev_buffer = 0
    for kind, item in candidates:
        if len(chosen) >= 4:
            break
        fee = item["price_adult"] * adults + item["price_child"] * paying_kids
        if fee > remaining_extra:
            continue
        travel = (uoc_thoi_gian_di(prev_zone, item["zone"])["phut"] + prev_buffer) if prev_zone else 0
        if kind == "show":
            s_m, e_m = _to_min(item["start"]), _to_min(item["end"])
            if s_m < cur + travel or e_m > end_limit:
                continue
        else:
            s_m = max(cur + travel, _to_min(item["open"]))
            e_m = s_m + item["duration_min"]
            if e_m > min(end_limit, _to_min(item["close"])):
                continue
        if not item["indoor"] and any(max(s_m, _to_min(w["start"])) < min(e_m, _to_min(w["end"])) for w in rain_windows):
            continue
        chosen.append({"id": item["id"], "start": _fmt_hhmm(s_m), "end": _fmt_hhmm(e_m), "ly_do": item["description"]})
        remaining_extra -= fee
        cur = e_m
        prev_zone = item["zone"]
        prev_buffer = int(item.get("buffer_after_min", 0))
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
) -> str:
    """Định dạng lịch trình từng khung giờ kèm tổng chi phí chuẩn từ code."""
    lines = ["[CHẾ ĐỘ KHUNG / AI GIẢ — chưa nối model thật]" if is_mock else "LỊCH TRÌNH ĐỀ XUẤT (đã kiểm tra ràng buộc):"]
    lines.append(f"- Thời tiết ngày {weather['ngay']}: {weather['tom_tat']}")
    for it in items:
        meta = catalog.get(it["id"], {})
        loai = "Trong nhà" if meta.get("indoor") else "Ngoài trời"
        lines.append(f"• {it['start']}–{it['end']} | [{it['id']}] {meta.get('name', it['id'])} ({meta.get('zone', '')}, {loai}) — {it.get('ly_do', '')}")
    cost = check_res["chi_tiet_chi_phi"]
    lines.append(
        f"- Tổng chi phí (tính bằng code): {check_res['tong_tien_vnd']:,}đ "
        f"(Vé cổng: {cost['ve_cong']:,}đ · Phụ thu: {cost['phu_thu']:,}đ)."
    )
    lines.append("- Lưu ý: Đây là lịch trình gợi ý để phụ huynh duyệt và tự đặt vé; không có tác động đặt/thanh toán tự động.")
    return "\n".join(lines)


def answer(text: str) -> dict[str, str]:
    """Điểm vào chuẩn cho run.py, eval và simulate."""
    blocked = _check_safety(text)
    if blocked:
        return {"output": blocked}

    parsed = _parse_request(text)
    missing: list[str] = []
    if parsed["ngan_sach_vnd"] is None:
        missing.append("ngân sách tối đa (VNĐ)")
    if parsed["so_nguoi_lon"] is None:
        missing.append("số người lớn")
    if not parsed["danh_sach_tuoi_tre"]:
        missing.append("số lượng và độ tuổi trẻ nhỏ")
    if missing:
        note("hoi_lai: thieu " + ", ".join(missing))
        return {
            "output": (
                f"Để xếp lịch chính xác và đúng ngân sách cho gia đình, vui lòng bổ sung: {', '.join(missing)}. "
                "Ví dụ: '2 người lớn, 1 bé 5 tuổi (110cm), ngân sách 1.5 triệu, đi từ 9h đến 17h'."
            )
        }

    weather = tra_thoi_tiet(parsed["ngay"])
    min_age = min(parsed["danh_sach_tuoi_tre"])
    min_h = min(parsed["chieu_cao_tre_cm"]) if parsed["chieu_cao_tre_cm"] else None
    attrs = tra_diem_choi(
        do_tuoi_nho_nhat=min_age,
        chieu_cao_nho_nhat_cm=min_h,
        chi_trong_nha=parsed["chi_trong_nha"],
        ngay=parsed["ngay"],
    )
    shows = tra_lich_show(ngay=parsed["ngay"], chi_trong_nha=parsed["chi_trong_nha"])
    catalog = {a["id"]: a for a in attrs["diem_choi"]} | {s["id"]: s for s in shows["shows"]}

    # Kiểm tra nhanh nếu ngân sách thấp hơn cả vé cổng cơ bản
    pre_check = kiem_lich_trinh(
        [], parsed["ngan_sach_vnd"], parsed["so_nguoi_lon"], parsed["danh_sach_tuoi_tre"],
        parsed["ngay"], parsed["gio_bat_dau"], parsed["gio_ket_thuc"], parsed["chieu_cao_tre_cm"],
    )
    if pre_check["chi_tiet_chi_phi"]["ve_cong"] > parsed["ngan_sach_vnd"]:
        note("dung: ngan sach thap hon ve cong toi thieu")
        return {
            "output": (
                f"Không thể xếp lịch vì ngân sách {parsed['ngan_sach_vnd']:,}đ thấp hơn tiền vé cổng tối thiểu "
                f"({pre_check['chi_tiet_chi_phi']['ve_cong']:,}đ).\nGợi ý: " + "; ".join(pre_check["goi_y_noi_rang_buoc"])
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
            check_res = kiem_lich_trinh(
                items, parsed["ngan_sach_vnd"], parsed["so_nguoi_lon"], parsed["danh_sach_tuoi_tre"],
                parsed["ngay"], parsed["gio_bat_dau"], parsed["gio_ket_thuc"], parsed["chieu_cao_tre_cm"],
            )
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
        check_res = kiem_lich_trinh(
            items, parsed["ngan_sach_vnd"], parsed["so_nguoi_lon"], parsed["danh_sach_tuoi_tre"],
            parsed["ngay"], parsed["gio_bat_dau"], parsed["gio_ket_thuc"], parsed["chieu_cao_tre_cm"],
        )
        if check_res["hop_le"]:
            note(f"dung: lich hop le tai vong {round_idx + 1}")
            break
        prompt = (
            f"Lịch trình vừa đề xuất có các vi phạm sau (do code kiểm tra):\n"
            + "\n".join("- " + v for v in check_res["vi_pham"])
            + f"\nHãy sửa lại JSON để hết hoàn toàn vi phạm.\nDữ liệu gốc:\n{context}"
        )

    if not check_res.get("hop_le"):
        note("dung: het vong sua van con vi pham")
        return {
            "output": (
                "Không xếp được lịch trình thỏa mãn toàn bộ ràng buộc.\n"
                "Lý do vướng:\n- " + "\n- ".join(check_res.get("vi_pham", ["Chưa tạo được lịch hợp lệ"]))
                + "\nGợi ý nới ràng buộc: " + "; ".join(check_res.get("goi_y_noi_rang_buoc", []))
            )
        }
    return {"output": _format_success(items, check_res, catalog, weather, is_mock)}
