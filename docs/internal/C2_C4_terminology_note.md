# Ghi chú nội bộ — Thuật ngữ cold-start P0 vs luận án (C2/C4)

**Ngày:** 2026-07-22 (theo nhận xét PGS. Nguyễn Văn Hậu, mục B6)

## P0 (bài APIN)

- **Cold-start** = phân tầng theo **tần suất tương tác train** trên KC: S1 very_cold ($n_f<20$), S2 cold, S3 warm, S4 hot.
- KC **không có** tương tác train **không** nằm trong bảng tần suất → bị loại khỏi aggregate stratum (hoặc xuất hiện dưới nhãn *out of range* nếu held-out KC không map được bin).
- Đây là **frequency-stratum diagnostic**, không phải split zero-interaction / zero-shot.

## Luận án (roadmap v8.0)

- **Sparse** = ít tương tác (gần với P0 cold/very_cold).
- **Cold-start (luận án)** = **zero interaction** trên train (user/item/KC chưa thấy).

## Quy tắc khi viết C2/C4

1. **Không** trích tầng `very_cold` của P0 như thể đó là cold-start zero-shot của luận án.
2. Khi so sánh với P0, nêu rõ: *"P0 frequency-stratum very_cold ($n_f<20$), not dissertation zero-interaction cold-start."*
3. Nếu C2/C4 dùng zero-interaction split, thiết kế thí nghiệm riêng; không tái sử dụng số AUC Junyi very_cold P0 (đã suppress trong bảng vì suy biến thống kê).
