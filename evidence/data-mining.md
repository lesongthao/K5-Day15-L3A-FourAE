# Đào data — cách đếm và kết quả

> Điền ở guide bước 1.2. Ôn lại: ngày 2, ngày 6 · lab ngày 2, lab ngày 6.
> Không đào data thì xoá file này. Script / công thức đếm để trong repo (`evidence/count.py`), người khác chạy lại phải ra cùng số.
> Repo chỉ chứa mẫu đã ẩn danh và số đã tổng hợp — không chép lại tên tác giả hay dữ liệu định danh cá nhân.

## 1. Cách đếm — viết TRƯỚC khi chạy

- **Data dùng:** `evidence/reviews_anon.csv` — 50 review công khai thu thập ngày `27/11/2026` trên Google Maps (`hl=vi`), chế độ sắp xếp `Phù hợp nhất` (*Most relevant*) tại hai khu vui chơi tổ hợp lớn:
  - `Sun World Ba Na Hills` (`BN01`–`BN25`): 25 review liên tiếp, mốc hiển thị trên Google Maps từ `2 tuần trước` đến `7 tháng trước`.
  - `VinWonders Nha Trang` (`VN01`–`VN25`): 25 review liên tiếp, mốc hiển thị trên Google Maps từ `5 ngày trước` đến `5 tháng trước`.
- **Đếm gì · trên tập nào · lọc gì:**
  - Lọc đầu vào: chỉ lấy các review có văn bản chi tiết (`>= ~15` từ, đã mở toàn văn bằng nút "Thêm"/"Xem thêm"), bỏ qua review chỉ chấm sao không có chữ; lấy liên tiếp từ trên xuống để tránh thiên vị chọn lọc.
  - Ẩn danh toàn bộ thành mã `BN01`–`BN25` và `VN01`–`VN25` (loại bỏ hoàn toàn tên người dùng, link hồ sơ và mọi PII).
  - Tập con `has_family_kids = true`: chỉ gán `true` khi nội dung review nhắc trực tiếp tới gia đình (`gia đình`, `nhà mình`) hoặc trẻ nhỏ (`trẻ em`, `trẻ nhỏ`, `trẻ con`, `con nhỏ`, `bé`, `lớp 4-6`).
  - Đếm tần suất 6 nhãn vướng mắc (`pain_tags`), tập cốt lõi giả thuyết (`core_hours_show_or_kids`: có `lo_show_gio_mo_cua` hoặc `tre_nho_chieu_cao_tuoi`), tập vướng mắc lịch trình/vận hành (`planning_ops_pain`: có ít nhất 1 trong 4 tag `lo_show_gio_mo_cua`, `tre_nho_chieu_cao_tuoi`, `di_chuyen_rong`, `xep_hang_chong_gio`), và tỷ lệ có ít nhất 1 vướng mắc (`any_pain`).
- **Mẫu số là gì:**
  - Mẫu số chính toàn tập: `N = 50` review chi tiết hợp lệ (không lấy tổng lượt gắn nhãn làm mẫu số vì 1 review có thể có nhiều tag, và không loại review 4–5 sao khỏi mẫu số).
  - Mẫu số tập con gia đình/trẻ nhỏ: `N_family = 16` review có `has_family_kids = true`.
  - Mẫu số theo địa điểm: `N_BN = 25` (Sun World Ba Nà Hills) và `N_VN = 25` (VinWonders Nha Trang).
- **Script / công thức:** `python evidence/count.py` (chỉ dùng thư viện chuẩn `csv` của Python, UTF-8, đọc trực tiếp `evidence/reviews_anon.csv`).

## 2. Đọc trước, đếm sau

Đã đọc 15 review đầu (`BN01`–`BN08` và `VN01`–`VN07`) cùng cấu trúc 8 cột (`id,source,place,rating,date,has_family_kids,pain_tags,text`) trước khi chốt bộ nhãn. Các *kiểu* hành vi và vướng mắc thực tế thấy được trong dữ liệu:

- `xep_hang_chong_gio`: Phản ánh đông đúc, phải xếp hàng lâu (từ 30 phút đến 2.5 tiếng cho trò chơi hoặc buffet/check-in), hoặc phải mua fast-track / wow pass / đi từ 8h sáng để tránh đoàn khách.
- `di_chuyen_rong`: Khuôn viên quá rộng, các khu ở xa nhau, dễ đi lạc hoặc mất thời gian tìm nhau nếu không xem bản đồ và chọn khu từ đầu; đi bộ mỏi chân/chuột rút dù có xe điện, 1 ngày không đi hết.
- `lo_show_gio_mo_cua`: Lỡ hoặc suýt lỡ khung giờ vận hành/đóng cửa (sau 17h các tuyến cáp khác đóng hết chỉ còn cáp Cầu Vàng, quán ăn đóng sớm), show diễn buổi chiều bị huỷ đột xuất, hoặc khu xem show chật chội không có chỗ ngồi phải bỏ ra giữa chừng.
- `tre_nho_chieu_cao_tuoi`: Trò chơi giới hạn chiều cao (`> 1m`) khiến bé nhỏ không chơi được, quá ít trò cho trẻ nhỏ và người lớn tuổi, hoặc gia đình có trẻ nhỏ buộc phải thuê xe đẩy/xe điện riêng.
- `thoi_tiet_mua`: Thời tiết thay đổi rất nhanh từ nắng gắt sang mưa, lạnh, sương mù, hoặc đi vào mùa mưa nên không chơi được nhiều trò ngoài trời.
- `chi_phi_ve`: Giá vé, đồ ăn/nước uống cao hoặc phát sinh phụ phí (fast-track 200k/lượt, chụp ảnh 100k/tấm, cọc xe đẩy 3 triệu, nước suối 25k/chai), hoặc mua vé xong hôm sau có đợt giảm giá.

## 3. Kết quả

Số liệu khớp 100% đầu ra của `python evidence/count.py`:

| Đếm gì | Toàn tập (`N = 50`) | Tập `has_family_kids = true` (`N = 16`) | Sun World Ba Na Hills (`N = 25`) | VinWonders Nha Trang (`N = 25`) | Ghi chú |
|---|---|---|---|---|---|
| `any_pain` (ít nhất 1 pain tag) | 25 / 50 (50.0%) | 9 / 16 (56.2%) | 16 / 25 (64.0%) | 9 / 25 (36.0%) | Nhiều review 4–5 sao vẫn nêu rõ vướng mắc |
| `core_hours_show_or_kids` (`lo_show_gio_mo_cua` HOẶC `tre_nho_chieu_cao_tuoi`) | 8 / 50 (16.0%) | 7 / 16 (43.8%) | 4 / 25 (16.0%) | 4 / 25 (16.0%) | **Vượt ngưỡng ≥15%** trong `hypothesis.md` ngay cả theo nghĩa hẹp nhất |
| `planning_ops_pain` (`lo_show` / `tre_nho` / `di_chuyen_rong` / `xep_hang`) | 20 / 50 (40.0%) | 9 / 16 (56.2%) | 11 / 25 (44.0%) | 9 / 25 (36.0%) | Các vướng mắc ảnh hưởng trực tiếp tới lịch trình 1 ngày |
| `xep_hang_chong_gio` | 13 / 50 (26.0%) | 4 / 16 (25.0%) | 6 / 25 (24.0%) | 7 / 25 (28.0%) | Chờ 30–150 phút, 1 ngày chỉ chơi được ~3 trò hot |
| `di_chuyen_rong` | 10 / 50 (20.0%) | 5 / 16 (31.2%) | 7 / 25 (28.0%) | 3 / 25 (12.0%) | Dễ đi lạc, mỏi chân, cần bản đồ & lộ trình theo khu |
| `chi_phi_ve` | 9 / 50 (18.0%) | 1 / 16 (6.2%) | 5 / 25 (20.0%) | 4 / 25 (16.0%) | Vé >2 triệu, fast-track 200k, cọc xe đẩy 3 triệu, đồ ăn đắt |
| `thoi_tiet_mua` | 8 / 50 (16.0%) | 2 / 16 (12.5%) | 5 / 25 (20.0%) | 3 / 25 (12.0%) | Mưa làm ít trò chơi được, hoặc nắng/lạnh đổi đột ngột |
| `tre_nho_chieu_cao_tuoi` | 5 / 50 (10.0%) | 5 / 16 (31.2%) | 2 / 25 (8.0%) | 3 / 25 (12.0%) | Giới hạn chiều cao >1m, ít trò cho bé nhỏ, cần xe điện |
| `lo_show_gio_mo_cua` | 4 / 50 (8.0%) | 3 / 16 (18.8%) | 2 / 25 (8.0%) | 2 / 25 (8.0%) | Huỷ suất show tiên cá, cáp đóng sau 17h, quán đóng sớm |

