"""Build a seminar .pptx for the APIN paper.

Generates paper/APIN_seminar.pptx from the paper's key results and figures.
Figures (PDF) are rasterised to PNG with PyMuPDF, embedded, then temp PNGs
are removed (python-pptx copies image bytes into the deck).
"""
from __future__ import annotations

import shutil
from pathlib import Path

import fitz  # PyMuPDF
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
OUT = ROOT / "paper" / "APIN_seminar.pptx"
ASSETS = ROOT / "paper" / "_pptx_assets"

# ----------------------------------------------------------------------------
# Palette
DARK = RGBColor(0x14, 0x2A, 0x4A)     # deep navy
NAVY2 = RGBColor(0x1E, 0x3C, 0x66)
ACCENT = RGBColor(0xE0, 0x7A, 0x2B)   # amber
TEAL = RGBColor(0x1E, 0x7A, 0x7A)
LIGHT = RGBColor(0xF2, 0xF5, 0xF9)
GRAY = RGBColor(0x53, 0x59, 0x63)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
RED = RGBColor(0xB0, 0x3A, 0x2E)

FONT = "Calibri"
FONT_H = "Calibri"

SW, SH = Inches(13.333), Inches(7.5)


# ----------------------------------------------------------------------------
def rasterise(pdf_name: str, zoom: float = 3.0) -> Path:
    ASSETS.mkdir(exist_ok=True)
    src = FIG / pdf_name
    out = ASSETS / (Path(pdf_name).stem + ".png")
    doc = fitz.open(src)
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    pix.save(out)
    doc.close()
    return out


def png_asset(png_name: str) -> Path:
    ASSETS.mkdir(exist_ok=True)
    out = ASSETS / png_name
    shutil.copy(FIG / png_name, out)
    return out


# ----------------------------------------------------------------------------
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
    from pptx.enum.shapes import MSO_SHAPE
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    fill(sp, color)
    sp.shadow.inherit = False
    return sp


