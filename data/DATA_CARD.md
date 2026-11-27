# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

**Bản đầu CP2 · phụ trách: Trần Quốc Tuấn · ngày 27/11/2026.**

Toàn bộ dữ liệu trong `data/park/` là **dữ liệu lai** về VinWonders Nha Trang:
- **Phần thật:** tên khu, giờ mở cửa, giá vé, tên trò, giờ trò, ngưỡng chiều cao/cân nặng/tuổi. Đọc từ 3 trang chính thức của vinwonders.com, xem ngày 27/11/2026.
- **Phần synthetic:** lịch show, thời gian chờ, thời lượng, trong nhà/ngoài trời, thời gian đi bộ, kịch bản mưa. Nhóm tự dựng để có đủ tình huống thử.

Mỗi bản ghi có hai trường đánh dấu:
- `src`: mã nguồn, tra trong `data/park/park.json` → `sources`.
- `verified`: danh sách trường lấy từ nguồn thật. Trường không có trong `verified` là synthetic.

**Cách sinh phần synthetic:** dựng tay, không sinh ngẫu nhiên bằng script hay prompt, nên **không có seed**. Dữ liệu cố định trong file JSON, chạy lại luôn ra cùng kết quả.

Trò hoặc show hoàn toàn tự dựng có hậu tố **"(mẫu)"** trong tên. **Data này không phải bằng chứng pain.** Bằng chứng nằm ở `evidence/`.

| Mã nguồn | Trang | Ngày trên trang |
|---|---|---|
| `W_RULES` | https://vinwonders.com/vi/wonderpedia/news/quy-dinh-tro-choi-vinwonders-nha-trang/ | 21/07/2026 |
| `W_PRICE` | https://vinwonders.com/vi/wonderpedia/news/bang-gia-ve-vinwonders-nha-trang-cap-nhat/ | 01/01/2026 |
| `W_HOURS` | https://vinwonders.com/vi/wonderpedia/news/vinwonders-nha-trang-gio-mo-cua/ | 01/01/2026 |

## Dataset 1 · Thông tin khu và các phân khu (`data/park/park.json`)

| | |
|---|---|
| Dùng để làm gì | Nguồn cho công cụ kiểm giờ mở cửa và danh sách khu. Chứa luôn bảng mã nguồn cho mọi file khác |
| Từ đâu | `W_HOURS`: giờ 09:00–20:00, địa chỉ, tên 6 khu. Nút cổng vào `GATE` là synthetic |
| Xử lý những bước gì | Chép tay, đặt mã khu tiếng Anh (`FAIRY_LAND`…) |
| Số dòng | 1 khu · 6 phân khu · 1 cổng vào |
| Phiên bản / ngày lấy | v1 · 27/11/2026 |
| Nhãn | lai: thật + `synthetic` |
| Giới hạn | Một bài khác của VinWonders ghi giờ mở 08:30. Giờ công viên nước 10:00–17:30 chưa đọc được nguyên văn |

## Dataset 2 · Trò chơi (`data/park/attractions.json`)

| | |
|---|---|
| Dùng để làm gì | Nguồn cho công cụ lọc trò theo chiều cao/tuổi/giờ. Dùng cho câu thử về an toàn trẻ em |
| Từ đâu | **A01–A07 thật** (`W_RULES`): tên, khu, giờ, chiều cao tối thiểu, cân nặng, tuổi. **A08–A11:** tên có trên web, chi tiết synthetic. **A12–A18:** hoàn toàn synthetic |
| Xử lý những bước gì | Chép tay. "Dưới 50 tuổi" ghi thành `max_age: 49`. Các trường `duration_min`, `avg_wait_min`, `indoor`, `closes_in_rain`, `status` luôn tự ước tính. Trường `status` (`open` / `maintenance`) thêm theo P5 ("đi tới nơi mới biết trò bảo trì"). Web không công bố lịch bảo trì, nên `maintenance` **chỉ đặt cho trò "(mẫu)"** (A16, A17), không gán cho trò thật |
| Số dòng | 18 trò: 7 thật · 4 lai · 7 synthetic |
| Phiên bản / ngày lấy | v1 · 27/11/2026 |
| Nhãn | lai |
| Giới hạn | Chưa có danh sách trò đầy đủ của khu, nên số trò cho trẻ dưới 100cm bị thiếu và phải bù bằng trò "(mẫu)". Zipline không gồm trong vé nhưng không có giá lẻ: `extra_fee_vnd: null`, công cụ phải báo "không có giá" |

## Dataset 3 · Lịch show (`data/park/shows.json`)