**Đối chiếu với ngưỡng giả thuyết (`evidence/hypothesis.md`):**
- Ngưỡng đặt ra: `≥15%` review công khai (trên tập review chi tiết được lọc) phản ánh vướng mắc về lịch trình, giờ mở cửa/show hoặc điểm chơi cho trẻ nhỏ.
- Kết quả thực tế:
  - Theo định nghĩa hẹp nhất (`lo_show_gio_mo_cua` hoặc `tre_nho_chieu_cao_tuoi`): **8 / 50 (16.0%)** trên toàn tập (đạt 16.0% ở cả hai địa điểm) và **7 / 16 (43.8%)** trên tập có nhắc tới gia đình/trẻ nhỏ — **đạt và vượt ngưỡng ≥15%**.
  - Theo định nghĩa đầy đủ về vướng mắc lịch trình/vận hành (`planning_ops_pain`): **20 / 50 (40.0%)** trên toàn tập và **9 / 16 (56.2%)** trên tập gia đình/trẻ nhỏ.

## 4. ≥5 ví dụ cụ thể (trích nguyên văn từ `evidence/reviews_anon.csv`, không đoán ai là ai)

1. **`VN24`** (VinWonders Nha Trang · 3/5 · `has_family_kids=true` · `chi_phi_ve;xep_hang_chong_gio;lo_show_gio_mo_cua;tre_nho_chieu_cao_tuoi`):
   > "Còn bạn nào giống nhà mình ko chơi các trò chơi, xem show Tata thì ngồi dưới đất đông đúc chen chút đổ mồ hôi dc 10p là phải kiếm đường chạy ra. Qua chủ yếu bé em muốn xem show tiên cá mà qua nhận đc thông báo mới thay đổi huỷ xuất biểu diễn buổi chiều xu cà na luôn"
2. **`VN16`** (VinWonders Nha Trang · 4/5 · `has_family_kids=true` · `thoi_tiet_mua;tre_nho_chieu_cao_tuoi`):
   > "Tiếc là đi vào mùa mưa nên k chơi được nhiều. 1 số trò chơi bé phải trên 1 m mới dc chơi nên hạn chế vì đi cùng bé nhỏ"
3. **`BN04`** (Sun World Bà Nà Hills · 5/5 · `has_family_kids=true` · `lo_show_gio_mo_cua;di_chuyen_rong`):
   > "Nên mua vé có bao gồm ăn trưa và nên ăn đúng khung giờ mở cửa. Phong cảnh đẹp không chê vào đâu được. Vì diện tích rộng nên mọi người nhớ lúc nào cũng phải check bản đồ nhé. À còn có xe trung chuyển chở từ parking lot đến chỗ đi cáp treo nhé. Một điều note quan trọng là nếu chơi sau 5h mà muốn xuống thì chỉ có thể đi xuống bằng cáp treo cầu Vàng nhé (những cáp khác đóng cửa hết ời.)"
