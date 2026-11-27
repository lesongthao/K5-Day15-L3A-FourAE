# Chi phí khi dùng thật

> Guide bước 4.2 · nộp CP4 14:30 Thứ Bảy 28/11 · chấm ở rubric R6 · người phụ trách: Trần Quốc Tuấn.
> Số **không điền tay**: `cost/personas.yaml` → `python run.py simulate --rate-from eval/run-2.csv` → chép bảng trong `cost/simulate-N-summary.md` vào đây.
> Lúc build dùng proxy của nhóm, nhưng chi phí tính theo **giá trả phí chính thức** — đây là chi phí cho lúc đưa vào dùng thật.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`, theo `spec.md` §2 — số lần / tháng *(tự ước tính)* từ hành vi trong phỏng vấn P1–P5):

  | Persona | Tỉ lệ | Phiên / người / tháng | Lượt hỏi / phiên | Nguồn |
  |---|---:|---:|---:|---|
  | `lap_lich_nhanh` — lập lịch nhanh 1 lần trước chuyến đi | 50% | 1 | 2 | §2 kiểu 1 (P4, P5) |
  | `len_lich_ky` — lên lịch kỹ, sửa nhiều lần theo tuổi con và ngân sách | 35% | 3 | 3 | §2 kiểu 2 (P1, P3) |
  | `xep_lai_dot_xuat` — xếp lại do mưa / huỷ show / bảo trì | 15% | 2 | 4 | §2 kiểu 3 (16,0% review `thoi_tiet_mua`; P2, P5) |

  §2 ghi số lượt / phiên dạng khoảng (1–2, 2–3, 3–4) → lấy **cận trên** để không đánh giá thấp chi phí.
- **Số người dùng thật** (gia đình dùng công cụ / tháng tại 1 khu vui chơi lớn): thấp **1.124** · cơ sở **5.620** · cao **10.000**. Nguồn: cơ sở = 10.000 gia đình/tháng *(tự ước tính)* × 56,2% (9/16 review gia đình gặp pain, `evidence/data-mining.md`) — đúng số ở `spec.md` §2; cao = toàn bộ 10.000 gia đình *(tự ước tính, §2)*; thấp = 20% mức cơ sở *(tự ước tính)*. VinWonders không công bố số khách / năm (đã tra 27/11/2026).
- **Giá** 3 mức model, USD / 1 triệu token, giá chuẩn ngữ cảnh ngắn — [developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing), xem 27/11/2026:

  | Model | Vai trò | Vào | Ra |
  |---|---|---:|---:|
  | `gpt-5.6-luna` | model đang dùng (qua proxy, tên `cx/gpt-5.6-luna`) | 0,20 | 1,20 |
  | `gpt-6-luna` | mức rẻ hơn | 0,10 | 0,50 |
  | `gpt-5.6-terra` | mức mạnh hơn | 2,00 | 12,00 |

- **Tỉ lệ đạt** dùng để tính: **23/25 (92%)** — lượt `run-2` (`run-2@20261127-185059`, model `cx/gpt-5.6-luna`, cùng model với mô phỏng).
- **Đo token trên model `cx/gpt-5.6-luna`** (proxy định dạng OpenAI của nhóm), **tính giá** `gpt-5.6-luna`, `gpt-6-luna` và `gpt-5.6-terra`. Model khác bộ tách token thì số token thật có thể lệch.

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-2.csv` · run ID `simulate-2@20261127-215027` · **50 phiên** · seed **42** · phiên lỗi **0/50** · trace `traces/simulate-2.jsonl`

*(bảng chép nguyên từ `cost/simulate-2-summary.md`)*

| Model (giá $/1M vào · ra) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | / tháng — thấp (1.124) | / tháng — cơ sở (5.620) | / tháng — cao (10.000) | / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `cx/gpt-5.6-luna` (0,20 · 1,20) — **model đang dùng** | $0.0043 | **$0.0046** | $0.0017 | $9.25 | $46.25 | $82.30 | **$0.0082** |
| `gpt-6-luna` (0,10 · 0,50) | $0.0019 | $0.0021 | $0.00077 | $4.12 | $20.62 | $36.68 | $0.0037 |
| `gpt-5.6-terra` (2,00 · 12,00) | $0.0426 | $0.0463 | $0.0173 | $92.50 | $462.51 | $822.96 | $0.0823 |

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt (**92%**, `run-2`) — **không coi như đạt 100%**. Chi phí / câu hỏi đạt = chi phí / phiên ÷ 2,7 lượt hỏi trung bình / phiên ÷ 92%.