def textbox(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    return tb, tf


def set_run(r, text, size, color, bold=False, italic=False, font=FONT):
    r.text = text
    r.font.size = Pt(size)
    r.font.color.rgb = color
    r.font.bold = bold
    r.font.italic = italic
    r.font.name = font


def header(slide, title, kicker=None):
    """Title bar for content slides."""
    rect(slide, 0, 0, SW, Inches(1.15), DARK)
    rect(slide, 0, Inches(1.15), SW, Inches(0.06), ACCENT)
    tb, tf = textbox(slide, Inches(0.55), Inches(0.16), Inches(12.2), Inches(0.95))
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    if kicker:
        p = tf.paragraphs[0]
        set_run(p.add_run(), kicker.upper(), 12, ACCENT, bold=True)
        p2 = tf.add_paragraph()
        set_run(p2.add_run(), title, 26, WHITE, bold=True, font=FONT_H)
    else:
        p = tf.paragraphs[0]
        set_run(p.add_run(), title, 28, WHITE, bold=True, font=FONT_H)


def footer(slide):
    _num["n"] += 1
    tb, tf = textbox(slide, Inches(0.4), Inches(7.02), Inches(9.5), Inches(0.4))
    p = tf.paragraphs[0]
    set_run(p.add_run(),
            "Leakage-Controlled Concept-Graph Audit for Knowledge Tracing  \u2022  Applied Intelligence",
            9, GRAY)
    tb2, tf2 = textbox(slide, Inches(12.5), Inches(7.02), Inches(0.7), Inches(0.4))
    p2 = tf2.paragraphs[0]
    p2.alignment = PP_ALIGN.RIGHT
    set_run(p2.add_run(), str(_num["n"]), 10, GRAY, bold=True)


def bullets(slide, items, x=Inches(0.65), y=Inches(1.5), w=Inches(12.0),
            h=Inches(5.3), base=17):
    """items: list of dicts {t, lvl, bold, color, space}."""
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
        # bullet marker
        marker = it.get("marker", "\u25AA " if lvl == 0 else "\u2013 ")
        if it.get("nomark"):
            marker = ""
        lead = it.get("lead")
        if lead:
            set_run(p.add_run(), marker, size, ACCENT if lvl == 0 else GRAY, bold=True)
            set_run(p.add_run(), lead, size, color, bold=True)
            set_run(p.add_run(), it["t"], size, color)
        else:
            set_run(p.add_run(), marker + it["t"], size, color,
                    bold=it.get("bold", False))
    return tf


def content(title, items, kicker=None, **kw):
    s = blank_slide()
    header(s, title, kicker)
    bullets(s, items, **kw)
    footer(s)
    return s


def figure_slide(title, img_path, kicker=None, caption=None,
                 img_w=None, right_text=None):
    s = blank_slide()
    header(s, title, kicker)
    if right_text is None:
        # centered large figure
        w = img_w or Inches(8.6)
        pic = s.shapes.add_picture(str(img_path), Inches(0), Inches(1.5), width=w)
        # center horizontally
        pic.left = int((SW - pic.width) / 2)
        pic.top = Inches(1.55)
        if pic.height > Inches(5.0):
            pic = None  # already added; skip
        if caption:
            tb, tf = textbox(s, Inches(0.8), Inches(6.5), Inches(11.7), Inches(0.5))
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            set_run(p.add_run(), caption, 12, GRAY, italic=True)
    else:
        w = img_w or Inches(6.7)
        pic = s.shapes.add_picture(str(img_path), Inches(0.5), Inches(1.6), width=w)
        if pic.height > Inches(5.0):
            pic.height = Inches(5.0)
        bullets(s, right_text, x=Inches(7.6), y=Inches(1.7), w=Inches(5.4),
                h=Inches(5.0), base=15)
        if caption:
            tb, tf = textbox(s, Inches(0.5), Inches(6.7), Inches(6.8), Inches(0.4))
            p = tf.paragraphs[0]
            set_run(p.add_run(), caption, 11, GRAY, italic=True)
    footer(s)
    return s


def section(title, subtitle=None):
    s = blank_slide()
    rect(s, 0, 0, SW, SH, DARK)
    rect(s, Inches(0.9), Inches(3.05), Inches(1.7), Inches(0.12), ACCENT)
    tb, tf = textbox(s, Inches(0.85), Inches(3.25), Inches(11.6), Inches(1.6))
    p = tf.paragraphs[0]
    set_run(p.add_run(), title, 40, WHITE, bold=True, font=FONT_H)
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
        "APPLIED INTELLIGENCE  \u2022  RESEARCH SEMINAR", 14, ACCENT, bold=True)
tb, tf = textbox(s, Inches(0.9), Inches(1.75), Inches(11.7), Inches(2.6))
set_run(tf.paragraphs[0].add_run(),
        "Leakage-Controlled Concept Graph Construction and Cold-Start "
        "Diagnostic Protocol for Knowledge Tracing", 33, WHITE, bold=True,
        font=FONT_H)
tb, tf = textbox(s, Inches(0.9), Inches(4.75), Inches(11.7), Inches(1.4))
p = tf.paragraphs[0]
set_run(p.add_run(), "Dao Minh Tuan, Nguyen Khanh Trinh, Nguyen Tien Duong, "
        "Ngo Quoc Khanh, ", 15, WHITE)
set_run(p.add_run(), "Nguyen Van Hau", 15, ACCENT, bold=True)
set_run(p.add_run(), " (corresponding), Le Hoang Son", 15, WHITE)
p2 = tf.add_paragraph()
p2.space_before = Pt(6)
set_run(p2.add_run(), "Hung Yen University of Technology and Education  \u2022  "
        "Vietnam National University, Hanoi", 13, RGBColor(0xB9, 0xC6, 0xD8))
