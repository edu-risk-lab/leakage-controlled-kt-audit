# -*- coding: utf-8 -*-
"""Tao ban trinh bay seminar tieng Viet cho bai bao APIN.

Ban tieng Viet cua build_seminar_pptx.py. Dau ra: paper/APIN_seminar_vi.pptx.
Cac thuat ngu ky thuat (KT, AUC, DAG, DDR, TBMR, ECR, throughput, reliance) duoc
giu nguyen va chu giai mot lan; phan dien giai bang tieng Viet.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import fitz  # PyMuPDF
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
OUT = ROOT / "paper" / "APIN_seminar_vi.pptx"
ASSETS = ROOT / "paper" / "_pptx_assets_vi"

# Palette
DARK = RGBColor(0x14, 0x2A, 0x4A)
NAVY2 = RGBColor(0x1E, 0x3C, 0x66)
ACCENT = RGBColor(0xE0, 0x7A, 0x2B)
LIGHT = RGBColor(0xF2, 0xF5, 0xF9)
GRAY = RGBColor(0x53, 0x59, 0x63)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
RED = RGBColor(0xB0, 0x3A, 0x2E)

FONT = "Calibri"
SW, SH = Inches(13.333), Inches(7.5)


def rasterise(pdf_name: str, zoom: float = 3.0) -> Path:
    ASSETS.mkdir(exist_ok=True)
    out = ASSETS / (Path(pdf_name).stem + ".png")
    doc = fitz.open(FIG / pdf_name)
    doc[0].get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False).save(out)
    doc.close()
    return out


def png_asset(png_name: str) -> Path:
    ASSETS.mkdir(exist_ok=True)
    out = ASSETS / png_name
    shutil.copy(FIG / png_name, out)
    return out


prs = Presentation()
prs.slide_width = SW
prs.slide_height = SH
BLANK = prs.slide_layouts[6]
_num = {"n": 0}


def blank_slide():
    return prs.slides.add_slide(BLANK)


def fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def rect(slide, x, y, w, h, color):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    fill(sp, color)
    sp.shadow.inherit = False
    return sp


def textbox(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tb.text_frame.word_wrap = True
    return tb, tb.text_frame


def set_run(r, text, size, color, bold=False, italic=False, font=FONT):
    r.text = text
    r.font.size = Pt(size)
    r.font.color.rgb = color
    r.font.bold = bold
    r.font.italic = italic
    r.font.name = font


def header(slide, title, kicker=None):
    rect(slide, 0, 0, SW, Inches(1.15), DARK)
    rect(slide, 0, Inches(1.15), SW, Inches(0.06), ACCENT)
    tb, tf = textbox(slide, Inches(0.55), Inches(0.16), Inches(12.2), Inches(0.95))
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    if kicker:
        set_run(tf.paragraphs[0].add_run(), kicker.upper(), 12, ACCENT, bold=True)
        p2 = tf.add_paragraph()
        set_run(p2.add_run(), title, 26, WHITE, bold=True)
    else:
        set_run(tf.paragraphs[0].add_run(), title, 28, WHITE, bold=True)


def footer(slide):
    _num["n"] += 1
    tb, tf = textbox(slide, Inches(0.4), Inches(7.02), Inches(10.2), Inches(0.4))
    set_run(tf.paragraphs[0].add_run(),
            "Kiểm soát rò rỉ khi xây dựng đồ thị khái niệm cho Knowledge Tracing"
            "  •  Applied Intelligence", 9, GRAY)
    tb2, tf2 = textbox(slide, Inches(12.5), Inches(7.02), Inches(0.7), Inches(0.4))
    tf2.paragraphs[0].alignment = PP_ALIGN.RIGHT
    set_run(tf2.paragraphs[0].add_run(), str(_num["n"]), 10, GRAY, bold=True)


def bullets(slide, items, x=Inches(0.65), y=Inches(1.5), w=Inches(12.0),
            h=Inches(5.3), base=17):
    tb, tf = textbox(slide, x, y, w, h)
    first = True
    for it in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        lvl = it.get("lvl", 0)
        p.level = lvl
        p.space_after = Pt(it.get("space", 8))
        p.space_before = Pt(it.get("before", 0))
        size = it.get("size", base - 2 * lvl)
        color = it.get("color", DARK if lvl == 0 else GRAY)
        marker = it.get("marker", "▪ " if lvl == 0 else "– ")
        if it.get("nomark"):
            marker = ""
        lead = it.get("lead")
        if lead:
            set_run(p.add_run(), marker, size, ACCENT if lvl == 0 else GRAY, bold=True)
            set_run(p.add_run(), lead, size, color, bold=True)
            set_run(p.add_run(), it["t"], size, color)
        else:
            set_run(p.add_run(), marker + it["t"], size, color, bold=it.get("bold", False))
    return tf


def content(title, items, kicker=None, **kw):
    s = blank_slide()
    header(s, title, kicker)
    bullets(s, items, **kw)
    footer(s)
    return s


def figure_slide(title, img_path, kicker=None, caption=None, img_w=None, right_text=None):
    s = blank_slide()
    header(s, title, kicker)
    if right_text is None:
        pic = s.shapes.add_picture(str(img_path), Inches(0), Inches(1.55), width=(img_w or Inches(8.6)))
        pic.left = int((SW - pic.width) / 2)
        pic.top = Inches(1.55)
        if caption:
            tb, tf = textbox(s, Inches(0.8), Inches(6.5), Inches(11.7), Inches(0.5))
            tf.paragraphs[0].alignment = PP_ALIGN.CENTER
            set_run(tf.paragraphs[0].add_run(), caption, 12, GRAY, italic=True)
    else:
        pic = s.shapes.add_picture(str(img_path), Inches(0.5), Inches(1.6), width=(img_w or Inches(6.7)))
        if pic.height > Inches(5.0):
            pic.height = Inches(5.0)
        bullets(s, right_text, x=Inches(7.6), y=Inches(1.7), w=Inches(5.4), h=Inches(5.0), base=15)
        if caption:
            tb, tf = textbox(s, Inches(0.5), Inches(6.7), Inches(6.8), Inches(0.4))
            set_run(tf.paragraphs[0].add_run(), caption, 11, GRAY, italic=True)
    footer(s)
    return s


def section(title, subtitle=None):
    s = blank_slide()
    rect(s, 0, 0, SW, SH, DARK)
    rect(s, Inches(0.9), Inches(3.05), Inches(1.7), Inches(0.12), ACCENT)
    tb, tf = textbox(s, Inches(0.85), Inches(3.25), Inches(11.6), Inches(1.6))
    set_run(tf.paragraphs[0].add_run(), title, 40, WHITE, bold=True)
    if subtitle:
        p2 = tf.add_paragraph()
        set_run(p2.add_run(), subtitle, 18, RGBColor(0xB9, 0xC6, 0xD8))
    return s


# ============================================================================
# 1. TITLE
s = blank_slide()
rect(s, 0, 0, SW, SH, DARK)
rect(s, 0, Inches(4.55), SW, Inches(0.09), ACCENT)
tb, tf = textbox(s, Inches(0.9), Inches(1.1), Inches(11.6), Inches(0.6))
set_run(tf.paragraphs[0].add_run(),
        "APPLIED INTELLIGENCE  •  SEMINAR NGHIÊN CỨU", 14, ACCENT, bold=True)
tb, tf = textbox(s, Inches(0.9), Inches(1.7), Inches(11.7), Inches(2.7))
set_run(tf.paragraphs[0].add_run(),
        "Quy trình kiểm soát rò rỉ khi xây dựng đồ thị khái niệm và chẩn đoán "
        "cold-start cho Knowledge Tracing", 32, WHITE, bold=True)
tb, tf = textbox(s, Inches(0.9), Inches(4.75), Inches(11.7), Inches(1.4))
p = tf.paragraphs[0]
set_run(p.add_run(), "Dao Minh Tuan, Nguyen Khanh Trinh, Nguyen Tien Duong, "
        "Ngo Quoc Khanh, ", 15, WHITE)
set_run(p.add_run(), "Nguyen Van Hau", 15, ACCENT, bold=True)
set_run(p.add_run(), " (tác giả liên hệ), Le Hoang Son", 15, WHITE)
p2 = tf.add_paragraph()
p2.space_before = Pt(6)
set_run(p2.add_run(), "Trường Đại học Sư phạm Kỹ thuật Hưng Yên  •  "
        "Đại học Quốc gia Hà Nội", 13, RGBColor(0xB9, 0xC6, 0xD8))
tb, tf = textbox(s, Inches(0.9), Inches(6.5), Inches(11.7), Inches(0.6))
set_run(tf.paragraphs[0].add_run(),
        "Một quy trình rà soát rò rỉ — không phải một mô hình KT mới — giúp "
        "graph-enhanced KT trở nên đáng tin cậy", 14, RGBColor(0xD8, 0xE0, 0xEC),
        italic=True)

# 2. AGENDA
content("Nội dung trình bày", kicker="Tổng quan", items=[
    {"t": "Bối cảnh & vấn đề: rò rỉ dữ liệu ẩn trong KT tăng cường bằng đồ thị", "lead": "1. "},
    {"t": "Vì sao đồ thị trở thành kênh đưa thông tin của tập test vào mô hình", "lead": "2. "},
    {"t": "Đóng góp: một quy trình rà soát rò rỉ gồm năm thành phần", "lead": "3. "},
    {"t": "Phương pháp: kiểm soát rò rỉ, kiểm tra DAG, DDR, cold-start, đối chiếu chuyên gia", "lead": "4. "},
    {"t": "Luật hai yếu tố: throughput × reliance", "lead": "5. "},
    {"t": "Kết quả: tác hại có điều kiện, thứ tự mô hình, khác biệt so với chuyên gia", "lead": "6. "},
    {"t": "Từ tín hiệu rà soát đến hành động triển khai", "lead": "7. "},
    {"t": "Hạn chế, hướng phát triển và điểm chốt", "lead": "8. "},
], y=Inches(1.6))

# ---- SECTION 1
section("1. Bối cảnh & Vấn đề",
        "Vì sao xây dựng đồ thị là một kênh rò rỉ dữ liệu thường bị bỏ qua")

# 3. Background
content("Knowledge Tracing và đồ thị khái niệm", kicker="Bối cảnh", items=[
    {"t": "Knowledge Tracing (KT) ước lượng mức thành thạo các thành phần "
          "kiến thức (KC) của người học dựa trên lịch sử trả lời.", "lead": "Là gì: "},
    {"t": "Ứng dụng: luyện tập thích nghi, hệ dạy học thông minh, gợi ý lộ trình học.", "lvl": 1},
    {"t": "từ BKT → mô hình chuỗi sâu (DKT, DKVMN, AKT, simpleKT) → mô hình "
          "tăng cường bằng đồ thị (GKT, GIKT, DGEKT).", "lead": "Xu hướng: "},
    {"t": "các mô hình này lan truyền thông tin trên đồ thị KC, mã hóa quan hệ "
          "tiên quyết hoặc tương đồng giữa các KC.", "lead": "Vai trò đồ thị: "},
    {"t": "đồ thị phụ trợ này thường được dựng từ CHÍNH bộ log dùng để huấn "
          "luyện và đánh giá.", "lvl": 1, "color": RED},
    {"t": "lợi ích từ đồ thị là thật, hay chỉ là hệ quả của cách dựng đồ thị?",
     "lead": "Câu hỏi: ", "before": 6, "color": NAVY2},
])

# 4. Leakage problem
content("Kênh rò rỉ ẩn", kicker="Vấn đề", items=[
    {"t": "nếu gom cạnh TRƯỚC khi chia train/test, thông tin của tập test đi vào "
          "mô hình qua đồ thị — dù bộ tối ưu KT chỉ nhìn thấy fold huấn luyện.", "lead": "Cơ chế: "},
    {"t": "Chia fold ở mức chuỗi là cần nhưng CHƯA ĐỦ: đồ thị là một kênh nhiễm "
          "dữ liệu độc lập.", "color": RED},
    {"t": "Ví dụ về throughput (tỷ lệ nhiễm của một cạnh):", "before": 6, "bold": True, "nomark": True},
    {"t": "KC \"nóng\" (nhiều dữ liệu): 20 lượt rò làm support của cạnh tăng "
          "40→60 → nhiễm 33%.", "lvl": 1},
    {"t": "KC \"rất lạnh\" (ít dữ liệu): cũng 20 lượt đó làm tăng 4→24 → nhiễm 83%.", "lvl": 1, "color": RED},
    {"t": "mức nhiễm tỉ lệ NGHỊCH với tần suất của KC trong fold train — KC "
          "cold-start chính là điểm rò nguy hiểm nhất.",
     "lead": "Nhận định: ", "before": 6, "color": NAVY2},
    {"t": "AUC tổng hợp báo động quá muộn; cần đo kênh rò rỉ này một cách "
          "trực tiếp.", "lead": "Do đó: "},
])

# ---- SECTION 2
section("2. Đóng góp", "Một quy trình rà soát rò rỉ, không phải một mô hình mới")

# 5. Contributions
content("Năm đóng góp (C1–C5)", kicker="Đóng góp", items=[
    {"t": "Xây dựng có kiểm soát rò rỉ — chia dữ liệu theo người học & thời gian; "
          "suy quan hệ tiên quyết/tương đồng chỉ từ fold train; ghi xuất xứ "
          "(provenance) từng cạnh.", "lead": "C1  "},
    {"t": "Chẩn đoán rò rỉ phân tầng — các chỉ số builder mass, TBMR, ECR-flag, "
          "ECR-overlap đo mức nhiễm độc lập với độ chính xác.", "lead": "C2  "},
    {"t": "Kiểm tra DAG và chỉ số DDR (DAG Disruption Rate) — thước đo cấu trúc "
          "giúp phân biệt các toán tử tăng cường (augmentation).", "lead": "C3  "},
    {"t": "Phân tầng cold-start — báo cáo kết quả theo tần suất KC, làm lộ nơi "
          "rò rỉ và bằng chứng yếu tập trung.", "lead": "C4  "},
    {"t": "Đối chiếu với \"chân trị\" (ground-truth) — so đồ thị suy từ hành vi "
          "với chú giải tiên quyết của chuyên gia.", "lead": "C5  "},
    {"t": "một lớp hỗ trợ quyết định và chấm điểm rủi ro rò rỉ — không nhằm "
          "tăng độ chính xác.", "lead": "Định vị: ", "before": 8, "color": NAVY2},
])

# ---- SECTION 3
section("3. Quy trình rà soát rò rỉ", "Xây dựng → Chẩn đoán → Đối chiếu")

# 6. Leakage control
content("Kiểm soát rò rỉ & xuất xứ (provenance)", kicker="Phương pháp — C1/C2", items=[
    {"t": "chia theo người học và thời gian; suy cạnh chỉ từ fold huấn luyện "
          "(F_train), không dùng log đã gom.", "lead": "Chỉ dùng train: "},
    {"t": "ghi xuất xứ theo từng fold cho mọi cạnh được giữ lại → tái lập được "
          "và so sánh được giữa các bài báo.", "lead": "Xuất xứ: "},
    {"t": "Ba tầng chẩn đoán rò rỉ:", "before": 6, "bold": True, "nomark": True},
    {"t": "Builder mass / TBMR — đo mức trộn thời gian trong tập train và throughput.", "lvl": 1},
    {"t": "ECR-flag — kiểm tra tính tách biệt người học (có thể bằng 0 dù throughput cao).", "lvl": 1},
    {"t": "ECR-overlap — đo mức nhiễm ở vùng lân cận các KC cold-start.", "lvl": 1},
    {"t": "chỉ chia fold tách biệt là chưa đủ; một chỉ số rò rỉ đơn lẻ có thể "
          "che giấu dịch chuyển do throughput gây ra.", "lead": "Bài học: ",
     "before": 6, "color": RED},
])

# 7. DDR figure
ddr = rasterise("fig_ddr_junyi.pdf")
figure_slide("DDR: DAG Disruption Rate", ddr, kicker="Phương pháp — C3",
             right_text=[
                 {"t": "DDR đo mức một toán tử tăng cường phá vỡ DAG tiên quyết, "
                       "tại cùng một \"ngân sách\" nhiễu.", "lead": "Ý tưởng: "},
                 {"t": "quét 5 toán tử (xóa cạnh, xóa nút, …, bảo toàn tiên quyết).", "lead": "Phạm vi thử: "},
                 {"t": "toán tử bảo toàn tiên quyết (giữ khung xương của DAG) phá "
                       "vỡ ít hơn hẳn so với xóa cạnh, ở cùng ngân sách.",
                  "lead": "Kết quả: ", "color": GREEN},
                 {"t": "DDR dùng được cho mọi đồ thị lộ trình học có hướng.", "lead": "Ứng dụng: "},
             ], caption="DDR theo mức nhiễu tăng dần (Junyi).")

# 8. Cold-start + GT-XV
content("Cold-start & đối chiếu chân trị", kicker="Phương pháp — C4/C5", items=[
    {"t": "Phân tầng cold-start (C4):", "bold": True, "nomark": True},
    {"t": "Báo cáo chỉ số theo từng tầng tần suất KC (từ rất lạnh đến nóng).", "lvl": 1},
    {"t": "AUC tổng hợp che đi hành vi ở tầng nhỏ; số KC rất lạnh ít "
          "(n = 19–161) nên phương sai cao — cần đọc kèm n.", "lvl": 1},
    {"t": "Đối chiếu chân trị (C5):", "bold": True, "nomark": True, "before": 6},
    {"t": "so đồ thị suy từ hành vi (chỉ từ train) với chú giải tiên quyết của "
          "chuyên gia trên Junyi.", "lvl": 1},
    {"t": "đồng thuận ở mức nút nhưng KHÁC BIỆT ở mức cạnh — suy luận từ hành vi "
          "KHÔNG thể thay cho chuyên gia.", "lvl": 1, "color": RED},
])

# 9. PR curve
pr = rasterise("fig_pr_curve.pdf")
figure_slide("Đối chiếu chân trị trên Junyi", pr, kicker="Phương pháp — C5",
             right_text=[
                 {"t": "đồ thị suy từ hành vi khôi phục được cạnh tiên quyết của "
                       "chuyên gia tốt hơn ngẫu nhiên nhiều…", "lead": "Tín hiệu: "},
                 {"t": "…nhưng hai nguồn khác biệt ở mức cạnh, nên xem là BỔ SUNG "
                       "cho nhau chứ không thay thế nhau.", "lead": "Sắc thái: "},
                 {"t": "nên đưa cả đồ thị hành vi và đồ thị chuyên gia vào như hai "
                       "quan hệ riêng.", "lead": "Ý nghĩa: ", "color": NAVY2},
             ], caption="Đường precision–recall: cạnh suy luận so với cạnh chuyên gia.")

# ---- SECTION 4
section("4. Luật hai yếu tố & Kết quả",
        "Khi nào rò rỉ qua đồ thị mới thực sự gây hại?")

# 10. Datasets
content("Dữ liệu & thiết lập thực nghiệm", kicker="Thiết lập", items=[
    {"t": "XES3G5M — benchmark chính để so sánh mô hình (dữ liệu dày, nhiều chuyển tiếp).", "lead": "Chính: "},
    {"t": "ASSISTments 2012 — Q-matrix đơn kỹ năng nên không dựng được cạnh tương đồng.", "lead": "Phụ: "},
    {"t": "Junyi Academy — kiểm tra bão hòa và đối chiếu chân trị.", "lead": "Đối chiếu: "},
    {"t": "hai bộ dữ liệu mô phỏng với cấu trúc khái niệm được kiểm soát.", "lead": "Tổng hợp: "},
    {"t": "simpleKT/AKT (chỉ dùng chuỗi), GKT & GIKT (phụ thuộc đồ thị), DGEKT; "
          "chạy trên pyKT, fold tách người học, xuất đồ thị chỉ-từ-train.",
     "lead": "Mô hình: ", "before": 6},
])

# 11. Two-factor 2x2 table
s = blank_slide()
header(s, "Luật hai yếu tố: throughput × reliance", kicker="Kết quả chính")
tb, tf = textbox(s, Inches(0.65), Inches(1.4), Inches(12), Inches(0.72))
p = tf.paragraphs[0]
set_run(p.add_run(), "Rò rỉ qua đồ thị chỉ làm dịch AUC khi CẢ HAI yếu tố cùng "
        "cao — throughput (mức nhiễm) và reliance (mức phụ thuộc đồ thị). "
        "Ba trong bốn ô đều ≈ 0.", 15, DARK)
gtbl = s.shapes.add_table(3, 3, Inches(0.85), Inches(2.3), Inches(11.6), Inches(3.5)).table
gtbl.columns[0].width = Inches(3.6)
gtbl.columns[1].width = Inches(4.0)
gtbl.columns[2].width = Inches(4.0)
data = [
    ["", "Reliance thấp (simpleKT)", "Reliance cao (GKT, GIKT)"],
    ["Throughput thấp\n(train-only vs. full-log)", "≈ 0", "≤ 0.003  (ablation full-log)"],
    ["Throughput cao\n(inject 20% test-fold)", "≈ 0 (+0.0004)", "≈ 0 (GKT −0.010; GIKT +0.0002)"],
]
for r in range(3):
    for c in range(3):
        cell = gtbl.cell(r, c)
        cell.text = data[r][c]
        para = cell.text_frame.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER if (c > 0 or r == 0) else PP_ALIGN.LEFT
        run = para.runs[0] if para.runs else para.add_run()
        run.font.size = Pt(15)
        run.font.name = FONT
        if r == 0 or c == 0:
            run.font.bold = True
            run.font.color.rgb = WHITE
            cell.fill.solid(); cell.fill.fore_color.rgb = DARK
        else:
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT
            run.font.color.rgb = GRAY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
tb, tf = textbox(s, Inches(0.85), Inches(6.1), Inches(11.7), Inches(0.8))
p = tf.paragraphs[0]
set_run(p.add_run(), "Điểm chốt: ", 15, ACCENT, bold=True)
set_run(p.add_run(), "S17 (builder) phản ứng khi inject, nhưng AUC fold-0 gần phẳng "
        "(S18 decoupling; GPU verified 2026-07-23). Phải đọc throughput trước AUC.",
        15, DARK)
footer(s)

# 12. Conditional harm
dd = png_asset("fig_ddr_downstream.png")
figure_slide("Tác hại có điều kiện: phép thử phá đồ thị", dd, kicker="Kết quả",
             right_text=[
                 {"t": "ràng mọi kết luận downstream vào một phép thử phá đồ thị "
                       "(manipulation check) — phá đồ thị có làm dịch AUC không?", "lead": "Phép thử: "},
                 {"t": "GKT trên XES3G5M ĐẠT — phá đồ thị làm mất 0.07–0.09 AUC.",
                  "lead": "Phụ thuộc: ", "color": GREEN},
                 {"t": "khi đó DDR dự báo tốt mức mất AUC (r = 0.97) và toán tử "
                       "bảo toàn tiên quyết tốn ít độ chính xác nhất.", "lvl": 1},
                 {"t": "DGEKT và GKT trên ASSISTments TRƯỢT — phá toàn bộ đồ thị "
                       "chỉ làm dịch AUC ≤ 0.002 → đồ thị gần như không được dùng.", "lead": "Trơ: ", "color": RED},
                 {"t": "hư hại cấu trúc chỉ chuyển thành hư hại dự báo khi mô "
                       "hình thực sự đọc đồ thị.", "lead": "Kết luận: ", "color": NAVY2},
             ], caption="DDR → AUC downstream (mô hình phụ thuộc đồ thị).")

# 13. Model ordering
content("Thứ tự mô hình trên XES3G5M", kicker="Kết quả", items=[
    {"t": "Bộ ba mô hình chính (cùng ngân sách 10 epoch):", "bold": True, "nomark": True},
    {"t": "simpleKT/AKT ≈ 0.875   •   GIKT ≈ 0.878   •   GKT ≈ 0.834.", "lvl": 1},
    {"t": "GKT kém simpleKT ≈ 0.041 AUC (paired-t, CI 95% [−0.044, −0.038]).", "lead": "Chênh lệch: ", "color": RED},
    {"t": "kéo GKT lên 30 epoch chỉ gỡ ≈ 0.003 AUC; trung bình gộp vẫn ≈ −0.038 "
          "trên chín fold → không phải do thiếu ngân sách.", "lead": "Không do ngân sách: "},
    {"t": "phụ thuộc đồ thị không đồng nghĩa với lợi thế độ chính xác — có khi "
          "còn làm giảm độ chính xác khi mô hình chuỗi đã đủ mạnh.",
     "lead": "Thông điệp: ", "before": 6, "color": NAVY2},
])

# ---- SECTION 5
section("5. Từ rà soát đến hành động",
        "Người triển khai cần làm khác đi điều gì")

# 14. Decision map table
s = blank_slide()
header(s, "Bản đồ quyết định: tín hiệu rà soát → hành động", kicker="Giá trị ứng dụng")
t = s.shapes.add_table(6, 3, Inches(0.55), Inches(1.45), Inches(12.25), Inches(5.1)).table
t.columns[0].width = Inches(3.7)
t.columns[1].width = Inches(4.0)
t.columns[2].width = Inches(4.55)
dm = [
    ["Tín hiệu rà soát", "Cách đọc", "Hành động triển khai"],
    ["Builder mass / TBMR", "Tăng (log gom vs. chỉ-train)", "Ép đồ thị chỉ-từ-train; nghi ngờ phần lợi ích"],
    ["ECR-flag = 0 nhưng throughput cao", "Tách biệt nhưng vẫn nhiễm", "Chia fold là chưa đủ; giữ nhật ký xuất xứ"],
    ["Phép thử phá đồ thị", "AUC không đổi khi phá đồ thị", "Mô hình trơ: DDR chỉ để tái lập, không phải mục tiêu"],
    ["DDR vs. AUC (r ≈ 0.97)", "Đơn điệu trên mô hình phụ thuộc đồ thị", "Ưu tiên bảo toàn tiên quyết; DDR là mục tiêu thiết kế"],
    ["Tầng cold-start", "Throughput cao nhất ở nơi ít dữ liệu", "Báo cáo xuất xứ theo từng tầng"],
]
for r in range(6):
    for c in range(3):
        cell = t.cell(r, c); cell.text = dm[r][c]
        run = cell.text_frame.paragraphs[0].runs[0]
        run.font.size = Pt(13 if r else 14)
        run.font.name = FONT
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        if r == 0:
            run.font.bold = True; run.font.color.rgb = WHITE
            cell.fill.solid(); cell.fill.fore_color.rgb = DARK
        else:
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT if r % 2 else RGBColor(0xE6, 0xEC, 0xF3)
            run.font.color.rgb = GRAY
            if c == 2:
                run.font.color.rgb = NAVY2; run.font.bold = True
footer(s)

# 15. Practitioner 4 steps
content("Người triển khai cần làm khác đi", kicker="Giá trị ứng dụng", items=[
    {"t": "Dựng đồ thị sạch theo fold — chỉ suy từ fold huấn luyện và ghi xuất "
          "xứ từng cạnh.", "lead": "1. "},
    {"t": "Đọc chỉ số throughput thay vì độ chính xác — xác định vị trí bộ dữ "
          "liệu trên lưới throughput × reliance.", "lead": "2. "},
    {"t": "Ràng mọi kết luận downstream vào phép thử phá đồ thị — xác nhận mô "
          "hình thực sự đọc đồ thị trước khi quy công cho nó.", "lead": "3. "},
    {"t": "Ưu tiên toán tử tăng cường bảo toàn cấu trúc — dùng toán tử bảo toàn "
          "tiên quyết mà DDR đánh giá cao.", "lead": "4. "},
    {"t": "Bốn bước này là phần cốt lõi hành động của checklist và bản đồ "
          "quyết định.", "before": 8, "nomark": True, "color": NAVY2, "bold": True},
], y=Inches(1.6))

# ---- SECTION 6
section("6. Thảo luận & Điểm chốt")

# 16. Limitations
content("Hạn chế & hướng phát triển", kicker="Thảo luận", items=[
    {"t": "cạnh tương đồng phụ thuộc Q-matrix (không dựng được khi mã hóa đơn "
          "kỹ năng, ví dụ ASSISTments).", "lead": "Hạn chế: "},
    {"t": "hiệu ứng rò rỉ nhỏ trên các benchmark công khai là do bộ lọc tần "
          "suất siết throughput, không phải vì rò rỉ vô hại nói chung.", "lvl": 1},
    {"t": "tầng rất lạnh có n nhỏ nên AUC theo tầng có phương sai cao.", "lvl": 1},
    {"t": "tách lợi ích của graph-KT thành ba phần — phần còn lại sau kiểm soát "
          "rò rỉ, phần do cách dựng đồ thị, phần do mô hình nền.", "lead": "Hướng phát triển: "},
    {"t": "kết hợp đồ thị suy luận và đồ thị chuyên gia như hai quan hệ; mở "
          "rộng phép thử downstream có kiểm soát; rà soát reachability-disruption.", "lvl": 1},
])

# 17. Conclusion
content("Điểm chốt", kicker="Kết luận", items=[
    {"t": "Xây dựng đồ thị là một thành phần thực nghiệm hạng nhất — và là một "
          "kênh rò rỉ dữ liệu — chứ không phải bước tiền xử lý xem nhẹ.", "lead": "1. "},
    {"t": "Tác hại có điều kiện: cần đồng thời throughput cao VÀ mô hình phụ "
          "thuộc đồ thị (đạt phép thử phá đồ thị).", "lead": "2. "},
    {"t": "Đo kênh trực tiếp (builder mass, TBMR); AUC là báo động muộn và "
          "không đáng tin.", "lead": "3. "},
    {"t": "DDR cùng toán tử bảo toàn tiên quyết cho một lựa chọn tăng cường có "
          "nguyên tắc, tôn trọng cấu trúc.", "lead": "4. "},
    {"t": "Sản phẩm là một lớp rà soát rò rỉ hỗ trợ quyết định và chấm điểm rủi ro "
          "cho graph-enhanced KT đáng tin cậy.", "lead": "5. ", "color": NAVY2, "bold": True},
], y=Inches(1.6))

# 18. Thank you
s = blank_slide()
rect(s, 0, 0, SW, SH, DARK)
rect(s, Inches(0.9), Inches(3.7), Inches(1.7), Inches(0.12), ACCENT)
tb, tf = textbox(s, Inches(0.85), Inches(2.6), Inches(11.6), Inches(1.2))
set_run(tf.paragraphs[0].add_run(), "Xin cảm ơn — Thảo luận?", 42, WHITE, bold=True)
tb, tf = textbox(s, Inches(0.9), Inches(3.95), Inches(11.6), Inches(1.6))
set_run(tf.paragraphs[0].add_run(),
        "Kiểm soát rò rỉ khi xây dựng đồ thị khái niệm cho Knowledge Tracing",
        17, RGBColor(0xD8, 0xE0, 0xEC))
p2 = tf.add_paragraph(); p2.space_before = Pt(8)
set_run(p2.add_run(), "Tác giả liên hệ: Nguyen Van Hau — nvhau66@gmail.com",
        14, RGBColor(0xB9, 0xC6, 0xD8))
p3 = tf.add_paragraph()
set_run(p3.add_run(), "Mã nguồn & dữ liệu: github.com/tuanymc/p0_project",
        14, RGBColor(0xB9, 0xC6, 0xD8))

# ============================================================================
# Speaker notes (tiếng Việt) — theo đúng thứ tự slide 1..24
NOTES = [
    # 1. Title
    "Xin chào mọi người. Hôm nay tôi trình bày công trình gửi tạp chí Applied "
    "Intelligence. Điều tôi mong mọi người nhớ ngay từ đầu là: đây không phải "
    "một mô hình KT mới, mà là một quy trình rà soát rò rỉ, giúp trả lời câu hỏi "
    "'lợi ích mà đồ thị mang lại cho mô hình có thật sự đáng tin hay không'. Tôi "
    "sẽ giới thiệu nhanh nhóm tác giả rồi đi vào nội dung chính.",
    # 2. Agenda
    "Bài nói đi qua tám phần, từ bối cảnh và vấn đề, sang đóng góp và phương "
    "pháp, rồi đến kết quả và góc nhìn triển khai. Nếu phải chọn hai phần để "
    "theo dõi kỹ nhất, đó là luật hai yếu tố ở slide 11 và kết quả tác hại có "
    "điều kiện ở slide 12 — những phần còn lại đều xoay quanh hai ý này.",
    # 3. Section 1
    "Ở phần mở đầu, tôi muốn làm rõ một điều dễ bị bỏ qua: bản thân việc xây "
    "dựng đồ thị cũng là một con đường làm rò rỉ dữ liệu. Cộng đồng đã rất cẩn "
    "thận chống rò rỉ khi chia dữ liệu theo chuỗi trả lời, nhưng lại vô tình để "
    "hở đúng con đường đi qua đồ thị.",
    # 4. Background
    "Trước hết xin nhắc nhanh nền tảng. Knowledge Tracing ước lượng xem người "
    "học đã nắm vững từng khái niệm đến đâu. Lĩnh vực này phát triển từ các mô "
    "hình cổ điển, đến mô hình chuỗi sâu, và gần đây là mô hình tăng cường bằng "
    "đồ thị — loại lan truyền thông tin giữa các khái niệm qua một đồ thị. Điểm "
    "mấu chốt nằm ở dòng chữ màu đỏ: đồ thị đó thường được dựng từ chính bộ dữ "
    "liệu dùng để huấn luyện và đánh giá, nên câu hỏi tự nhiên đặt ra là lợi ích "
    "thu được là thật, hay chỉ do cách dựng đồ thị tạo ra.",
    # 5. Leakage problem
    "Giải thích cơ chế bằng lời đơn giản. Đồ thị khái niệm được dựng từ dữ liệu: "
    "mỗi cạnh nối hai khái niệm mạnh hay yếu tùy theo số lần người học đi từ "
    "khái niệm này sang khái niệm kia. Nếu ta dựng đồ thị từ TOÀN BỘ dữ liệu "
    "(gồm cả phần test) rồi mới chia train/test, thì dấu vết của phần test đã "
    "nằm sẵn trong các cạnh — mô hình 'nhìn' được phần test một cách gián tiếp "
    "qua đồ thị, dù khi huấn luyện nó chỉ dùng phần train. "
    "Ví dụ cho thấy vì sao khái niệm hiếm (cold-start) nguy hiểm nhất: giả sử có "
    "20 lượt của tập test bị lọt vào. Với một khái niệm phổ biến, cạnh vốn đã có "
    "40 lượt từ train nên 20 lượt lọt chỉ chiếm 33% — ảnh hưởng nhỏ. Nhưng với "
    "một khái niệm hiếm chỉ có 4 lượt train, thì 20 lượt lọt chiếm tới 83% — gần "
    "như toàn bộ 'bằng chứng' của cạnh đó đến từ dữ liệu test. Càng ít dữ liệu "
    "train thì rò rỉ càng chi phối mạnh. "
    "Chốt lại: chỉ nhìn AUC (độ chính xác) thì phát hiện quá muộn — đến lúc AUC "
    "lệch thì rò rỉ đã xảy ra rồi. Vì vậy phải đo trực tiếp 'có bao nhiêu thông "
    "tin test lọt vào đồ thị' — đó chính là chỉ số throughput.",
    # 6. Section 2
    "Chúng ta chuyển sang phần đóng góp. Tôi xin nhắc lại thông điệp xuyên suốt: "
    "đóng góp của chúng tôi là một quy trình rà soát rò rỉ, chứ không phải một "
    "mô hình mới.",
    # 7. Contributions
    "Chúng tôi có năm đóng góp. Thứ nhất là cách dựng đồ thị chỉ từ dữ liệu huấn "
    "luyện và ghi lại xuất xứ của từng cạnh. Thứ hai là bộ chỉ số chẩn đoán rò "
    "rỉ theo nhiều tầng. Thứ ba là chỉ số DDR, đo mức đồ thị bị phá vỡ cấu trúc. "
    "Thứ tư là cách báo cáo kết quả tách riêng theo mức độ hiếm của khái niệm. "
    "Và thứ năm là phép đối chiếu đồ thị suy từ hành vi với đồ thị do chuyên gia "
    "biên soạn. Tất cả hợp lại thành một lớp hỗ trợ ra quyết định và chấm điểm "
    "rủi ro.",
    # 8. Section 3
    "Bây giờ tôi đi sâu vào ba khối chính của phương pháp: kiểm soát rò rỉ, chỉ "
    "số DDR, và phép đối chiếu với chân trị của chuyên gia.",
    # 9. Leakage control
    "Ở bước kiểm soát rò rỉ, chúng tôi chia dữ liệu theo người học và theo thời "
    "gian, chỉ suy ra các cạnh từ phần huấn luyện, và ghi lại xuất xứ của từng "
    "cạnh. Có ba tầng chỉ số để soi rò rỉ: builder mass và TBMR đo lượng thông "
    "tin lọt vào; ECR-flag kiểm tra xem các nhóm người học có thật sự tách biệt "
    "không; còn ECR-overlap đo mức nhiễm ở vùng khái niệm hiếm. Điều đáng lưu ý "
    "là ECR-flag có thể bằng 0 — nghĩa là nhìn thì có vẻ 'sạch' — nhưng lượng "
    "thông tin lọt vào vẫn cao, nên chỉ chia dữ liệu cẩn thận thôi là chưa đủ.",
    # 10. DDR figure
    "Chỉ số DDR đo mức một phép tăng cường làm phá vỡ đồ thị tiên quyết, khi "
    "cùng một 'liều' can thiệp. Nhìn vào biểu đồ: khi tăng liều can thiệp, phép "
    "bảo toàn tiên quyết ở đường thấp hơn gây hư hại ít hơn hẳn so với việc xóa "
    "cạnh ngẫu nhiên. Đây chính là căn cứ để chọn phép tăng cường một cách có "
    "nguyên tắc, thay vì chọn tùy tiện.",
    # 11. Cold-start & GT-XV
    "Slide này có hai ý. Thứ nhất, phải báo cáo độ chính xác tách riêng theo "
    "từng nhóm khái niệm phân theo tần suất, bởi nhóm khái niệm rất hiếm có quá "
    "ít mẫu nên con số dao động mạnh, dễ gây hiểu nhầm. Thứ hai, khi đối chiếu "
    "đồ thị suy từ hành vi người học với đồ thị do chuyên gia biên soạn, chúng "
    "khớp nhau ở mức từng khái niệm nhưng lại lệch nhau ở mức từng cạnh — nghĩa "
    "là không thể lấy suy luận từ hành vi để thay cho tri thức chuyên gia.",
    # 12. PR curve
    "Biểu đồ precision–recall cho thấy đồ thị suy từ hành vi tìm lại được khá "
    "nhiều cạnh của chuyên gia, tốt hơn hẳn mức ngẫu nhiên, nhưng vẫn không "
    "trùng khớp hoàn toàn. Vì vậy nên xem hai nguồn là bổ sung cho nhau, và đưa "
    "cả hai vào mô hình như hai loại quan hệ riêng biệt.",
    # 13. Section 4
    "Đây là phần quan trọng nhất của bài: trả lời câu hỏi khi nào rò rỉ qua đồ "
    "thị mới thực sự gây hại, thông qua điều mà chúng tôi gọi là luật hai yếu tố.",
    # 14. Datasets
    "Về dữ liệu và thiết lập: XES3G5M là bộ chính để so sánh mô hình, còn "
    "ASSISTments và Junyi đóng vai trò bổ trợ, cộng thêm hai bộ mô phỏng. Về mô "
    "hình, chúng tôi so sánh loại chỉ dùng chuỗi trả lời như simpleKT với loại "
    "phụ thuộc vào đồ thị như GKT và GIKT. Mọi thí nghiệm đều chạy trên thư viện "
    "pyKT, với cách chia dữ liệu tách biệt theo người học.",
    # 15. Two-factor
    "Đây là slide cốt lõi. Ý tưởng gốc là: rò rỉ chỉ gây hại khi đi trọn một "
    "chuỗi nhân quả — thông tin test trước hết phải lọt vào cạnh đồ thị, tức cần "
    "throughput cao, rồi sau đó phải được mô hình thật sự đọc, tức cần reliance "
    "cao. Chỉ cần một mắt xích bằng 0 thì tích bằng 0, nên tác hại là phép NHÂN "
    "chứ không phải phép cộng — đó là lý do ba trong bốn ô đều xấp xỉ 0. Trên "
    "các benchmark công khai, bộ lọc tần suất giữ throughput ở mức thấp nên AUC "
    "chỉ dịch dưới 0.003; khi chủ động bơm 20% test-fold vào builder thì S17 tăng "
    "(|E_pre|, TBMR) nhưng AUC retrain gần phẳng (S18: GKT −0.010, simpleKT +0.0004) — "
    "decoupling builder vs. headline. Kết luận: phải đo throughput trực tiếp, "
    "không tin AUC làm báo động leakage.",
    # 16. Conditional harm
    "Đây là kết quả tác hại có điều kiện. Trước khi kết luận rằng đồ thị mang "
    "lại lợi ích, ta phải làm một phép thử: cố tình phá đồ thị và xem độ chính "
    "xác có tụt không. Với GKT trên bộ XES3G5M, phá đồ thị làm mất 0.07 đến 0.09 "
    "điểm AUC — chứng tỏ mô hình thật sự dùng đồ thị, và đúng như dự đoán, chỉ "
    "số DDR bám rất sát mức tụt này, tương quan tới 0.97. Ngược lại, DGEKT và "
    "GKT trên ASSISTments gần như không đổi, dưới 0.002, nghĩa là đồ thị hầu như "
    "không được dùng. Điểm cần nhấn: hư hại về cấu trúc chỉ biến thành hư hại về "
    "dự đoán khi mô hình thật sự đọc đồ thị.",
    # 17. Model ordering
    "Trên bộ XES3G5M, GKT kém simpleKT khoảng 0.041 điểm AUC, với khoảng tin cậy "
    "hẹp và rõ ràng. Ngay cả khi huấn luyện GKT lâu hơn, tới 30 epoch, khoảng "
    "cách cũng chỉ thu hẹp được khoảng 0.003 — tức không phải do thiếu thời gian "
    "huấn luyện. Thông điệp ở đây là: mô hình phụ thuộc vào đồ thị không đồng "
    "nghĩa với việc nó chính xác hơn; đôi khi còn ngược lại, khi mô hình chuỗi "
    "vốn đã đủ mạnh.",
    # 18. Section 5
    "Chúng ta sang phần ứng dụng: có quy trình này rồi thì người triển khai nên "
    "làm khác đi điều gì trong thực tế.",
    # 19. Decision map
    "Bảng này biến kết quả rà soát thành hành động cụ thể: mỗi tín hiệu đo được "
    "đều có một cách diễn giải và một việc nên làm tương ứng, hoàn toàn không phụ "
    "thuộc vào độ chính xác. Đây chính là phần giá trị ứng dụng mà một tạp chí "
    "như Applied Intelligence quan tâm.",
    # 20. Practitioner
    "Có thể gói lại thành bốn bước dễ nhớ. Một, dựng đồ thị sạch, chỉ từ dữ liệu "
    "huấn luyện. Hai, đọc chỉ số throughput — tức lượng thông tin lọt vào — thay "
    "vì chỉ nhìn độ chính xác. Ba, luôn làm phép thử phá đồ thị trước khi quy "
    "công cho đồ thị. Và bốn, ưu tiên phép tăng cường giữ được cấu trúc. Đây là "
    "thông điệp tôi mong mọi người mang về.",
    # 21. Section 6
    "Cuối cùng là phần thảo luận về hạn chế và các điểm chốt.",
    # 22. Limitations
    "Tôi xin nói thẳng về hạn chế. Cạnh tương đồng phụ thuộc vào cách mã hóa kỹ "
    "năng, nên có bộ dữ liệu không dựng được. Hiệu ứng rò rỉ nhỏ trên các bộ "
    "công khai là vì bộ lọc của chúng tôi đã siết lượng thông tin lọt vào, chứ "
    "không phải vì rò rỉ vô hại. Và nhóm khái niệm rất hiếm có ít mẫu nên số "
    "liệu dao động. Về hướng phát triển, chúng tôi muốn tách rõ lợi ích của mô "
    "hình đồ thị thành ba thành phần, và kết hợp đồ thị suy từ hành vi với đồ "
    "thị chuyên gia.",
    # 23. Conclusion
    "Xin chốt lại năm ý. Một, việc xây dựng đồ thị là một khâu thực nghiệm quan "
    "trọng, đồng thời cũng là một con đường rò rỉ, chứ không phải bước xử lý qua "
    "loa. Hai, tác hại chỉ xảy ra có điều kiện. Ba, nên đo trực tiếp lượng thông "
    "tin lọt vào thay vì trông chờ ở độ chính xác. Bốn, chỉ số DDR cùng phép bảo "
    "toàn tiên quyết cho ta một lựa chọn có nguyên tắc. Năm, sản phẩm cuối cùng "
    "là một lớp rà soát rò rỉ hỗ trợ ra quyết định. Đây là ý tôi muốn nhấn mạnh "
    "nhất.",
    # 24. Thank you
    "Xin cảm ơn mọi người và rất mong nhận được câu hỏi. Trên màn hình là email "
    "tác giả liên hệ và đường dẫn mã nguồn để ai quan tâm có thể tái lập kết quả.",
]

for slide, note in zip(prs.slides, NOTES):
    slide.notes_slide.notes_text_frame.text = note

prs.save(str(OUT))
print(f"Saved {OUT}  ({len(prs.slides)} slides, {len(NOTES)} notes)")
shutil.rmtree(ASSETS, ignore_errors=True)
