# Dàn slide trình bày 5 phút (4 trang trực quan) → `demo-slides.pdf`

> Làm ở guide bước 5.1. Luật: **không có bằng chứng thì không có slide** — mỗi trang đều gắn số liệu đo thật có nguồn từ repo, thiết kế theo dạng sơ đồ luồng trực quan để người nói triển khai tự nhiên thay vì đọc chữ.
> Theo hướng dẫn của Lab Coach (mỗi nhóm có **5 phút** trình bày kèm Live Demo), nhóm FourAE tinh gọn trọn bộ vào **4 trang 16:9** và xuất thành `demo-slides.pdf` tại thư mục gốc repo (nộp CP4 14:30 Thứ Bảy 28/11).

| # | Trang | Nội dung hiển thị & Điểm neo số liệu đo thật | Số lấy từ | Xong |
|---|---|---|---|---|
| 1 | **Tổng quan (Giới thiệu · 0:40)** | **Nhóm FourAE - Đội 5 - Zone 2** (`Hackathon AI20K · Lớp L3A · Track C1`) · Tiêu đề **Trợ lý lịch trình VinWonders Nha Trang** · 2 câu tóm gọn trọn chức năng (tự ghép lịch theo chiều cao bé, độ tuổi ông bà & ngân sách; tự tránh trò bảo trì, đổi khu trong nhà khi mưa & tính rõ tổng chi phí) · **3 chỉ số đo thật:** **`92%`** (`23/25` tình huống đạt chuẩn), **`120đ`** (1 lần lập lịch thành công), **`0 lỗi`** (không sai giờ mở cửa, chiều cao hay giá vé) · 4 thành viên ở thanh đáy | `TEAMS.md`, `canvas.md`, `spec.md` §4 | ☑ |
| 2 | **Bài toán & 2 nguồn bằng chứng thật (1:15)** | Nỗi đau lát cắt từ `canvas.md` & **Hành trình vỡ lịch 4 bước (`P1`–`P5`):** `01. Trước khi đi (30–90p)` → `02. Vừa qua cổng đảo (không biết trò bảo trì)` → `03. Đang chơi thì đứt mạch (tắm thay đồ sau công viên nước mất 40p trễ show, mưa chiều dừng trò, bé chưa đủ 1m2 phải quay ra — 3/5 gia đình chuẩn bị kỹ vẫn vỡ lịch)` → `04. Kết cục (5/5 gia đình xoay xở đổi khu & tốn phí lẻ)` · **3 khối bằng chứng đo thật (2 nguồn đối chiếu):** **`56,2%`** (`9/16` gia đình Google Maps rối lịch), **`43,8%`** (`7/16` vướng giờ show/chiều cao; toàn tập `16% > 15%`), **`5/5 gia đình`** phỏng vấn thật (`P1`–`P5`) · Phễu **Chọn hướng C1** (loại C2, C3) | `canvas.md`, `evidence/summary.md`, `evidence/data-mining.md`, `spec.md` §0–§2 | ☑ |
| 3 | **Giải pháp — Quy trình lát cắt C1 & Kết quả đo thật (2:40)** | **Sơ đồ quy trình 5 bước:** `Gia đình nhập` → `1. Lọc an toàn (code 0đ, chặn 4/4 ca nguy hiểm)` *(2 nhánh tách biệt: `Từ chối an toàn` & `Hỏi lại đúng 1 câu`)* → `2. Tra 4 nguồn dữ liệu` → `3. AI ghép lịch trình (gpt-5.6-luna)` → `4. Code kiểm tra & tính tiền (giờ mở, chiều cao, bảo trì, cộng 20p tắm thay đồ, đúng ngân sách)` *(vòng lặp `Sai điều kiện → AI sửa tối đa 2 lần`, nhánh đạt `Xuất lịch từng giờ & tổng tiền chuẩn`, nhánh lỗi `Báo rõ không xếp được + gợi ý đổi vé sau 16h hoặc giảm trò`)* · **3 thẻ kết quả đo thật:** Eval **`64% → 92%`** (`16 → 23/25`, giảm `28,7%` token) · Chi phí **`120 đồng / lần`** (`$0,0046`, 50 phiên 0 lỗi) · An toàn & thử thật **`AI gợi ý, người quyết`** (chặn `4/4`, thử với `3` người ngoài nhóm) | `spec.md` §4, §7–§9 · `eval/report.md` · `cost/cost-estimate.md` · `validation/log.md` | ☑ |
| 4 | **Cảm ơn & Live Demo (0:25)** | Trang lời cảm ơn tối giản, ít chữ: **Cảm ơn đã lắng nghe! Live Demo & Q&A** · 3 nhãn tình huống demo nhanh (`01 · Gia đình đi sau 16h`, `02 · Trời mưa buổi chiều`, `03 · Chặn ép vượt chiều cao`) · Bản đồ Đảo Hòn Tre, link repo GitHub, video dự phòng & 4 thành viên | `eval/benchmark.csv`, `README.md` | ☑ |

**Trước khi lên:** tải repo về một máy khác (hoặc thư mục mới), chạy theo mục "Chạy trong 3 phút" của `README.md` · `.env` có trên máy demo, đã gọi thử 1 câu trong vòng 1 giờ trước giờ demo · video dự phòng mở được bằng cửa sổ ẩn danh · biết bản chạy thử sẽ làm gì với **1 câu thử lạ** của giám khảo.

Phân công trình bày & Q&A (mỗi người ≥1 phần trong 5 phút):

| Phần | Thời lượng | Người nói |
|---|---|---|
| Slide 1 · Tổng quan & Lát cắt C1 | 0:40 | Lê Sông Thao |
| Slide 2 · Bài toán & 2 nguồn bằng chứng thật (`P1`–`P5` + 50 Google Maps) | 1:15 | Nguyễn Tuấn Dũng |
| Slide 3 (sơ đồ) · Quy trình lát cắt C1 (AI xếp lịch, code kiểm chuẩn) | 1:15 | Lê Sông Thao |
| Slide 3 (thẻ trái) · Đánh giá Lượt 1 → Lượt 2 (`64% → 92%`) | 0:40 | Nguyễn Huy Giang |
| Slide 3 (thẻ giữa & phải) & Slide 4 · Chi phí thật (`120đ`), Thử nghiệm thực tế & Mở Live Demo | 1:10 | Trần Quốc Tuấn |
