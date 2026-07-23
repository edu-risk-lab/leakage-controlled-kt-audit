# Audit Report: Server B Injection History

## 1. Tóm tắt (Summary)
- **Trạng thái thực thi injection**: KHÔNG CÓ job injection nào từng được chạy trên Server B (0/6 job hoàn thành).
- Mọi nỗ lực tìm kiếm log, cache, git stash và file lưu trữ đều không cho thấy dấu vết của job injection hay script sinh đồ thị injection được chạy thành công.

## 2. Bảng Artifact & Bảng THIẾU (Missing Artifacts)
Tất cả các artifacts liên quan đến bài test injection đều đang bị **THIẾU** trên Server B:

| Artifact Type | Expected Path / Pattern | Trạng thái (Server B) |
|---|---|---|
| **Cache JSON** | `results/cache/xes3g5m_fold_0_*_s42_inject*_result.json` | ❌ Thiếu (0/6 files) |
| **Checkpoints** | `results/pykt_work/xes3g5m/fold_0_seed_42/inject05/` & `inject20/` | ❌ Thiếu (0/6 ckpts) |
| **Graph files** | `data/processed/xes3g5m/fold_0/e_pre_inject05.csv` & `e_pre_inject20.csv` | ❌ Thiếu (chỉ có train_only) |
| **Logs** | Trong folder `logs/` (tìm kiếm từ khóa "inject") | ❌ Không có |

*(Ghi chú: Lệnh dry-run `python -m scripts.run_injection_auc` và `build_injected_graphs()` bị lỗi crash ngay từ đầu do thiếu thư viện `pyarrow` / `fastparquet` trên environment `C:\TUAN\p0_project\.venv`)*

## 3. GPU Environment (Server B)
- **GPU Card**: NVIDIA RTX A5000 Laptop GPU
- **VRAM**: 16384 MiB (16GB)
- **CUDA Version**: 13.2
- **Driver Version**: 596.36
- **Workspace Path**: `C:\TUAN\p0_project`

## 4. Khuyến nghị (Recommendations)
1. **Khuyến nghị A (Giải quyết Dependency)**: Cần cài đặt `pyarrow` (`pip install pyarrow`) trên Server B để script load được `xes3g5m.parquet` khi gọi `build_injected_graphs()`.
2. **Khuyến nghị B (Xử lý Primary Checkpoints)**: Vì Server B hiện **không có** primary checkpoints của `train_only` (xem Phụ lục), ta phải quyết định: (1) Tìm và copy primary checkpoints từ nơi khác về Server B, HOẶC (2) Chạy train lại base models (train_only) trên Server B.
3. **Khuyến nghị C (Thực hiện Rerun)**: Do các con số trên Server A chỉ là placeholder và Server B chưa từng chạy, tôi đề xuất xin phép **Rerun toàn bộ 6 job injection** (cùng quá trình gen graph) trên máy này để tạo ground-truth, sau khi đã hoàn thành bước B.

## Phụ lục (Appendix): Tình trạng Checkpoint Primary XES / DDR Seed 42
- Kiểm tra tại `results/pykt_work/xes3g5m/fold_0_seed_42/train_only/`: **KHÔNG TÌM THẤY** file `gkt_p0_protocol_best.ckpt` hay bất cứ file `.ckpt` nào khác. Chỉ tồn tại các cache files (`gkt_graph_p0_protocol.npz`, `test_sequences.csv...`).
- => **Kết luận:** Server B không lưu giữ file checkpoint gốc XES seed 42 (Jun 2026). Có khả năng file checkpoint đã bị xóa, hoặc nó vốn chỉ được train/lưu ở một máy tính khác chưa được sync lên.
