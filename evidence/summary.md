# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☑ | `evidence/data-mining.md` · `evidence/count.py` · `evidence/reviews_anon.csv` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng — đã có 5/5) | ☑ | `evidence/interviews/P1.md`…`P5.md` |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☐ *(không dùng)* | `evidence/survey/` |

## 2. Số chính

- **Đào data** (`python evidence/count.py` trên `N = 50` review công khai Google Maps tại Sun World Bà Nà Hills và VinWonders Nha Trang, trong đó `N_family = 16` review nhắc tới gia đình/trẻ nhỏ):
  - `any_pain` (có ≥1 vướng mắc): **25 / 50 (50.0%)** toàn tập · **9 / 16 (56.2%)** tập gia đình/trẻ nhỏ.
  - `planning_ops_pain` (lỡ show/giờ mở cửa, chiều cao/tuổi trẻ nhỏ, di chuyển rộng, xếp hàng): **20 / 50 (40.0%)** toàn tập · **9 / 16 (56.2%)** tập gia đình/trẻ nhỏ.
  - `core_hours_show_or_kids` (nghĩa hẹp trong giả thuyết — `lo_show_gio_mo_cua` hoặc `tre_nho_chieu_cao_tuoi`): **8 / 50 (16.0%)** toàn tập (đều **4 / 25 = 16.0%** ở cả hai địa điểm, vượt ngưỡng ≥15%) · **7 / 16 (43.8%)** tập gia đình/trẻ nhỏ.
  - Từng nhóm vướng mắc: `xep_hang_chong_gio` **13 / 50 (26.0%)** · `di_chuyen_rong` **10 / 50 (20.0%)** *(gia đình: 5/16 = 31.2%)* · `chi_phi_ve` **9 / 50 (18.0%)** · `thoi_tiet_mua` **8 / 50 (16.0%)** · `tre_nho_chieu_cao_tuoi` **5 / 50 (10.0%)** *(gia đình: 5/16 = 31.2%)* · `lo_show_gio_mo_cua` **4 / 50 (8.0%)** *(gia đình: 3/16 = 18.8%)*.
- **Phỏng vấn:** **5/5 người** gặp ít nhất 1 sự cố làm vỡ lịch/đổi điểm chơi hoặc phát sinh chi phí khi đi khu vui chơi cùng trẻ nhỏ *(n nhỏ không ghi %)* — trong đó **3/5 người (P1, P3, P5)** đã chuẩn bị lịch trước **30–90 phút** vẫn gặp sự cố (lỡ show, xếp chồng giờ do thiếu thời gian đệm, vướng giới hạn chiều cao hoặc trò bảo trì), và **2/5 người (P2, P4)** xem nhanh **10–20 phút** vẫn bị động khi mưa/đông và phát sinh chi phí lẻ.
- **Khảo sát:** không dùng.

Phỏng vấn nhiều vai thì đếm theo từng vai, không cộng chung.

