# Tóm tắt mô phỏng simulate-1@20261127-192829

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| lap_lich_nhanh | 4 | 2 | 5143 | 1712 | 1.5 | 8.5 |
| len_lich_ky | 3 | 3 | 5918 | 1695 | 1.7 | 9.3 |
| xep_lai_dot_xuat | 0 | 4 | — | — | — | — |

Tỉ lệ đạt dùng để tính: 23/25 (92%) — lượt run-2@20261127-185059

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (1.124 người) | Chi phí / tháng — cơ sở (5.620 người) | Chi phí / tháng — cao (10.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| cx/gpt-5.6-luna (vào 0.2 · ra 1.2 $/1M) | $0.0031 | $0.0034 | $0.0014 | $6.59 | $32.95 | $58.62 | $0.0059 |
| gpt-6-luna (vào 0.1 · ra 0.5 $/1M) | $0.0014 | $0.0015 | $0.00063 | $2.94 | $14.70 | $26.16 | $0.0026 |
| gpt-5.6-terra (vào 2.0 · ra 12.0 $/1M) | $0.0314 | $0.0341 | $0.0141 | $65.89 | $329.47 | $586.24 | $0.0586 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (2.4) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: cx/gpt-5.6-luna. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 43/50.