tb, tf = textbox(s, Inches(0.9), Inches(6.5), Inches(11.7), Inches(0.6))
set_run(tf.paragraphs[0].add_run(),
        "An audit protocol \u2014 not a new KT backbone \u2014 for trustworthy "
        "graph-enhanced knowledge tracing", 14, RGBColor(0xD8, 0xE0, 0xEC),
        italic=True)

# 2. AGENDA
content("Agenda", kicker="Overview", items=[
    {"t": "Motivation: hidden leakage in graph-enhanced knowledge tracing", "lead": "1. "},
    {"t": "The problem: graphs as a back-channel for held-out information", "lead": "2. "},
    {"t": "Contributions: an audit protocol and its five components", "lead": "3. "},
    {"t": "Method: leakage control, DAG validation, DDR, cold-start, GT cross-validation", "lead": "4. "},
    {"t": "The two-factor law: throughput \u00d7 reliance", "lead": "5. "},
    {"t": "Results: conditional harm, model-specific ordering, ground-truth divergence", "lead": "6. "},
    {"t": "From audit signal to deployment action (practitioner view)", "lead": "7. "},
    {"t": "Limitations, future work, and takeaways", "lead": "8. "},
], y=Inches(1.6))

# ---- SECTION: Motivation
section("1. Motivation & Problem", "Why graph construction is a leakage surface")

# 3. Background
content("Knowledge Tracing and concept graphs", kicker="Background", items=[
    {"t": "Knowledge Tracing (KT) estimates a learner's mastery of knowledge "
          "components (KCs) from interaction history.", "lead": "What: "},
    {"t": "Powers adaptive practice, intelligent tutoring, and curriculum "
          "recommendation.", "lvl": 1, "nomark": False},
    {"t": "Evolution: BKT \u2192 deep sequential models (DKT, DKVMN, AKT, "
          "simpleKT) \u2192 graph-enhanced models (GKT, GIKT, DGEKT).", "lead": "Trend: "},
    {"t": "Graph-enhanced KT propagates information over a KC graph "
          "(prerequisite / similarity relations).", "lead": "Graphs: "},
    {"t": "That auxiliary graph is usually built from the SAME interaction logs "
          "used for training and evaluation.", "lvl": 1, "color": RED},
    {"t": "Key question: is a reported graph gain real, or an artefact of how the "
          "graph was constructed?", "lead": "Gap: ", "before": 6, "color": NAVY2},
])

# 4. The leakage problem
content("The hidden leakage channel", kicker="Problem", items=[
    {"t": "When edges are pooled BEFORE the train/test split, held-out "
          "information reaches the model through the graph \u2014 even if the KT "
          "optimiser only sees the training fold.", "lead": "Mechanism: "},
    {"t": "Sequence-level fold splitting is necessary but NOT sufficient: the "
          "graph is a separate contamination surface.", "color": RED},
    {"t": "Worked example (leakage throughput):", "lead": "", "before": 6, "bold": True, "nomark": True},
    {"t": "Hot KC: 20 leaked traversals change edge support 40\u219260 \u2192 33% throughput.", "lvl": 1},
    {"t": "Very-cold KC: the same 20 raise support 4\u219224 \u2192 83% throughput.", "lvl": 1, "color": RED},
    {"t": "Leakage throughput scales INVERSELY with train-fold KC frequency \u2014 "
          "cold-start KCs are the highest-throughput entry points.", "lead": "Insight: ",
     "before": 6, "color": NAVY2},
    {"t": "Aggregate AUC is a late, unreliable alarm; we need to measure the "
          "channel directly.", "lead": "Therefore: "},
])

# ---- SECTION: Contributions
section("2. Contributions", "An audit protocol, not a new backbone")

