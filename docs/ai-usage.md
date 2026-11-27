# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | Coding Agent (Antigravity / Codex) | Sinh khung 5 công cụ chỉ đọc `codebase/tools.py`, nhánh kết nối API chuẩn `codebase/ai.py` và luồng `Plan -> Verify -> Repair` trong `codebase/agent.py` | Kiểm tra lại công thức tính vé cổng, phụ thu, thời gian di chuyển + đệm công viên nước, test chạy 8 ca biên `tests/test_c1_agent.py` | Lê Sông Thao, Trần Quốc Tuấn |
| Prompt / thiết kế lời gọi mô hình | Coding Agent | Gợi ý `SYSTEM` prompt xuất JSON theo căn cứ và prompt vòng sửa lỗi | Chỉnh câu chữ từ chối an toàn, giới hạn vòng sửa `MAX_REPAIR_ROUNDS = 2` và kiểm tra khớp `spec.md` §4 | Lê Sông Thao |
| Đào data (viết script đếm, gợi ý nhãn) | *(Chưa chạy / cập nhật CP3)* | Viết script đếm review công khai và gợi ý gom nhãn | Kiểm tay __ dòng, khớp __ | Nguyễn Huy Giang |
| Rà câu hỏi phỏng vấn / khảo sát | Coding Agent | Rà câu hỏi mở không dẫn dắt theo Mom Test | Phỏng vấn trực tiếp 5 người ngoài nhóm (`P1.md`–`P5.md`), tự ghi chép câu trả lời thật | Nguyễn Tuấn Dũng |
| Viết câu thử (benchmark) | *(Chưa chạy / cập nhật CP2–CP3)* | Gợi ý biến thể câu chữ dựa trên lưới input | Mỗi câu thử có `source`; câu thử AI viết được ghi rõ mã `sinh_seed` | Nguyễn Huy Giang |
| Sinh data `synthetic` (nếu có) | Tự dựng thủ công + rà soát bằng tool | Bổ sung khung kịch bản thời tiết, show mẫu (`data/park/*.json`) kết hợp dữ liệu thật từ VinWonders (`W_RULES`, `W_PRICE`, `W_HOURS`) | Không sinh ngẫu nhiên bằng prompt; kiểm tay 18 trò chơi, 6 show, 4 kịch bản qua `tests/test_c1_agent.py` | Trần Quốc Tuấn, Lê Sông Thao |
| Chấm cột `pass` bằng LLM (nếu có) | *(Không dùng — chấm bằng code + người)* | — | Kiểm tra thủ công __ câu thử, khớp __/__ | Nguyễn Huy Giang, Nguyễn Tuấn Dũng |
| Slide, văn bản | Coding Agent | Rà cấu trúc markdown, sơ đồ Mermaid và chính tả tài liệu `spec.md`, `canvas.md` | Đối chiếu từng số liệu với phiếu phỏng vấn thật `P1`–`P5`, không bịa số | Cả nhóm |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
