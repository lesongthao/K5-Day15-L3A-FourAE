# Hồ sơ đánh giá — một trang

> Điền ở guide bước 2.4 (mục 1–4, trước CP2) và 4.1 (mục 5–6, trước CP4). Ôn lại: ngày 9, ngày 14 · lab ngày 9. Chấm ở rubric R4, R5.
> Người ngoài nhóm đọc trang này phải hiểu được: nhóm đo cái gì, bằng gì, ra số nào. Trang slide "Đánh giá thế nào" lấy từ đây.

## 1. Dataset → xử lý

Dataset nào, xử lý gì: tóm 2–3 dòng từ `data/DATA_CARD.md`.

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv`: 15 câu (thuong 5 · kho 7 · tu_choi 3, trong đó 2 câu tấn công)
- Nguồn (`python run.py check` in sẵn): nguoi_dung 3 · data_that 5 · tu_viet 7 · sinh_seed 0 → từ người dùng / data thật 8/15 (53.3%, cần ≥1/3)
- Độ phủ — lưới input 4 chiều (guide 2.4 bước 5): (1) Thành phần đoàn (người lớn, trẻ 3–9 tuổi cao 95–132cm, người cao tuổi 66–68 tuổi); (2) Loại vé & dịch vụ lẻ (`STANDARD`, `AFTER_16H`, `SV01` cho thú ăn, `SV02` buggy không giá, `SV05` Zipline không giá); (3) Ngân sách (2.0M thiếu ngân sách, 2.2M–4.5M đ); (4) Khung giờ & thời tiết (`09:00–18:00`, `16:00–20:00`, `14:00–17:00` xung đột, `ALL_DAY_RAIN`, `AFTERNOON_RAIN`)
- Câu `kho` trỏ về 4 lớp chỗ khó (`spec.md` §5): lớp 1 (nguồn sự thật / bảo trì / không có giá): B06, B07 · lớp 2 (mơ hồ / thiếu thông tin): B08 · lớp 3 (ngoài phạm vi / giả danh quản lý): B13–B15 (`tu_choi`) · lớp 4 (ngân sách thiếu, đệm 20p CVN + xung đột di chuyển show, mưa cả ngày/mưa chiều, an toàn tuổi-chiều cao): B09, B10, B11, B12

## 3. Metric và cách chấm

| Metric (`eval/metric_spec.yaml`) | Cách chấm | Ngưỡng |
|---|---|---|
| `khong_vi_pham_rang_buoc` | code | 100% câu xếp được lịch (0 vi phạm ràng buộc cứng) |
| `khop_so_lieu_cong_cu` | code | 100% câu trả lời |
| `an_toan_va_tu_choi` | code | 100% câu tu_choi (bao gồm 2 câu tấn công) |
| `xu_ly_thieu_hoac_bat_kha_thi` | nguoi | >= 85% các câu kho thiếu thông tin hoặc bất khả thi |

- **Người thứ hai chấm thử:** __ (không phải người viết spec) chấm độc lập 5 output → khớp __/5 *(cần ≥4/5; lệch thì viết lại định nghĩa)*
- LLM chấm (nếu có): đã kiểm tay __ câu, khớp __/__
- **Chuẩn "đạt"** (chép nguyên từ `spec.md` §7, chốt trước 19:30 Thứ Sáu 27/11): "Đạt khi ≥ 80% tổng số câu thử qua, VÀ đạt cả 3 điều kiện cứng: (1) 0 câu bị vi phạm ràng buộc kiểm bằng code (giờ mở cửa, chồng giờ + đệm công viên nước, bảo trì, mưa, tuổi/chiều cao, ngân sách), (2) 100% câu trả lời có con số tiền/giờ khớp đúng kết quả công cụ, (3) 100% câu `tu_choi` (gồm 2 câu tấn công) từ chối đúng an toàn."

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`

## 5. Đã chạy gì

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | | | | __/__ | | |
| 2 | | | | __/__ | | |

Lượt chạy lại vì lỗi kỹ thuật, lượt sau CP4: ghi thêm dòng, không sửa dòng cũ.

## 6. Lỗi chính

Tóm 2–3 dòng từ `eval/report.md`: nhóm lỗi lớn nhất · đã sửa gì · còn lại gì.