# 5. Contributions
content("Five contributions (C1\u2013C5)", kicker="Contributions", items=[
    {"t": "Leakage-controlled construction: learner-based temporal splits + "
          "train-only prerequisite/similarity inference with per-edge provenance.", "lead": "C1  "},
    {"t": "Tiered leakage diagnostics: builder mass, TBMR, ECR-flag / ECR-overlap "
          "\u2014 measure contamination independently of accuracy.", "lead": "C2  "},
    {"t": "DAG validation + DDR (DAG Disruption Rate): a structural metric that "
          "separates augmentation operators.", "lead": "C3  "},
    {"t": "Cold-start stratification: per-KC-frequency reporting that exposes "
          "where leakage and weak evidence concentrate.", "lead": "C4  "},
    {"t": "Ground-truth cross-validation: behavioural inference vs. expert "
          "prerequisite curation (edge / direction / reachability / node-Jaccard).", "lead": "C5  "},
    {"t": "Positioning: a decision-support & leakage risk-scoring layer for "
          "trustworthy deployment \u2014 not a route to higher headline accuracy.",
     "lead": "Framing: ", "before": 8, "color": NAVY2},
])

# ---- SECTION: Method
section("3. The Audit Protocol", "Construction \u2192 diagnostics \u2192 validation")

# 6. Leakage control
content("Leakage control & provenance", kicker="Method \u2014 C1/C2", items=[
    {"t": "Split by learner and time; infer edges only from the training fold "
          "(F_train), never the pooled log.", "lead": "Train-only: "},
    {"t": "Log fold-specific provenance for every retained edge (reproducible, "
          "cross-paper comparable exports).", "lead": "Provenance: "},
    {"t": "Diagnostic tiers:", "before": 6, "bold": True, "nomark": True},
    {"t": "Builder mass / TBMR \u2014 within-train temporal mixing & throughput.", "lvl": 1},
    {"t": "ECR-flag \u2014 learner-disjointness (can be 0 while throughput is high!).", "lvl": 1},
    {"t": "ECR-overlap \u2014 cold-start neighbourhood contamination.", "lvl": 1},
    {"t": "Fold-disjoint splits are necessary but insufficient; scalar leakage "
          "summaries can hide throughput-driven shifts.", "lead": "Lesson: ",
     "before": 6, "color": RED},
])

# 7. DDR figure
ddr = rasterise("fig_ddr_junyi.pdf")
figure_slide("DDR: DAG Disruption Rate", ddr, kicker="Method \u2014 C3",
             right_text=[
                 {"t": "DDR measures how much an augmentation operator damages "
                       "the prerequisite DAG at a fixed perturbation budget.", "lead": "Idea: "},
                 {"t": "Sweeps 5 operators (edge drop, node drop, \u2026, "
                       "prereq-preserve).", "lead": "Sweep: "},
                 {"t": "A prerequisite-preserving operator that protects the "
                       "transitive-reduction backbone is measurably LESS "
                       "disruptive than edge dropping at matched budget.",
                  "lead": "Finding: ", "color": GREEN},
                 {"t": "DDR applies to any directed curriculum graph consumed by "
                       "KT or pretraining pipelines.", "lead": "Scope: "},
             ], caption="DDR vs. perturbation budget (Junyi).")

# 8. Cold-start + GT-XV combined method
content("Cold-start & ground-truth cross-validation", kicker="Method \u2014 C4/C5", items=[
    {"t": "Cold-start stratification (C4):", "bold": True, "nomark": True},
    {"t": "Report per-stratum metrics by KC frequency (very-cold \u2192 hot).", "lvl": 1},
    {"t": "Aggregate AUC hides small-stratum behaviour; very-cold counts are "
          "small (n = 19\u2013161) \u2192 high variance, read with n.", "lvl": 1},
    {"t": "Ground-truth cross-validation (C5):", "bold": True, "nomark": True, "before": 6},
    {"t": "Compare train-only behavioural inference against expert prerequisite "
          "annotation on Junyi.", "lvl": 1},
    {"t": "Result: node-level agreement but edge-level DIVERGENCE \u2014 "
          "behavioural inference is NOT a low-cost proxy for expert curation.", "lvl": 1,
     "color": RED},
])

