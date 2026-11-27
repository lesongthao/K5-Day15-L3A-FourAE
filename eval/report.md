# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử 25 câu (`eval/benchmark.csv`), cùng chuẩn "đạt" (`spec.md` §7) và cùng model `cx/gpt-5.6-luna`. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` và `python run.py score eval/run-2.csv`.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261127-182508` | 16/25 | 64% | 4/9 (44%) | 8/12 (67%) | 4/4 (100%) | Chưa đạt (<80%; đạt 3/3 điều kiện cứng) |
| 2 | `run-2@20261127-185059` | 23/25 | 92% | 9/9 (100%) | 10/12 (83%) | 4/4 (100%) | **Đạt** (≥80%; 0 vi phạm cứng; 4/4 `tu_choi`) |

- **Hiệu năng & token qua 2 lượt (cả 25 câu, 0 lỗi kỹ thuật):**
  - Lượt 1: `28` lần gọi model · `94` lần gọi tool · `86,758` token vào + `23,877` token ra = **`110,635` token** · tổng thời gian `480.941s`.
  - Lượt 2: `18` lần gọi model · `104` lần gọi tool · `60,403` token vào + `18,481` token ra = **`78,884` token** (giảm **28.7%**) · tổng thời gian `367.488s` (giảm **23.6%**).
- Kết quả từng câu: [eval/run-1.csv](eval/run-1.csv), [eval/run-2.csv](eval/run-2.csv). Trace: [traces/run-1.jsonl](traces/run-1.jsonl), [traces/run-2.jsonl](traces/run-2.jsonl).

## 2. Lỗi lượt 1 — gom thành nhóm có tên

Tổng cộng **9/25 câu trượt** ở Lượt 1 (100% câu an toàn `tu_choi` đều đạt `4/4`), chia thành 3 nhóm lỗi gốc:

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| Thiếu chi phí/giá dịch vụ trong `context` & pre-check bỏ sót phụ thu | 4 | `B03`, `B06`, `B22`, `B23` |
| Thiếu ma trận di chuyển (`travel_times`) & đệm 20p CVN trong `context` hoặc tự bỏ cuộc khi sửa xung đột | 3 | `B01`, `B10`, `B17` |
| Xếp lịch hợp lệ nhưng bỏ sót điểm/show khách chỉ định | 2 | `B18`, `B19` |

**4 lỗi cụ thể ở Lượt 1:**

| Câu | Input | Output (rút gọn) | Vì sao sai |
|---|---|---|---|
| `B01` (`thuong`) | 2 người lớn, 1 bé 7t cao 115cm, 3.5tr, 09:00–18:00, thích thủy cung & công viên nước | `"Không xếp được lịch trình thỏa mãn toàn bộ ràng buộc. Lý do: - Thiếu thời gian di chuyển từ A11 (KINGS_GARDEN) sang A14 (TROPICAL_PARADISE): cần 25p, chỉ có 0p."` | Model không nhận được ma trận `travel_times` trong `context`, đoán sai khoảng cách khiến hết 3 vòng sửa vẫn lỗi 25p di chuyển. |
| `B03` (`thuong`) | 2 người lớn, 1 bé 5t cao 108cm, 3.5tr, thêm cho thú ăn `SV01` & hỏi giá buggy `SV02` | `"Không xếp được lịch trình phù hợp. Gợi ý: Không có giá công khai trong căn cứ cho SV01... Không có dữ liệu giá vé STANDARD trong căn cứ..."` | `context` chưa truyền kết quả `chi_tiet_chi_phi` đã tính từ `kiem_lich_trinh` và giá `SV01` (`50.000đ`), làm model tưởng thiếu giá vé `STANDARD` rồi bỏ cuộc. |
| `B18` (`thuong`) | 2 người lớn, 1 bé 6t cao 112cm, 3.5tr, 10:00–20:00, muốn đi Thủy cung, Vườn thú và Tata Show buổi tối | Xuất lịch chỉ gồm `A08` (10:00–11:00) và `A11` (11:20–12:20), tổng `2,900,000đ` | Lịch đạt `hop_le=True` về mặt thời gian/giá nhưng bỏ sót yêu cầu bắt buộc của người dùng là xem `S01` Tata Show (`19:30`). |
| `B23` (`kho`) | 2 người lớn, 1 bé 7t cao 120cm, ngân sách 2.920.000đ, thêm `SV01` (`50k`) + `SV03` (`50k`) | `"Không xếp được lịch trình phù hợp. Gợi ý: Căn cứ chưa cung cấp giá vé STANDARD và giá của SV01, SV03..."` | Pre-check ở `agent.py` chỉ kiểm `ve_cong > ngan_sach` (`2.9M <= 2.92M`), bỏ sót `tong_tien_vnd` (`3.0M > 2.92M`), và `context` không có giá để model báo vượt `80.000đ`. |

## 3. Một lần cải tiến

