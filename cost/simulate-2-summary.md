# Tóm tắt mô phỏng simulate-2@20261127-215027

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| lap_lich_nhanh | 24 | 2 | 6020 | 1822 | 1.8 | 10.2 |
| len_lich_ky | 18 | 3 | 7470 | 2327 | 2.2 | 13.0 |
| xep_lai_dot_xuat | 8 | 4 | 11677 | 3704 | 3.5 | 18.5 |

Tỉ lệ đạt dùng để tính: 23/25 (92%) — lượt run-2@20261127-185059

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (1.124 người) | Chi phí / tháng — cơ sở (5.620 người) | Chi phí / tháng — cao (10.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| cx/gpt-5.6-luna (vào 0.2 · ra 1.2 $/1M) | $0.0043 | $0.0046 | $0.0017 | $9.25 | $46.25 | $82.30 | $0.0082 |
| gpt-6-luna (vào 0.1 · ra 0.5 $/1M) | $0.0019 | $0.0021 | $0.00077 | $4.12 | $20.62 | $36.68 | $0.0037 |
| gpt-5.6-terra (vào 2.0 · ra 12.0 $/1M) | $0.0426 | $0.0463 | $0.0173 | $92.50 | $462.51 | $822.96 | $0.0823 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (2.7) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: cx/gpt-5.6-luna. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