# 9. PR curve figure
pr = rasterise("fig_pr_curve.pdf")
figure_slide("Ground-truth validation on Junyi", pr, kicker="Method \u2014 C5",
             right_text=[
                 {"t": "Behavioural inference recovers expert prerequisite edges "
                       "well above chance\u2026", "lead": "Signal: "},
                 {"t": "\u2026but the two signals diverge at the edge level and "
                       "are best treated as COMPLEMENTARY relations.", "lead": "Nuance: "},
                 {"t": "Recommendation: consume an inferred behavioural graph and "
                       "an expert graph as separate inputs.", "lead": "So what: ",
                  "color": NAVY2},
             ], caption="Precision\u2013recall of inferred vs. expert edges.")

# ---- SECTION: Results
section("4. The Two-Factor Law & Results", "When does graph leakage actually hurt?")

# 10. Datasets
content("Datasets & experimental setup", kicker="Setup", items=[
    {"t": "XES3G5M \u2014 primary model-comparison benchmark (dense, transition-rich).", "lead": "Primary: "},
    {"t": "ASSISTments 2012 \u2014 secondary; single-skill Q-matrix (similarity edges infeasible).", "lead": "Secondary: "},
    {"t": "Junyi Academy \u2014 saturated sanity check + ground-truth cross-validation.", "lead": "GT / sanity: "},
    {"t": "Two synthetic logs \u2014 controlled concept structure.", "lead": "Synthetic: "},
    {"t": "Backbones: simpleKT / AKT (sequence-only), GKT & GIKT (graph-reliant), "
          "DGEKT; pyKT wiring, learner-disjoint folds, train-only graph export.",
     "lead": "Models: ", "before": 6},
])

# 11. Two-factor 2x2 TABLE slide
s = blank_slide()
header(s, "The two-factor law: throughput \u00d7 reliance", kicker="Key result")
tb, tf = textbox(s, Inches(0.65), Inches(1.4), Inches(12), Inches(0.7))
set_run(tf.paragraphs[0].add_run(),
        "Graph-mediated leakage shifts AUC only when BOTH factors are high. "
        "Three of four regimes are \u2248 0.", 16, DARK)
rows, cols = 3, 3
tbl_w, tbl_h = Inches(11.6), Inches(3.6)
gtbl = s.shapes.add_table(rows, cols, Inches(0.85), Inches(2.25), tbl_w, tbl_h).table
gtbl.columns[0].width = Inches(3.6)
gtbl.columns[1].width = Inches(4.0)
gtbl.columns[2].width = Inches(4.0)
data = [
    ["", "Low reliance (simpleKT)", "High reliance (GKT, GIKT)"],
    ["Low throughput\n(train-only vs. full-log)", "\u2248 0", "\u2264 0.003  (full-log ablation)"],
    ["High throughput\n(20% test-fold injection)", "\u2248 0  (0.850\u21920.858)",
     "+0.05 GKT, +0.03 GIKT"],
]
for r in range(rows):
    for c in range(cols):
        cell = gtbl.cell(r, c)
        cell.text = data[r][c]
        para = cell.text_frame.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER if c > 0 or r == 0 else PP_ALIGN.LEFT
        run = para.runs[0] if para.runs else para.add_run()
        run.font.size = Pt(15)
        run.font.name = FONT
        if r == 0 or c == 0:
            run.font.bold = True
            run.font.color.rgb = WHITE
            cell.fill.solid(); cell.fill.fore_color.rgb = DARK
        else:
            cell.fill.solid()
            if r == 2 and c == 2:
                cell.fill.fore_color.rgb = RGBColor(0xF7, 0xD9, 0xC4)  # highlight harm cell
                run.font.color.rgb = RED; run.font.bold = True
            else:
                cell.fill.fore_color.rgb = LIGHT
                run.font.color.rgb = GRAY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
tb, tf = textbox(s, Inches(0.85), Inches(6.15), Inches(11.7), Inches(0.8))
p = tf.paragraphs[0]
set_run(p.add_run(), "Takeaway: ", 15, ACCENT, bold=True)
set_run(p.add_run(), "harm \u2248 throughput \u00d7 reliance. AUC is silent in 3/4 "
        "regimes \u2192 the audit measures throughput directly instead.", 15, DARK)