- **Nhắm vào nhóm lỗi:** Thiếu căn cứ chi phí, ma trận di chuyển và các mục bảo trì/ngoài vé trong `context` kèm pre-check thiếu phụ thu (`7/9` câu trượt Lượt 1) + nhắc giữ mục khách yêu cầu (`2/9` câu trượt). **Vì sao là nhóm đau nhất với người dùng:** Phụ huynh cần một lịch trình có thể đi được ngay (đủ giờ di chuyển giữa các khu xa như `King's Garden` ↔ `Tropical Paradise` + 20p thay đồ cho trẻ, giữ đúng show gia đình mong muốn, và chốt đúng tổng tiền kể cả dịch vụ lẻ) — nếu hệ thống báo "không xếp được" giả tạo hoặc bỏ sót show thì người dùng mất 30–90 phút chuẩn bị mà vẫn không có lịch dùng được (đúng pain của `P1`, `P3`, `P4` và `VN11`, `VN24`).
- **Đã sửa gì (commit `d9cb135` ở `codebase/agent.py`, `codebase/request_parser.py`, `codebase/tools.py`):**
  1. Nâng `_build_context()` nén gọn `diem_choi`/`shows`, truyền trực tiếp `chi_phi_code_da_tinh` (loại vé, vé cổng, phụ thu, tổng tiền, trạng thái đủ ngân sách), `dich_vu_le_bang_gia`, `diem_bao_tri_va_ngoai_ve` (`A16`, `A17`, `A01`/`SV05`), và ma trận `di_chuyen_va_dem` (kèm `20p` đệm rời `TROPICAL_PARADISE`).
  2. Sửa pre-check ngân sách dùng `pre["tong_tien_vnd"] > parsed["ngan_sach_vnd"]` để chặn đúng ca vượt ngân sách do dịch vụ lẻ (`B23`).
  3. Cập nhật `SYSTEM` prompt và thông báo sửa lịch (repair): cấm tự báo thiếu giá hoặc đặt `khong_xep_duoc=true` khi vẫn xếp được phương án thay thế hợp lệ, và yêu cầu giữ đủ các mục khách chỉ định nếu hợp lệ.
- **Kết quả:** Nhóm lỗi thiếu context/pre-check giảm từ `7` câu xuống còn `1` câu (`B22`); nhóm bỏ sót mục khách yêu cầu giảm `2/2 → 0/2` (`B18`, `B19` đều đạt); tổng tỷ lệ đạt tăng **`64% (16/25) → 92% (23/25)`** (trong đó `thuong` **4/9 → 9/9 = 100%**, `kho` **8/12 → 10/12 = 83%**, `tu_choi` giữ **4/4 = 100%**).
- **Câu nào tệ đi sau khi sửa:** **Không có câu nào tệ đi** (`16/16` câu đạt ở Lượt 1 đều tiếp tục đạt ở Lượt 2).

## 4. Còn lại

- **Lỗi chưa sửa ở Lượt 2 (2 câu):**
  1. **`B06` (`kho` — lỗi `request_parser.py`):** Input ghi `"2 bé 8 tuổi cao 125cm"` nhưng `_extract_heights()` chỉ bắt được 1 giá trị `125cm` rồi tạo `1` phần tử `CHILD` trong `nhom_khach`, dẫn tới tính vé cổng `2.900.000đ` thay vì `3.700.000đ` (thiếu `800.000đ` của bé thứ 2). **Mức độ nguy hiểm:** Gia đình đông con có cùng chiều cao (hoặc cặp sinh đôi như `P5`) bị báo hụt tiền vé ở cổng.
  2. **`B22` (`kho` — lỗi hành vi model với `EVENING_RAIN`):** Input yêu cầu đi `16:00–20:00` khi mưa tối (`18:30–20:00`) và muốn xem `S01` Tata Show (`19:30`). Model nhận diện đúng `S01` bị huỷ và cảnh báo `A09`, nhưng vẫn trả `khong_xep_duoc=true` thay vì xuất lịch trong nhà thay thế (`A08`, `A03`, `A10`, `A13`, `S06`) với tổng vé `AFTER_16H` `1.950.000đ`. **Mức độ nguy hiểm:** Thấp về an toàn (không gợi ý mục nguy hiểm), nhưng làm trải nghiệm cụt khi trời mưa buổi tối.
  - *Lưu ý nhỏ ở `B17` (`thuong`, vẫn đạt):* Chuỗi `"áo mưa"` trong input làm bộ tách từ khóa `"mưa" in low` kích hoạt kịch bản `AFTERNOON_RAIN` dù khách chỉ xin áo mưa dự phòng (vẫn xếp được lịch hợp lệ `4.530.000đ`, nên giữ điểm đạt nhưng cần tách regex tránh khớp `"áo mưa"`).
- **Nếu có thêm 1 tuần:**
  1. Sửa `request_parser.py` bắt số lượng bé (`"2 bé ... cao 125cm"`) khi chỉ có 1 chiều cao để nhân bản đủ số khách, và dùng word-boundary tránh `"áo mưa"` kích hoạt kịch bản mưa.
  2. Thêm hướng dẫn fallback khi toàn bộ show buổi tối bị huỷ do `EVENING_RAIN` để model luôn gợi ý lịch trong nhà thay thế thay vì dừng ở `khong_xep_duoc=true`.
  3. Mở rộng dữ liệu thật sang thêm các khu vui chơi lớn khác (như Sun World Bà Nà Hills, VinWonders Phú Quốc) để dùng chung cùng kiến trúc.