| | Vai | Gặp pain? | Số lần / 1 tháng qua | Lần gần nhất mất | Đang xoay xở bằng |
|---|---|---|---|---|---|
| P1 | Phụ huynh (2 bé 4 & 7 tuổi) | Có | Chưa hỏi rõ *(lần gần nhất: ~2 tháng trước)* | 90 phút chuẩn bị tối hôm trước | Bản đồ giấy + hỏi nhân viên dọc đường (ngại mở app dưới nắng) |
| P2 | Phụ huynh (1 bé 6 tuổi, đi cùng ông bà) | Một phần | Chưa hỏi rõ *(lần gần nhất: dịp nghỉ lễ gần đây)* | 20 phút lướt clip; 45 phút chờ cáp treo | Đi tới đâu hay tới đó + hỏi nhân viên điều phối |
| P3 | Phụ huynh (2 bé 3 & 9 tuổi) | Có | Chưa hỏi rõ *(lần gần nhất: mùa hè vừa rồi)* | 60 phút lập ghi chú; trễ 40 phút tắm/thay đồ | App xem giờ show + bản đồ giấy |
| P4 | Phụ huynh (1 bé 5 tuổi) | Một phần | Chưa hỏi rõ *(lần gần nhất: cuối tuần tháng trước)* | 10 phút lướt fanpage sáng hôm đi | Biển chỉ dẫn + hỏi bảo vệ (lười tải app mới) |
| P5 | Phụ huynh (2 bé sinh đôi 8 tuổi) | Có | Chưa hỏi rõ *(lần gần nhất: đầu tháng trước)* | 30 phút trao đổi qua Zalo | Hỏi nhân viên ở cổng về trò bảo trì + chụp ảnh bản đồ lớn |

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. "Bị lỡ show Nàng tiên cá ở Cung điện Hải Vương vì hai bé mải chơi khu trò chơi trong nhà, lúc nhìn đồng hồ chạy ra thì đã hết giờ." — P1
2. "Khoảng 2 giờ chiều trời bất ngờ đổ sương mù dày đặc rồi mưa phùn. Khu xe trượt ống ngoài trời phải tạm dừng hoạt động." — P2
3. "Ước lượng sai thời gian \"chết\" — tức là thời gian di chuyển giữa các khu, thời gian trẻ đi vệ sinh, thay đồ, ăn nhẹ. Nhìn lịch show trên giấy thì thấy rất hợp lý nhưng thực tế chạy không bao giờ kịp." — P3
4. "Ngoài ra, một số dịch vụ bên trong không nằm trong vé trọn gói (như cho thú ăn, xe điện, một vài trò chơi lẻ) khiến mình cứ phải dừng lại hỏi giá và mua thêm vé lẻ khá lắt nhắt." — P4
5. "Hụt hẫng và mất công nhất là lặn lội đi tới tận khu trò chơi rồi mới biết trò đóng cửa bảo trì hoặc yêu cầu chiều cao khắt khe hơn mình nghĩ. Hai đứa trẻ con bị hụt hẫng nên dễ cáu gắt cả buổi sau đó." — P5
6. "Còn bạn nào giống nhà mình ko chơi các trò chơi, xem show Tata thì ngồi dưới đất đông đúc chen chút đổ mồ hôi dc 10p là phải kiếm đường chạy ra. Qua chủ yếu bé em muốn xem show tiên cá mà qua nhận đc thông báo mới thay đổi huỷ xuất biểu diễn buổi chiều xu cà na luôn" — dòng data `VN24` (`evidence/reviews_anon.csv`)
7. "Tiếc là đi vào mùa mưa nên k chơi được nhiều. 1 số trò chơi bé phải trên 1 m mới dc chơi nên hạn chế vì đi cùng bé nhỏ" — dòng data `VN16` (`evidence/reviews_anon.csv`)
8. "Vì diện tích rộng nên mọi người nhớ lúc nào cũng phải check bản đồ nhé. À còn có xe trung chuyển chở từ parking lot đến chỗ đi cáp treo nhé. Một điều note quan trọng là nếu chơi sau 5h mà muốn xuống thì chỉ có thể đi xuống bằng cáp treo cầu Vàng nhé (những cáp khác đóng cửa hết ời.)" — dòng data `BN04` (`evidence/reviews_anon.csv`)

## 4. Các nguồn có khớp nhau không

- **Khớp nhau:** Hai nguồn độc lập (đào 50 review Google Maps trong `evidence/data-mining.md` và phỏng vấn 5 phụ huynh `P1–P5`) cùng xác nhận 5 nhóm vướng mắc cốt lõi của gia đình có trẻ nhỏ:
  1. *Giới hạn chiều cao/độ tuổi trẻ nhỏ:* **5/16 (31.2%)** review gia đình (`VN16`, `BN15`) ↔ **P1** (bé 4 tuổi dưới 1m2 không chơi được tàu lượn), **P5** (chiều cao khắt khe hơn dự tính).
  2. *Lỡ show / huỷ show / giờ đóng cửa:* **3/16 (18.8%)** review gia đình (`VN24`, `BN04`) ↔ **P1** (lỡ show Nàng tiên cá), **P3** (trễ show chim vì tắm tráng 40 phút).
  3. *Khuôn viên rộng, di chuyển mất sức:* **5/16 (31.2%)** review gia đình (`VN18`, `VN11`) ↔ **P1** (đẩy xe đẩy đi bộ 10 phút dưới nắng), **P2** (đường dốc cho ông bà), **P3** (sai thời gian di chuyển giữa các khu).
  4. *Thời tiết mưa làm gián đoạn lịch:* **8/50 (16.0%)** toàn tập (`VN16`) ↔ **P2** (sương mù/mưa lúc 14h làm dừng xe trượt ống, phải dồn vào khu trong nhà).
  5. *Phát sinh chi phí ngoài vé chính:* **9/50 (18.0%)** toàn tập (`VN25`) ↔ **P2, P3, P4, P5** (áo mưa, locker/khăn tắm, xe điện nội khu, cho thú ăn, túi chống nước/dép).
