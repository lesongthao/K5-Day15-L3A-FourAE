# Reflection — Nguyễn Tuấn Dũng

> Làm ở guide bước 5.3. Mỗi người một file: chép file này thành `reflection/<ten-khong-dau>.md` (viết thường, không dấu). Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. Vai trò + phần mình làm (trỏ tới file / commit):
Em là thành viên nhóm FourAE (Track C1 — Lịch trình một ngày tại khu vui chơi cho gia đình có trẻ nhỏ), phụ trách phỏng vấn 5 phụ huynh ngoài nhóm (`evidence/interviews/P1.md`–`P5.md`, PR #2), tổng hợp đối chiếu 2 nguồn bằng chứng (`evidence/summary.md`, PR #10) và cập nhật `canvas.md`. Em cũng viết `spec.md` §0–§3 & §5 (bảng Impact 3 hướng, công thức Impact/tháng, 3 persona cho `cost/personas.yaml`, 4 lớp chỗ khó + 2 tấn công), chấm độc lập đối chiếu `25/25` trên `eval/run-1.csv` với Giang (`eval/README.md`, PR #13) và chủ trì dàn ý `slides/outline.md` cùng kịch bản demo.

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):
Em dùng Coding Agent để chuẩn hóa ghi chép phỏng vấn theo mẫu Mom Test, đối chiếu số liệu từ `evidence/count.py` vào `evidence/summary.md`, chẩn đoán lỗi HTTP 403 (Cloudflare 1010) của `urllib` trong `codebase/ai.py` để gửi Tuấn sửa kết nối model thật, và rà nhanh 25 output Lượt 1. Các phần em tự thực hiện và sửa tay gồm: trực tiếp hỏi 5 phụ huynh ngoài nhóm, loại bỏ mọi suy diễn không có trong lời kể (ghi trung thực chưa hỏi tần suất theo tháng), đánh dấu rõ thừa số `*(tự ước tính)*` ở `spec.md` §2 và kiểm tra lại từng câu chấm `pass` bảo đảm không đụng cột dữ liệu gốc.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:
Ở Lượt 1 (`run-1@20261127-182508`), câu `B23` (ngân sách `2.920.000đ`, vé cổng `2.900.000đ` + cho thú ăn `SV01` `50.000đ` + locker `SV03` `50.000đ` = `3.000.000đ`, vượt `80.000đ`) bị trượt vì pre-check trong `agent.py` chỉ kiểm `ve_cong > ngan_sach` mà bỏ sót phụ thu dịch vụ lẻ, đồng thời `context` chưa truyền bảng giá khiến model báo sai "thiếu dữ liệu giá vé STANDARD/SV01/SV03". Qua đó em học được rằng insight từ phỏng vấn người dùng (`P4`, `P5` về chi phí lẻ ngoài vé trọn gói) chỉ có giá trị khi đi xuyên suốt từ bằng chứng → câu thử → hàm kiểm code → ngữ cảnh gửi model; sau khi sửa ở Lượt 2 (`d9cb135`), `B23` đạt và tỷ lệ tổng tăng từ `64%` lên `92%`.