Theo persona (token trung bình / phiên, đo thật trên `cx/gpt-5.6-luna`):

| Persona | Số phiên | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| `lap_lich_nhanh` | 24 | 2 | 6.020 | 1.822 | 1,8 | 10,2 |
| `len_lich_ky` | 18 | 3 | 7.470 | 2.327 | 2,2 | 13,0 |
| `xep_lai_dot_xuat` | 8 | 4 | 11.677 | 3.704 | 3,5 | 18,5 |

**Lượt hỏng, không dùng:** `cost/simulate-1.csv` (`simulate-1`) — **43/50 phiên lỗi** `HTTP 530 · error code 1033` do tunnel của proxy sập giữa lượt (lỗi hạ tầng, không phải lỗi bản chạy thử). Giữ nguyên file, không sửa; chạy lại thành `simulate-2` khi proxy ổn định.

### Lưu ý về token do proxy cộng thêm

Proxy của nhóm cộng thêm token vào mỗi lần gọi model, không do bản chạy thử tạo ra: ngày 27/11/2026, gọi `cx/gpt-5.6-luna` với câu *"Trả lời đúng một chữ: ok"* và prompt hệ thống trống vẫn đo **2.493 token vào** (câu hỏi chỉ ~10 token). Bảng trên dùng **token đo thật** (đúng yêu cầu R6, không ước lượng) nên **cao hơn** chi phí khi gọi API gốc. Ước tính sau khi trừ phần này — *chỉ để tham khảo, không thay bảng trên*:

- Token vào thừa / phiên ≈ 2.483 × 2,22 lần gọi model / phiên ≈ **5.512 token = 74% token vào** (7.447 token vào / phiên trung bình) *(ước tính từ 1 lần đo)*
- Chi phí / phiên sau khi trừ: `gpt-5.6-luna` **$0.0032** (giảm 26%) · `gpt-6-luna` $0.0014 (giảm 29%) · `gpt-5.6-terra` $0.0315 (giảm 26%)

## 3. So với impact

- **Impact / người / tháng** (`spec.md` §2): 60–120 phút ≈ **100.000–200.000 đ / người / tháng** *(tự ước tính, mức 100.000 đ/giờ)*.
- **Chi phí / người / tháng** (cơ sở, `gpt-5.6-luna`): **$0.0082 ≈ 213 đ** *(tỉ giá 26.000 đ/USD — tự ước tính; không tìm được tỉ giá Vietcombank tháng 11/2026 có trang gốc kiểm được. Tỉ giá lệch ±10% không đổi kết luận)*. Chi phí / task thành công $0.0046 ≈ **120 đ**.
- **Kết luận một dòng — đáng làm không:** **Go (về chi phí)** — chi phí model ~213 đ / người / tháng chỉ bằng **~0,1–0,2%** impact ước tính (100.000–200.000 đ), kể cả model đắt nhất `gpt-5.6-terra` (~2.140 đ) vẫn < 3%; rủi ro của sản phẩm nằm ở **độ đúng** (2/25 câu `kho` còn trượt ở `run-2`) và **giữ data cập nhật**, không nằm ở tiền model.

## 4. *(Muốn sâu hơn, không bắt buộc)*

- **Đổi model:** `gpt-6-luna` rẻ hơn **~2,2 lần** so với `gpt-5.6-luna`; `gpt-5.6-terra` đắt hơn **~10 lần**. Chưa đo tỉ lệ đạt trên 2 model này — đổi model phải chạy lại eval trước khi dùng con số.
- **Bỏ phần token proxy cộng thêm** (gọi API gốc): giảm **~26%** chi phí / phiên với `gpt-5.6-luna` (mục 2).
- **Persona tốn nhất:** `xep_lai_dot_xuat` (mưa / huỷ show / bảo trì) dùng ~1,9 lần token / phiên so với `lap_lich_nhanh` vì phải tra lại và xếp lại lịch nhiều vòng.
- **Chi phí ngoài model** *(chưa tính)*: hosting, lưu trữ trace, giờ công cập nhật data khu vui chơi (giá vé, lịch show, bảo trì) — với data lai, đây có thể là khoản lớn hơn tiền model.
