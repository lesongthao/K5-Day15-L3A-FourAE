# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Dữ liệu chạy thử (bài mẫu, thông báo mẫu, đoạn transcript…) để trong thư mục `data/` này.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

## Dataset 1 · `data/park_data.json` (Khu vui chơi Mẫu WonderPark)

| | |
|---|---|
| Dùng để làm gì | Nguồn dữ liệu nền cho 5 công cụ trong `codebase/tools.py` (`tra_diem_choi`, `tra_lich_show`, `tra_thoi_tiet`, `uoc_thoi_gian_di`, `kiem_lich_trinh`) phục vụ lập và kiểm tra lịch trình 1 ngày cho gia đình có trẻ nhỏ. |
| Từ đâu | Nhóm tự xây dựng có kiểm soát (`synthetic`) với tên công viên dựng `"Khu vui chơi Mẫu WonderPark"`, mô phỏng cấu trúc điểm chơi/show/giá vé/ràng buộc chiều cao-độ tuổi của các khu vui chơi tổ hợp lớn. |
| Xử lý những bước gì | Thiết kế cấu trúc JSON chuẩn hóa 4 khu (`CongChao`, `CoTich`, `ThuyCung`, `MaoHiem`), kiểm tra tính đối xứng của ma trận thời gian di chuyển `travel_times_min`, cài sẵn các ca biên (đóng sớm `16:30`, mở chiều `13:00`, phụ thu riêng, thời gian đệm 20p sau công viên nước `DC04`, bảo trì `DC02`/`SH03` ngày `2026-12-01`, bảng phí dịch vụ lẻ `extra_services`, giới hạn `min_age`/`min_height_cm`, mưa chiều/mưa cả ngày). |
| Số dòng / số đoạn | 12 điểm chơi (`DC01`–`DC12`), 4 show diễn (`SH01`–`SH04`), 4 kịch bản thời tiết (`2026-11-28` đến `2026-12-01`), ma trận di chuyển 4×4 khu vực. |
| Phiên bản / ngày lấy | v1.0 · ngày 27/11/2026 (seed cố định `42`). |
| Nhãn | `synthetic` |
| Giới hạn | Dữ liệu dựng cố định trên một công viên mẫu với 4 kịch bản thời tiết; chưa phản ánh biến động thời gian xếp hàng thực tế theo giờ cao điểm cuối tuần. |

**Data `synthetic` (nhóm tự sinh):** Tạo thủ công có chủ đích theo `seed: 42` để bao phủ 4 lớp chỗ khó Track C1 (nguồn sự thật, mơ hồ, ngoài phạm vi, sai ràng buộc an toàn trẻ nhỏ/ngân sách); người kiểm: Lê Sông Thao (kiểm tra toàn bộ 12 điểm + 4 show + 4 kịch bản ngày qua test hàm `kiem_lich_trinh`). **Data tự dựng không dùng làm bằng chứng pain.**

## Dataset 2 · Review công khai khu vui chơi tổ hợp (Google Maps / Tripadvisor)

| | |
|---|---|
| Dùng để làm gì | Đào bằng chứng pain thực tế (`evidence/data-mining.md`) và làm nguồn thật cho bộ câu thử `eval/benchmark.csv` (mã `data_that:`). |
| Từ đâu | Review công khai trên Google Maps / Tripadvisor của các khu vui chơi tổ hợp lớn tại Việt Nam (đang thu thập và gắn nhãn theo guide bước 1.2 bởi Nguyễn Huy Giang). |
| Xử lý những bước gì | Lọc bỏ tên người viết, giữ lại nguồn, ngày, số sao, tối đa 2 câu trích nguyên văn và gán nhãn loại vấn đề (`evidence/count.py`). |
| Số dòng / số đoạn | Đang thu thập (mục tiêu 30–50 review trước 19:30; hoàn tất trước CP3). |
| Phiên bản / ngày lấy | 27/11/2026 |
| Nhãn | `thật` |
| Giới hạn | Review thường nghiêng về trải nghiệm quá tốt hoặc quá tệ; cần kết hợp đối chiếu với phỏng vấn trực tiếp phụ huynh (`evidence/interviews/`). |