- **Chỗ lệch & giải thích:**
  1. *Tỷ lệ pain trong review thấp hơn trong phỏng vấn:* Review trên Google Maps chịu `positivity & ranking bias` (chế độ *Phù hợp nhất* ưu tiên review 4–5★ khen cảnh quan, **25/50 = 50.0%** không nêu pain nào; nhóm gia đình có **9/16 = 56.2%** nêu pain), trong khi phỏng vấn hỏi thẳng vào lần đi gần nhất giúp phát hiện **5/5** gia đình đều gặp ít nhất 1 tình huống vỡ lịch hoặc phát sinh chi phí.
  2. *Vai trò nguyên nhân gốc:* Data review nêu mạnh hiện tượng **xếp hàng dài** (**13/50 = 26.0%**, chờ 30–150 phút) nhưng không nói rõ họ chuẩn bị thế nào trước khi đi; phỏng vấn bổ sung phần *vì sao* còn thiếu: phụ huynh tự chuẩn bị mất **30–90 phút** (`P1`, `P3`, `P5`) nhưng không ước lượng được thời gian đệm (`P3`), không biết trò bảo trì (`P5`), và ngại tải/mở app liên tục dưới nắng (`P1`, `P4`).

## 5. Kết luận

Giả thuyết ở `evidence/hypothesis.md`: **đúng và được xác nhận bởi cả 2 nguồn đạt ngưỡng** — trên data review công khai, tỷ lệ vướng mắc vượt ngưỡng `≥15%` ở cả nghĩa hẹp (**8/50 = 16.0%** toàn tập; **7/16 = 43.8%** tập gia đình) lẫn nghĩa lịch trình/vận hành (**20/50 = 40.0%** toàn tập; **9/16 = 56.2%** tập gia đình); qua phỏng vấn, **3/5** phụ huynh tự lập lịch 30–90 phút trước vẫn vỡ lịch và **5/5** gặp sự cố đổi điểm/phát sinh chi phí.

Điều vẫn chưa biết (giới hạn trung thực): (1) thời gian xếp hàng theo giờ thực tại từng trò chưa có dữ liệu công khai liên tục (hệ thống dùng thời lượng chơi/di chuyển từ dữ liệu mẫu và báo rõ giới hạn); (2) tần suất đi khu vui chơi tính theo *tháng* ở cấp từng hộ gia đình chưa hỏi trực tiếp trong `P1–P5` (vì phần lớn gia đình đi theo dịp lễ/hè/cuối tuần) nên sẽ ước tính thận trọng và ghi rõ `*(tự ước tính)*` trong `spec.md` §2 và `cost/personas.yaml`.

## Lịch hẹn (dùng cho CP2 — chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| Phụ huynh (2 bé 4 & 7 tuổi) — P1 | 27/11/2026 (đã hỏi) | Xong |
| Phụ huynh (1 bé 6 tuổi, đi cùng ông bà) — P2 | 27/11/2026 (đã hỏi) | Xong |
| Phụ huynh (2 bé 3 & 9 tuổi) — P3 | 27/11/2026 (đã hỏi) | Xong |
| Phụ huynh (1 bé 5 tuổi) — P4 | 27/11/2026 (đã hỏi) | Xong |
| Phụ huynh (2 bé sinh đôi 8 tuổi) — P5 | 27/11/2026 (đã hỏi) | Xong |
