# Dàn slide → lấy số từ file nào

> Làm ở guide bước 5.1. Luật: **không có bằng chứng thì không có slide** — mỗi trang ≥1 con số / trích dẫn có nguồn / kết quả đo.
> Xuất PDF thành `demo-slides.pdf` ở thư mục gốc repo, nộp tại CP4 14:30 Thứ Bảy 28/11. Nộp PDF, không nộp link.

| # | Trang | Có gì | Số lấy từ | Xong |
|---|---|---|---|---|
| 1 | Người dùng & pain | Phụ huynh có trẻ nhỏ (3–10 tuổi) đi khu vui chơi tổ hợp lớn · 2 nguồn đối chiếu: 50 review Google Maps (**20/50 = 40.0%** toàn tập & **9/16 = 56.2%** gia đình gặp `planning_ops_pain`; **8/50 = 16.0%** toàn tập & **7/16 = 43.8%** gia đình gặp pain hẹp giờ mở/show hoặc chiều cao/tuổi, vượt ngưỡng ≥15%) + phỏng vấn **5/5** gia đình ngoài nhóm (`3/5` tự chuẩn bị 30–90p vẫn vỡ lịch/lỡ show/vướng chiều cao/bảo trì, `5/5` phát sinh phí/đổi điểm) · Trích nguyên văn `P3` & `VN24` | `evidence/summary.md` | ☑ |
| 2 | Vì sao chọn bài này | Bảng so sánh 3 hướng (**C1** Chọn · **C2** Lễ tân khách sạn — Loại · **C3** Huỷ chuyến bay — Loại) · Công thức Impact 1 khu vui chơi lớn: `10.000 gia đình/tháng *(tự ước tính)* × 56.2% × 1 lượt × 60 phút = 337.200 phút/tháng (~5.620 giờ ≈ 562 triệu đ/tháng)` · Quy đổi theo người dùng: `~60–120 phút/người/tháng (≈ 100k–200k đ/người/tháng)` | `spec.md` §2 | ☑ |
| 3 | Giải pháp | Lát cắt 1 câu C1 · Sơ đồ workflow cố định `Safety → Tools đọc data → LLM Plan → kiem_lich_trinh (code) → Repair tối đa 2 vòng` (lý do không dùng multi-agent) · Mức tự động: *AI gợi ý, người quyết* (chỉ đọc, không tự đặt vé/thanh toán) · Chỗ chặn rủi ro bằng code (`_check_safety` + `kiem_lich_trinh`) + nguyên tắc `G10` | `spec.md` §4 | ☑ |
| 4 | Demo live | 1 ca thường (`B05`: vé `AFTER_16H`, `1.950.000đ`, Bánh xe bầu trời + Tata Show 19:30) + 1 ca khó (`B12`: `AFTERNOON_RAIN` 14:00–16:00, bé 5t 108cm + ông 68t, `3.700.000đ`) + 1 ca tấn công (`B15`/`B25` ép bỏ giới hạn chiều cao) · Link video dự phòng *(chờ Thao quay bản cuối ở CP4)* | `eval/benchmark.csv` | ☐ |
| 5 | **Đánh giá thế nào** | Dataset VinWonders Nha Trang lai thật (`W_HOURS/W_PRICE/W_RULES`) + `synthetic` · 25 câu thử (`15/25 = 60%` từ nguồn thật) · 4 metric (chấm chéo khớp `25/25`) · **Lượt 1** (`run-1@20261127-182508`): `16/25 (64%)`, `tu_choi 4/4 (100%)`, 3 nhóm lỗi chính (5 câu hiểu nhầm thiếu giá vé/dịch vụ, 2 câu sót show bắt buộc, 2 câu kẹt vòng sửa) → **Lượt 2** *(chờ chạy sau cải tiến ở CP4)* | `eval/README.md`, `eval/report.md` | ☐ |
| 6 | **Chi phí khi dùng thật** | *(Chờ Tuấn chạy `python run.py simulate` ≥50 phiên với 3 persona từ §2 và ≥2 mức model → điền chi phí/task thành công, 3 kịch bản thấp/cơ sở/cao và so với impact `100k–200k đ/người/tháng`)* | `cost/cost-estimate.md` | ☐ |
| 7 | Kết luận | *(Chờ số Lượt 2 từ Trang 5 & chi phí từ Trang 6 để chốt Go / Iterate / Stop dựa trên số)* | — | ☐ |
| 8 | Nếu có thêm 1 tuần | *(Chờ lỗi còn lại sau Lượt 2 + phản hồi 2–3 người dùng thử từ `validation/log.md` — dự kiến tích hợp hàng chờ thực tế, lịch bảo trì real-time và xuất lịch 1 màn hình offline theo `P1`/`P4`/`P5`)* | `eval/report.md` mục 4 · `validation/log.md` | ☐ |

**Trước khi lên:** tải repo về một máy khác (hoặc thư mục mới), chạy theo mục "Chạy trong 3 phút" của `README.md` · `.env` có trên máy demo, đã gọi thử 1 câu trong vòng 1 giờ trước giờ demo · video dự phòng mở được bằng cửa sổ ẩn danh · biết bản chạy thử sẽ làm gì với **1 câu thử lạ** của giám khảo.

Ai nói trang nào (mỗi người ≥1 phần):

| Trang | Người nói |
|---|---|
| 1–2 · Pain + Bằng chứng + Impact (§1–§2) | Nguyễn Tuấn Dũng |
| 3–4 · Thiết kế giải pháp + Live Demo (§4) | Lê Sông Thao |
| 5 · Bộ câu thử + Metric + Kết quả Lượt 1 → Lượt 2 (§7) | Nguyễn Huy Giang |
| 6–7 · Mô phỏng chi phí + Kết luận Go / Iterate (§8) | Trần Quốc Tuấn |
| 8 · Hướng phát triển tiếp + Điều phối Q&A | Nguyễn Tuấn Dũng |