| | |
|---|---|
| Dùng để làm gì | Nguồn cho công cụ tra suất show và kiểm chồng giờ |
| Từ đâu | **Giờ suất đều synthetic.** Trang `W_HOURS` đăng lịch biểu diễn dạng ảnh, không đọc được. Tên Tata Show, show nàng tiên cá, show cho cá ăn có nhắc trên web (chưa kiểm nguyên văn) |
| Xử lý những bước gì | Tự dựng. Cài sẵn xung đột: show nàng tiên cá 15:00 (Sea World) sát show chim 15:30 (King's Garden), hai khu cách nhau 20 phút đi bộ |
| Số dòng | 6 show |
| Phiên bản / ngày lấy | v1 · 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | Không phản ánh lịch thật. Demo phải nói rõ "lịch show mẫu" |

## Dataset 4 · Giá vé (`data/park/tickets.json`)

| | |
|---|---|
| Dùng để làm gì | Nguồn cho công cụ tính tổng chi phí. Tiền **do code tính**, model không tự cộng |
| Từ đâu | `W_PRICE`, chép nguyên văn: 4 loại vé × 4 nhóm khách (người lớn ≥140cm · trẻ 100–<140cm · người cao tuổi ≥60 · trẻ <100cm miễn phí), gồm cáp treo 2 chiều |
| Xử lý những bước gì | Bỏ combo (buffet, buggy, VIP, WONDER15) vì trang không ghi rõ tính theo người. Bỏ bảng giá khuyến mãi đã hết hạn 11/02/2026 |
| Số dòng | 4 loại vé × 4 nhóm |
| Phiên bản / ngày lấy | v1 · 27/11/2026 |
| Nhãn | thật |
| Giới hạn | Giá có thể đổi theo mùa hoặc khuyến mãi. Vé 3 ngày trẻ em lệch giữa hai trang (1.050.000 và 1.200.000), file dùng `W_PRICE`. Không có giá lẻ Zipline hay combo |

## Dataset 4b · Dịch vụ thu phí lẻ (`data/park/services.json`)

| | |
|---|---|
| Dùng để làm gì | Nguồn cho công cụ tính ngân sách, tách rõ khoản trong vé và phí lẻ phát sinh (canvas CP2, từ P2, P3, P4) |
| Từ đâu | Tên dịch vụ theo lời phụ huynh kể: cho thú ăn, xe điện (P4) · tủ locker (P3) · áo mưa (P2). Xe buggy và Zipline có tên trên web. **Không lấy từ bảng giá VinWonders** |
| Xử lý những bước gì | Giá SV01, SV03, SV04 là *(tự ước tính)*. SV02 (buggy) và SV05 (Zipline) để `price_vnd: null` vì không có giá lẻ công khai. Không suy giá từ combo |
| Số dòng | 5 dịch vụ: 3 có giá *(tự ước tính)* · 2 không có giá |
| Phiên bản / ngày lấy | v1 · 27/11/2026 |
| Nhãn | `synthetic` (tên SV02, SV05 thật) |
| Giới hạn | Giá không phải giá thật. Câu áo mưa của P2 là chuyện ở Sun World Bà Nà, chỉ dùng làm kịch bản mưa |

## Dataset 5 · Thời gian đi bộ (`data/park/travel_times.json`)

| | |
|---|---|
| Dùng để làm gì | Nguồn cho công cụ tính thời gian di chuyển giữa các khu khi xếp lịch |
| Từ đâu | Nhóm tự ước tính cho gia đình đi chậm |
| Xử lý những bước gì | Ma trận 7×7, đối xứng. Trong cùng một khu tính 5 phút |
| Số dòng | 7 nút |
| Phiên bản / ngày lấy | v1 · 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | Không dựa trên bản đồ thật, chưa tính xe buggy |

## Dataset 6 · Kịch bản thời tiết (`data/park/weather.json`)

| | |
|---|---|
| Dùng để làm gì | Thử việc xếp lại lịch khi mưa: đóng trò ngoài trời, huỷ show ngoài trời |
| Từ đâu | Nhóm tự dựng. Các trang đã đọc không có quy định khi mưa |
| Xử lý những bước gì | 4 kịch bản: nắng · mưa chiều 14–16h · mưa tối 18:30–20h · mưa cả ngày |
| Số dòng | 4 kịch bản |
| Phiên bản / ngày lấy | v1 · 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | Không phải dự báo thật. Quy tắc đóng trò khi mưa là giả định của nhóm |

**Kiểm:**
- Phần thật được trích từ trang nguồn bằng công cụ AI (Claude Code), xem `docs/ai-usage.md`.
- **Chưa có người đối chiếu tay.** Trước CP3, Tuấn cần mở 3 link trên và so A01–A07 cùng bảng giá.
- Script kiểm tính nhất quán đã chạy ngày 27/11/2026, không lỗi: mã khu, mã nguồn, ma trận đối xứng, giờ trò nằm trong giờ mở cửa.
