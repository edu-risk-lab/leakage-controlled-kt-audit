"""Build a Vietnamese conference presentation from the paper results."""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "baocao.pptx"
ASSET_DIR = ROOT / "paper" / "pptx_assets"

NAVY = RGBColor(22, 54, 92)
BLUE = RGBColor(40, 103, 178)
CYAN = RGBColor(0, 143, 180)
GREEN = RGBColor(72, 149, 99)
ORANGE = RGBColor(224, 133, 49)
RED = RGBColor(180, 65, 65)
GRAY = RGBColor(92, 100, 112)
LIGHT = RGBColor(244, 248, 252)
WHITE = RGBColor(255, 255, 255)
BLACK = RGBColor(20, 25, 32)


def inches(value: float):
    return Inches(value)


def set_font(run, size=20, bold=False, color=BLACK, italic=False):
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color


def add_textbox(slide, x, y, w, h, text="", size=20, color=BLACK, bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(inches(x), inches(y), inches(w), inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_font(run, size=size, color=color, bold=bold)
    return box


def add_title(slide, title, subtitle=None):
    add_textbox(slide, 0.55, 0.28, 12.2, 0.55, title, size=24, color=NAVY, bold=True)
    line = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, inches(0.55), inches(0.91), inches(12.2), inches(0.03))
    line.fill.solid()
    line.fill.fore_color.rgb = CYAN
    line.line.fill.background()
    if subtitle:
        add_textbox(slide, 0.58, 0.99, 11.8, 0.35, subtitle, size=11, color=GRAY)


def add_footer(slide, idx):
    add_textbox(slide, 0.55, 7.15, 9.5, 0.25, "P0 KT Graph Protocol | Báo cáo hội thảo", size=8.5, color=GRAY)
    add_textbox(slide, 12.25, 7.15, 0.55, 0.25, str(idx), size=8.5, color=GRAY, align=PP_ALIGN.RIGHT)


def add_bullets(slide, x, y, w, h, items, size=18, color=BLACK, gap=0):
    box = slide.shapes.add_textbox(inches(x), inches(y), inches(w), inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.level = 0
        p.space_after = Pt(gap)
        p.font.name = "Arial"
        p.font.size = Pt(size)
        p.font.color.rgb = color
    return box


def add_metric_card(slide, x, y, w, h, value, label, color):
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, inches(x), inches(y), inches(w), inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    tf = shape.text_frame
    tf.clear()
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = value
    set_font(r1, size=28, bold=True, color=WHITE)
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = label
    set_font(r2, size=11.5, color=WHITE)


def add_small_table(slide, x, y, w, h, headers, rows, font_size=10.5, header_color=NAVY):
    table_shape = slide.shapes.add_table(len(rows) + 1, len(headers), inches(x), inches(y), inches(w), inches(h))
    table = table_shape.table
    for c, header in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_color
        for p in cell.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER
            for r in p.runs:
                set_font(r, size=font_size, bold=True, color=WHITE)
    for r_idx, row in enumerate(rows, start=1):
        for c_idx, value in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = str(value)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(248, 250, 252) if r_idx % 2 else WHITE
            for p in cell.text_frame.paragraphs:
                p.alignment = PP_ALIGN.CENTER if c_idx else PP_ALIGN.LEFT
                for run in p.runs:
                    set_font(run, size=font_size, color=BLACK)
    return table_shape


def render_pdf(name: str, zoom: float = 2.2) -> Path:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    pdf = ROOT / "results" / "figures" / name
    png = ASSET_DIR / f"{Path(name).stem}.png"
    if png.exists() and png.stat().st_mtime >= pdf.stat().st_mtime:
        return png
    doc = fitz.open(pdf)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    pix.save(png)
    doc.close()
    return png


def add_picture_fit(slide, path: Path, x, y, w, h):
    slide.shapes.add_picture(str(path), inches(x), inches(y), width=inches(w), height=inches(h))


def add_pipeline(slide):
    steps = [
        ("1. Chia người học", "train/val/test\nrời nhau"),
        ("2. Suy luận đồ thị", "chỉ từ train\nE_pre, E_sim"),
        ("3. Kiểm toán", "ECR, EOC,\nTBVR, DAG"),
        ("4. Huấn luyện KT", "pyKT + graph\ntrain-only"),
        ("5. Báo cáo", "baseline,\nablation, cold-start"),
    ]
    x0 = 0.75
    for i, (title, body) in enumerate(steps):
        x = x0 + i * 2.48
        color = [BLUE, CYAN, GREEN, ORANGE, RED][i]
        shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, inches(x), inches(2.35), inches(2.05), inches(1.35))
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        shape.line.fill.background()
        tf = shape.text_frame
        tf.clear()
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = title
        set_font(r, size=13, bold=True, color=WHITE)
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run()
        r2.text = body
        set_font(r2, size=10.5, color=WHITE)
        if i < len(steps) - 1:
            arrow = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RIGHT_ARROW, inches(x + 2.03), inches(2.78), inches(0.52), inches(0.32))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = GRAY
            arrow.line.fill.background()