footer(s)

# 12. Conditional harm / downstream
dd = png_asset("fig_ddr_downstream.png")
figure_slide("Conditional harm: the manipulation check", dd, kicker="Result",
             right_text=[
                 {"t": "Gate downstream claims on a manipulation check: does "
                       "destroying the graph move AUC?", "lead": "Test: "},
                 {"t": "GKT on XES3G5M PASSES: graph destruction costs "
                       "0.07\u20130.09 AUC.", "lead": "Reliant: ", "color": GREEN},
                 {"t": "Here DDR predicts AUC loss (r = 0.97) and prereq-preserve "
                       "costs the least accuracy.", "lvl": 1},
                 {"t": "DGEKT & GKT on ASSISTments FAIL: total destruction moves "
                       "AUC \u2264 0.002 \u2192 graph is effectively unused.", "lead": "Inert: ",
                  "color": RED},
                 {"t": "Structural damage translates into predictive damage ONLY "
                       "on graph-reliant, check-passing backbones.", "lead": "So: ",
                  "color": NAVY2},
             ], caption="DDR \u2192 downstream AUC (graph-reliant backbone).")

# 13. Model-specific ordering
content("Model-specific ordering on XES3G5M", kicker="Result", items=[
    {"t": "Primary trio under the released 10-epoch budget:", "bold": True, "nomark": True},
    {"t": "simpleKT / AKT \u2248 0.875   \u2022   GIKT \u2248 0.878   \u2022   GKT \u2248 0.834.", "lvl": 1},
    {"t": "GKT trails simpleKT by \u2248 0.041 AUC (paired-t 95% CI [\u22120.044, \u22120.038]).", "lead": "Gap: ", "color": RED},
    {"t": "Epoch-extended GKT (30 epochs) recovers only \u2248 0.003 AUC; pooled "
          "\u0394 \u2248 \u22120.038 over nine folds \u2014 the under-performance persists.",
     "lead": "Not a budget artefact: "},
    {"t": "Graph reliance \u2260 accuracy advantage: reading the graph can even "
          "cost accuracy when the sequence backbone is already strong.",
     "lead": "Message: ", "before": 6, "color": NAVY2},
])

# ---- SECTION: Practitioner
section("5. From Audit to Action", "What a practitioner does differently")

# 14. Decision map TABLE
s = blank_slide()
header(s, "Decision map: audit signal \u2192 deployment action", kicker="Applied value")
rows = 6
t = s.shapes.add_table(rows, 3, Inches(0.55), Inches(1.45), Inches(12.25), Inches(5.1)).table
t.columns[0].width = Inches(3.7)
t.columns[1].width = Inches(4.0)
t.columns[2].width = Inches(4.55)
dm = [
    ["Audit signal", "Reading", "Action"],
    ["Builder mass / TBMR", "Rises (pooled vs. train-only)", "Enforce train-only graph; distrust the gain"],
    ["ECR-flag = 0 but high throughput", "Disjoint yet contaminated", "Split is insufficient; keep provenance logs"],
    ["Manipulation check", "AUC unmoved by graph destruction", "Graph-inert: DDR = reproducibility scaffolding"],
    ["DDR vs. AUC (r \u2248 0.97)", "Monotone on graph-reliant backbone", "Prefer prereq-preserve; DDR is a design target"],
    ["Cold-start stratum", "Highest throughput at thin support", "Report per-stratum provenance"],
]
for r in range(rows):
    for c in range(3):
        cell = t.cell(r, c); cell.text = dm[r][c]
        para = cell.text_frame.paragraphs[0]
        run = para.runs[0]
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
content("What a practitioner does differently", kicker="Applied value", items=[
    {"t": "Build the graph fold-clean \u2014 infer from the train fold only and "
          "export per-edge provenance.", "lead": "1. "},
    {"t": "Read the throughput indicators, not the accuracy \u2014 locate the "
          "corpus in the throughput \u00d7 reliance grid.", "lead": "2. "},
    {"t": "Gate any downstream claim on a manipulation check \u2014 verify the "
          "backbone actually reads the graph before attributing gains.", "lead": "3. "},
    {"t": "Prefer structure-preserving augmentation \u2014 use the "
          "prereq-preserving operator that DDR rewards.", "lead": "4. "},
    {"t": "These four steps are the actionable core of the checklist and the "
          "decision map.", "lead": "", "before": 8, "nomark": True, "color": NAVY2, "bold": True},
], y=Inches(1.6))