4. **`BN15`** (Sun World Bà Nà Hills · 2/5 · `has_family_kids=true` · `tre_nho_chieu_cao_tuoi`):
   > "Ngoài chụp ảnh ra chả có gì đáng chơi các trò chơi cho bé wa ít. Nói chung nhà có trẻ con và ng già ko lên cho lên đây."
5. **`VN18`** (VinWonders Nha Trang · 5/5 · `has_family_kids=true` · `thoi_tiet_mua;xep_hang_chong_gio;di_chuyen_rong;tre_nho_chieu_cao_tuoi`):
   > "Nếu đi cùng gia đình, đặc biệt có trẻ nhỏ hoặc người lớn tuổi, nên mua thêm vé xe điện vì khuôn viên cực kỳ rộng. Nhà mình có đi xe điện mà cuối ngày vẫn mỏi chân kinh khủng."
6. **`VN11`** (VinWonders Nha Trang · 4/5 · `has_family_kids=false` · `di_chuyen_rong;chi_phi_ve`):
   > "Các khu vui chơi ở xa nhau. M.n nên chọn khu vui chơi ngay từ đầu, để tránh tốn thời gian di chuyển, vì không những xa mà còn lạc đường, đi lòng vòng. Nếu đi từ sáng thì nên chơi các trò ở xa, cảm giác mạnh, rồi trưa về ăn cơm và chơi các trò ở gần. Vì buffet ở gay gần cổng."
7. **`VN25`** (VinWonders Nha Trang · 3/5 · `has_family_kids=false` · `xep_hang_chong_gio;chi_phi_ve`):
   > "trò tàu lượn oke nhưng xếp hàng mất 2.5 tiếng, nếu biết thực sự lâu như này thì khuyên mng nên mua fast-track 200k/lượt nhé ạ, ngoài ra có chụp ảnh lúc mình trên đường đi nữa, 100k/tấm nha"

## 5. Giới hạn của data

Data cho biết người ta **gặp kết quả gì** (bị huỷ show tiên cá, bé dưới 1m không chơi được, đi lạc/mỏi chân, xếp hàng 1.5–2.5 tiếng, bất ngờ vì cáp đóng sau 17h), nhưng **không** cho biết đầy đủ **vì sao** và bối cảnh trước khi đi:
- **Lệch chọn mẫu (positivity & ranking bias):** Chế độ `Phù hợp nhất` trên Google Maps ưu tiên các review 4–5 sao có nhiều tương tác hoặc khen cảnh quan (`25 / 50 (50.0%)` review không nêu pain nào); đồng thời nhiều phụ huynh đi cùng con nhỏ mệt hoặc bỏ về sớm có thể không viết review dài.
- **Thiếu thông tin quy trình lập kế hoạch trước chuyến đi:** Review không cho biết gia đình đã tra cứu nguồn nào trước đó (web chính thức, app, đại lý, hay đi tuỳ hứng), ngân sách dự trù ban đầu là bao nhiêu, và họ có thực sự muốn dùng một công cụ lên lịch trước hay không.
- **Mốc thời gian thô:** Google Maps hiển thị ngày tương đối (`2 tuần trước`, `4 tháng trước`), chưa tách được đầy đủ tỷ lệ phàn nàn theo ngày cuối tuần/lễ so với ngày thường.

→ **Kiểm lại bằng phỏng vấn:** Phỏng vấn trực tiếp **≥3 phụ huynh ngoài nhóm** (trong thư mục `evidence/interviews/`) đã từng đưa trẻ nhỏ (3–10 tuổi) đi khu vui chơi tổ hợp lớn trong 12 tháng qua để kiểm chứng: (1) nguyên nhân gốc của việc lỡ show/chọn nhầm trò/vượt ngân sách, (2) hành vi tự ứng biến khi gặp mưa hoặc huỷ show, và (3) nhu cầu thực sự đối với lịch trình gợi ý có kiểm tra sẵn chiều cao, độ tuổi, giờ mở cửa và tổng chi phí.
