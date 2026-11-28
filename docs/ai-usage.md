# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử & Web UI | Coding Agent (Antigravity / Codex) | Sinh khung 5 công cụ chỉ đọc `codebase/tools.py`, nhánh kết nối API chuẩn `codebase/ai.py`, luồng `Plan -> Verify -> Repair` trong `codebase/agent.py`, `request_parser.py` và giao diện Web UI 0 thư viện ngoài (`app.py`, `web_ui.html`) | Kiểm tra lại công thức tính vé cổng, phụ thu, thời gian di chuyển + đệm công viên nước, sửa parser theo 3 phiên người dùng thật và kiểm thử 22 unit tests offline (`tests/test_c1_agent.py`, `tests/test_web_app.py`) | Lê Sông Thao, Trần Quốc Tuấn |
| Prompt / thiết kế lời gọi mô hình | Coding Agent | Gợi ý `SYSTEM` prompt xuất JSON theo căn cứ và prompt vòng sửa lỗi | Chỉnh câu chữ từ chối an toàn, giới hạn vòng sửa `MAX_REPAIR_ROUNDS = 2` và kiểm tra khớp `spec.md` §4 | Lê Sông Thao |
| Đào data (viết script đếm, gợi ý nhãn) | Coding Agent (Codex) | Viết script `evidence/count.py` đếm 6 nhãn pain từ CSV và chuẩn hóa định dạng bảng `evidence/data-mining.md` | Nhóm tự thu thập, lọc và ẩn danh 50 review Google Maps (`evidence/reviews_anon.csv`), tự đọc 15 review đầu chốt nhãn và đối chiếu 100% đầu ra `count.py` | Nguyễn Huy Giang |
| Rà câu hỏi phỏng vấn / khảo sát | Coding Agent | Rà câu hỏi mở không dẫn dắt theo Mom Test | Phỏng vấn trực tiếp 5 người ngoài nhóm (`P1.md`–`P5.md`), tự ghi chép câu trả lời thật | Nguyễn Tuấn Dũng |
| Viết câu thử (benchmark) | Coding Agent (Codex) | Rà độ phủ lưới 4 chiều và kiểm định dạng CSV/UTF-8 theo `run.py check` | Chốt đủ 25 câu thử (`eval/benchmark.csv`), 15/25 từ `nguoi_dung`/`data_that` (60.0%), `sinh_seed = 0`, tự viết và rà từng `pass_criterion` | Nguyễn Huy Giang |
| Sinh data `synthetic` (nếu có) | Claude Code (trích nguồn thật) + tự dựng thủ công | Trích xuất giờ mở, giá vé, ngưỡng `A01`–`A07` từ 3 trang `vinwonders.com`; rà cấu trúc JSON `data/park/*.json` | Không sinh ngẫu nhiên bằng prompt; đối chiếu tay nguồn thật (`data/DATA_CARD.md`), chạy script kiểm nhất quán và kiểm thử qua `tests/test_c1_agent.py` | Trần Quốc Tuấn, Lê Sông Thao |
| Chấm cột `pass` bằng LLM (nếu có) | *(Không dùng — chấm bằng code + người)* | — | Chấm độc lập theo `eval/metric_spec.yaml` và đối chiếu người thứ hai 25/25 output (khớp 25/25) ở `eval/README.md` | Nguyễn Huy Giang, Nguyễn Tuấn Dũng |
| Slide, văn bản | Coding Agent | Rà cấu trúc markdown, sơ đồ Mermaid và chính tả tài liệu `spec.md`, `canvas.md` | Đối chiếu từng số liệu với phiếu phỏng vấn thật `P1`–`P5`, không bịa số | Cả nhóm |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