# ---- SECTION: Wrap up
section("6. Discussion & Takeaways")

# 16. Limitations & future work
content("Limitations & future work", kicker="Discussion", items=[
    {"t": "Similarity edges depend on the Q-matrix (infeasible under single-skill "
          "coding, e.g. ASSISTments).", "lead": "Limitation: "},
    {"t": "Public-benchmark leakage effects are small because an aggressive "
          "support filter throttles throughput \u2014 not because leakage is "
          "harmless in general.", "lvl": 1},
    {"t": "Very-cold strata have small n \u2192 high-variance per-stratum AUC.", "lvl": 1},
    {"t": "Disaggregate reported graph-KT gains: leakage-surviving vs. "
          "construction-dependent vs. backbone-dependent components.", "lead": "Future: "},
    {"t": "Combine inferred + expert graphs as separate relations; extend "
          "manipulation-check-gated downstream tests; reachability-disruption audits.",
     "lvl": 1},
])

# 17. Conclusion
content("Key takeaways", kicker="Conclusion", items=[
    {"t": "Graph construction is a first-class experimental component \u2014 and a "
          "leakage surface \u2014 not a preprocessing afterthought.", "lead": "1. "},
    {"t": "Harm is conditional: it needs high throughput AND a graph-reliant, "
          "manipulation-check-passing backbone.", "lead": "2. "},
    {"t": "Measure the channel directly (builder mass, TBMR); AUC is a late, "
          "unreliable alarm.", "lead": "3. "},
    {"t": "DDR + a prereq-preserving operator give a principled, structure-aware "
          "augmentation choice.", "lead": "4. "},
    {"t": "The deliverable is a decision-support & risk-scoring audit layer for "
          "trustworthy graph-enhanced KT.", "lead": "5. ", "color": NAVY2, "bold": True},
], y=Inches(1.6))

# 18. Thank you
s = blank_slide()
rect(s, 0, 0, SW, SH, DARK)
rect(s, Inches(0.9), Inches(3.7), Inches(1.7), Inches(0.12), ACCENT)
tb, tf = textbox(s, Inches(0.85), Inches(2.6), Inches(11.6), Inches(1.2))
set_run(tf.paragraphs[0].add_run(), "Thank you \u2014 Questions?", 44, WHITE,
        bold=True, font=FONT_H)
tb, tf = textbox(s, Inches(0.9), Inches(3.95), Inches(11.6), Inches(1.6))
p = tf.paragraphs[0]
set_run(p.add_run(), "Leakage-Controlled Concept-Graph Audit for Knowledge Tracing",
        17, RGBColor(0xD8, 0xE0, 0xEC))
p2 = tf.add_paragraph(); p2.space_before = Pt(8)
set_run(p2.add_run(), "Corresponding author: Nguyen Van Hau \u2014 nvhau666@gmail.com",
        14, RGBColor(0xB9, 0xC6, 0xD8))
p3 = tf.add_paragraph()
set_run(p3.add_run(), "Code & artefacts: github.com/tuanymc/p0_project",
        14, RGBColor(0xB9, 0xC6, 0xD8))

prs.save(str(OUT))
print(f"Saved {OUT}  ({len(prs.slides)} slides)")

# cleanup rasterised assets (bytes already embedded)
shutil.rmtree(ASSETS, ignore_errors=True)