def make_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # 1
    slide = prs.slides.add_slide(blank)
    bg = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()
    add_textbox(slide, 0.75, 0.82, 11.8, 1.05, "Xây dựng đồ thị khái niệm kiểm soát rò rỉ\ncho Knowledge Tracing", size=32, color=WHITE, bold=True)
    add_textbox(slide, 0.78, 2.25, 10.8, 0.48, "Báo cáo kết quả nghiên cứu tại hội thảo", size=20, color=RGBColor(210, 230, 245))
    add_textbox(slide, 0.78, 5.55, 11.2, 0.6, "Dao Minh Tuan, Nguyen Tien Duong, Nguyen Khanh Trinh, Nguyen Van Hau, Le Hoang Son", size=13.5, color=WHITE)
    add_textbox(slide, 0.78, 6.15, 10.5, 0.35, "Hung Yen University of Technology and Education | VNU Information Technology Institute", size=11.5, color=RGBColor(210, 230, 245))

    # 2
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Bối cảnh và vấn đề")
    add_bullets(
        slide,
        0.75,
        1.45,
        5.7,
        4.9,
        [
            "KT dự đoán trạng thái nắm vững kiến thức từ chuỗi tương tác học tập.",
            "Các mô hình graph-KT dùng đồ thị kỹ năng/bài tập để bổ sung quan hệ tiên quyết.",
            "Nếu đồ thị được suy luận từ toàn bộ log trước khi split, cạnh có thể mang thông tin validation/test.",
            "Rò rỉ không nằm trong nhãn trực tiếp, mà đi qua feature cấu trúc của mô hình.",
        ],
        size=18,
        gap=6,
    )
    add_metric_card(slide, 7.05, 1.55, 2.55, 1.35, "Graph", "input của mô hình", BLUE)
    add_metric_card(slide, 9.9, 1.55, 2.55, 1.35, "Leakage", "qua nguồn gốc cạnh", RED)
    add_metric_card(slide, 7.05, 3.25, 2.55, 1.35, "Train-only", "ràng buộc chính", GREEN)
    add_metric_card(slide, 9.9, 3.25, 2.55, 1.35, "Audit", "báo cáo provenance", ORANGE)
    add_footer(slide, 2)

    # 3
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Mục tiêu nghiên cứu", "Biến đồ thị khái niệm từ artefact tiền xử lý thành đối tượng có thể kiểm toán")
    add_bullets(
        slide,
        0.75,
        1.4,
        11.9,
        4.8,
        [
            "Xây dựng E_pre và E_sim theo từng fold, chỉ dùng người học train.",
            "Ghi provenance và kiểm tra rò rỉ trực tiếp: ECR flag, ECR overlap, EOC, TBVR.",
            "Bảo đảm đồ thị tiên quyết là DAG bằng tỉa chu trình có quy tắc.",
            "Đánh giá ảnh hưởng train-only vs full-log bằng ablation có kiểm soát.",
            "Báo cáo cold-start và đối chiếu Junyi với chú giải chuyên gia.",
        ],
        size=19,
        gap=7,
    )
    add_footer(slide, 3)

    # 4
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Giao thức đề xuất")
    add_pipeline(slide)
    add_bullets(
        slide,
        1.0,
        4.45,
        11.3,
        1.4,
        [
            "Nguyên tắc: mọi cạnh đồ thị trong fold f chỉ được suy luận từ \\mathcal{F}_{train}^f.",
            "Validation/test chỉ dùng để đánh giá KT, không dùng để đếm transition hoặc co-occurrence.",
        ],
        size=16,
        color=GRAY,
        gap=4,
    )
    add_footer(slide, 4)

    # 5
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Dữ liệu thực nghiệm")
    add_small_table(
        slide,
        0.7,
        1.25,
        11.9,
        4.4,
        ["Dataset", "Vai trò", "Ghi chú"],
        [
            ["Junyi Academy", "Có expert prerequisite", "Đối chiếu hành vi - chuyên gia"],
            ["ASSISTments 2012", "Có Q-matrix", "Baseline đã có 3-fold learner CV"],
            ["XES3G5M", "Benchmark lớn", "Metadata KC phân cấp, baseline fold 0"],
            ["Synthetic C2/C5", "Sanity corpora", "Kiểm tra độ nhạy ablation"],
        ],
        font_size=15,
    )
    add_textbox(slide, 0.9, 6.05, 11.5, 0.45, "Tất cả dataset dùng split theo người học với tỷ lệ 0.7 / 0.1 / 0.2 và seed 42.", size=15, color=GRAY)
    add_footer(slide, 5)

    # 6
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Kiểm toán rò rỉ và DAG")
    add_metric_card(slide, 0.75, 1.15, 2.7, 1.15, "0.000", "ECR flag trên mọi dataset", GREEN)
    add_metric_card(slide, 3.75, 1.15, 2.7, 1.15, "1,139", "cạnh DAG Junyi giữ lại", BLUE)
    add_metric_card(slide, 6.75, 1.15, 2.7, 1.15, "47%", "ứng viên Junyi bị tỉa", ORANGE)
    add_metric_card(slide, 9.75, 1.15, 2.7, 1.15, "701", "cạnh DAG XES3G5M", CYAN)
    add_bullets(
        slide,
        0.9,
        2.8,
        5.6,
        3.5,
        [
            "Không có bằng chứng rò rỉ split ở mức người học.",
            "ECR overlap cao phản ánh mẫu transition lặp lại giữa người học khác nhau.",
            "Cycle pruning là bước bắt buộc vì dữ liệu hành vi tạo nhiều quan hệ xung đột.",
        ],
        size=16.5,
        gap=6,
    )
    add_picture_fit(slide, render_pdf("fig_kt_graph_junyi.pdf"), 6.85, 2.65, 5.5, 3.45)
    add_footer(slide, 6)

    # 7
    slide = prs.slides.add_slide(blank)
    add_title(slide, "DAG Disruption Rate (DDR)")
    add_picture_fit(slide, render_pdf("fig_ddr_junyi.pdf"), 0.55, 1.22, 3.95, 3.1)
    add_picture_fit(slide, render_pdf("fig_ddr_assist2012.pdf"), 4.72, 1.22, 3.95, 3.1)
    add_picture_fit(slide, render_pdf("fig_ddr_xes3g5m.pdf"), 8.88, 1.22, 3.95, 3.1)
    add_bullets(
        slide,
        0.85,
        4.95,
        11.8,
        1.2,
        [
            "Thứ tự tác động nhất quán: attribute masking < subgraph/random-walk < edge dropping < node dropping.",
            "DDR giúp chọn augmentation theo tác động cấu trúc, không chỉ theo mức nhiễu ngẫu nhiên.",
        ],
        size=15.5,
        color=GRAY,
        gap=4,
    )
    add_footer(slide, 7)

    # 8
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Baseline KT cập nhật")
    add_small_table(
        slide,
        0.55,
        1.2,
        12.25,
        5.25,
        ["Dataset", "Mô hình", "AUC", "ACC", "NLL", "Ghi chú"],
        [
            ["ASSIST", "simpleKT", "0.968", "0.916", "0.173", "3-fold"],
            ["ASSIST", "GKT", "0.961", "0.907", "0.185", "-0.007 AUC vs simpleKT"],
            ["Junyi", "simpleKT", "0.989", "0.962", "0.093", "fold 0"],
            ["Junyi", "SKT", "0.986", "0.954", "0.107", "cache bổ sung"],
            ["XES3G5M", "simpleKT", "0.874", "0.857", "0.325", "fold 0"],
            ["XES3G5M", "GKT", "0.835", "0.842", "0.365", "-0.039 AUC"],
        ],
        font_size=10.8,
    )
    add_footer(slide, 8)

    # 9
    slide = prs.slides.add_slide(blank)
    add_title(slide, "ASSISTments 3-fold learner CV")
    add_small_table(
        slide,
        0.85,
        1.25,
        7.25,
        4.4,
        ["Mô hình", "AUC", "ACC", "NLL", "Wilcoxon p"],
        [
            ["simpleKT", "0.968 ± 0.000", "0.916 ± 0.001", "0.173 ± 0.001", "---"],
            ["GKT", "0.961 ± 0.001", "0.907 ± 0.001", "0.185 ± 0.001", "0.250"],
            ["GIKT", "--", "--", "--", "cần rerun"],
            ["SKT", "0.953 ± 0.001", "0.898 ± 0.001", "0.198 ± 0.001", "0.250"],
            ["DyGKT", "0.952 ± 0.001", "0.899 ± 0.001", "0.200 ± 0.002", "0.250"],
        ],
        font_size=11.2,
    )
    add_bullets(
        slide,
        8.55,
        1.55,
        3.9,
        3.8,
        [
            "Wilcoxon với n=3 fold bị underpowered.",
            "GKT/SKT/DyGKT thấp hơn simpleKT trên ASSIST.",
            "GIKT native bị loại tạm thời do lỗi alignment đã được sửa, cần rerun.",
        ],
        size=16,
        gap=8,
    )
    add_footer(slide, 9)

    # 10
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Ablation: train-only vs full-log graph")
    add_metric_card(slide, 0.8, 1.3, 3.05, 1.25, "< 0.001", "|ΔAUC| trên public benchmarks", GREEN)
    add_metric_card(slide, 4.2, 1.3, 3.05, 1.25, "+0.004", "GIKT trên Synthetic C5", ORANGE)
    add_metric_card(slide, 7.6, 1.3, 3.05, 1.25, "-0.006", "GKT trên Synthetic C5", RED)
    add_bullets(
        slide,
        0.85,
        3.1,
        11.9,
        2.4,
        [
            "Full-log graph không cải thiện headline AUC/ACC trên ASSISTments, XES3G5M và Junyi ở ba chữ số thập phân.",
            "Kết quả không phủ nhận rủi ro rò rỉ; nó cho thấy bộ lọc cạnh hiện tại ổn định trên các benchmark lớn.",
            "Train-only graph không gây phạt hiệu năng đáng kể, nên là mặc định an toàn cho benchmark.",
        ],
        size=17,
        gap=7,
    )
    add_footer(slide, 10)

    # 11
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Đối chiếu ground-truth trên Junyi")
    add_picture_fit(slide, render_pdf("fig_pr_curve.pdf"), 0.65, 1.25, 6.3, 4.75)
    add_metric_card(slide, 7.35, 1.45, 2.4, 1.12, "0.63", "node Jaccard", BLUE)
    add_metric_card(slide, 10.0, 1.45, 2.4, 1.12, "0.18", "edge F1", ORANGE)
    add_metric_card(slide, 8.65, 2.95, 2.4, 1.12, "0.26", "direction agreement", RED)
    add_bullets(
        slide,
        7.35,
        4.55,
        5.05,
        1.1,
        [
            "Hành vi và chuyên gia liên quan ở mức nút, khác rõ ở mức cạnh.",
            "Đồ thị hành vi không nên được xem là thay thế rẻ cho expert DAG.",
        ],
        size=14.5,
        color=GRAY,
        gap=3,
    )
    add_footer(slide, 11)

    # 12
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Giới hạn và diễn giải")
    add_bullets(
        slide,
        0.8,
        1.3,
        12.0,
        4.8,
        [
            "Junyi, XES3G5M và synthetic hiện vẫn là fold 0 trong baseline chính; ASSISTments đã có 3-fold.",
            "Junyi mới có SKT cache; GKT/GIKT/DyGKT/DGEKT còn thiếu do giới hạn tài nguyên.",
            "TBVR cao đo mức trộn trong train timeline, không phải lỗi split validation/test.",
            "Cycle pruning loại xung đột yếu nhất trong chu trình; cần báo cáo độ nhạy theo mức tỉa.",
            "Kết luận hướng tới kỷ luật benchmark và provenance, không phải phủ định graph-KT.",
        ],
        size=18,
        gap=7,
    )
    add_footer(slide, 12)

    # 13
    slide = prs.slides.add_slide(blank)
    add_title(slide, "Thông điệp chính")
    add_metric_card(slide, 0.95, 1.35, 3.3, 1.45, "1", "Đồ thị KT phải có provenance theo fold", BLUE)
    add_metric_card(slide, 5.0, 1.35, 3.3, 1.45, "2", "Train-only không làm giảm headline AUC", GREEN)
    add_metric_card(slide, 9.05, 1.35, 3.3, 1.45, "3", "Behavioral graph ≠ expert graph", ORANGE)
    add_bullets(
        slide,
        1.1,
        3.65,
        11.3,
        1.7,
        [
            "So sánh graph-augmented KT và sequence-only KT cần kiểm soát nguồn gốc cạnh.",
            "Giao thức cung cấp pipeline tái lập: split, graph, audit, baseline, ablation, cold-start.",
            "Đây là tài nguyên benchmark/protocol, không phải một mô hình KT mới.",
        ],
        size=17.5,
        gap=6,
    )
    add_textbox(slide, 4.1, 6.45, 5.2, 0.38, "Xin cảm ơn!", size=22, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 13)

    try:
        prs.save(OUT)
    except PermissionError:
        fallback = OUT.with_name("baocao_gikt_fixed.pptx")
        prs.save(fallback)
        print(f"{OUT} is locked; wrote {fallback} instead")


if __name__ == "__main__":
    make_deck()
    print(f"Wrote {OUT}")
