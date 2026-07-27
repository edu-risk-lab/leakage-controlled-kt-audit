# M. Tổng hợp lỗi và quyết định gửi GS hướng dẫn

**Thời điểm:** 2026-07-25  
**PDF đề xuất:** `paper/submission_APIN/main_APIN.pdf`  
**Trang:** 60 (main body §1–§6: **34**; appendix từ §A p.35)  
**SHA-256:** `a705c463278d91f75ec0e937aad73bb6b050f4302266ba070d59c7f3385260c1`  
**Repo (sau transfer):** `https://github.com/edu-risk-lab/leakage-controlled-kt-audit`  
**PDF nộp EM:** `paper/submission_APIN/DaoMinh_2026_LeakageControlledKT_APIN.pdf`

## Kết luận đề xuất

| Quyết định | Trạng thái |
|------------|------------|
| Gửi GS hướng dẫn | **Sẵn sàng** |
| Nộp APIN | **Sẵn sàng có điều kiện** (sau xác nhận GS + EM) |

## Lỗi mở bắt buộc

**Không còn** (0).

## Đã xử lý trong phiên audit gần nhất

| Mức | Mã | Việc đã làm |
|-----|-----|-------------|
| Cao | L01 | Abstract ≈219 từ; 6 keywords; heading *Statements and Declarations* |
| Trung bình | K04 | Code availability: pyKT MIT + OSS deps |
| Trung bình | L07 | Cover letter khôi phục + originality/exclusivity; bỏ S22 |
| Trung bình | L08 | Xóa `.aux/.log/.out/.blg`; làm mới `MANIFEST.csv` |

## CXM — cần thao tác khi nộp (không chặn gửi GS)

1. **L05** — Nhập metadata EM khớp title page (corresponding: Van-Hau Nguyen / `nvhau66@gmail.com`).
2. **L06** — Chỉ blind nếu EM yêu cầu; guidelines APIN hiện không bắt buộc double-blind PDF.

## Soft (thông tin, không fail checklist)

- Font Type3 (ORCID icon / DejaVu trong figure): đã embed.
- `LICENSE` repo public: tuỳ chọn ngoài manuscript.
- Sau mỗi lần `pdflatex`, nhớ **không** upload lại `.aux/.log`.

## Gói gửi GS

**Zip sẵn sàng:** `paper/gui_GS_package_APIN_20260725.zip` (1.78 MB)

1. `main_APIN.pdf` (+ bản trong `submission_APIN/`)
2. `submission_APIN/` (gói LaTeX, đã loại `.aux/.log/.out/.blg`)
3. `cover_letter_APIN.md`
4. `Checklist/checklist_APIN.docx` + `Log_CheckList.docx`
5. `audit/crossref_auc_report.md` (12/12 pass, 25/07/2026)
6. `submission_APIN/APIN_Review_Report.docx` — phản biện nội bộ mô phỏng + mapping PGS
7. `PACKAGE_INFO.txt` + `M_QUYET_DINH_GUI_GS.md`

---
*Checklist hỗ trợ QA; không thay phản biện khoa học của GS hay hướng dẫn nộp bài hiện hành của APIN.*
