import fitz
from pathlib import Path
from collections import defaultdict

pdf = fitz.open(r"D:/0. NCS/CODE/p0_project/paper/main_APIN_fig3.pdf")
page = pdf[8]
r = page.rect
crop = fitz.Rect(r.width * 0.28, 35, r.width * 0.74, 390)
pix = page.get_pixmap(matrix=fitz.Matrix(3.5, 3.5), clip=crop, alpha=False)
Path(r"D:/0. NCS/CODE/p0_project/audit/2026-07-17-1541/figure3_panel_b_crop.png").write_bytes(
    pix.tobytes("png")
)
pix2 = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
Path(r"D:/0. NCS/CODE/p0_project/audit/2026-07-17-1541/figure3_page-09.png").write_bytes(
    pix2.tobytes("png")
)

words = page.get_text("words")
b_words = [w for w in words if 200 < w[1] < 360 and 170 < w[0] < 430]
lines = defaultdict(list)
for w in b_words:
    lines[round(w[1] / 2)].append(w)
for y in sorted(lines):
    text = " ".join(x[4] for x in sorted(lines[y], key=lambda z: z[0]))
    keys = ("train", "val", "check", "graph", "select", "valid", "(b)", "optim", "kt", "construction")
    if any(k in text.lower() for k in keys):
        print(f"{y:6.1f} | {text}")

print("--- hyphen fragments ---")
for ln in page.get_text("text").splitlines():
    low = ln.lower()
    if "selec-" in low or "vali-" in low or "tion." in low and "selec" in low:
        print(repr(ln))
    if "checkpoint selection" in low or "validation-based" in low:
        print(repr(ln))
