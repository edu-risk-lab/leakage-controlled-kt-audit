import fitz
from pathlib import Path

pdf = fitz.open(r"D:/0. NCS/CODE/p0_project/paper/main_APIN_fig3.pdf")
out = Path(r"D:/0. NCS/CODE/p0_project/audit/2026-07-17-1541")
for i, page in enumerate(pdf):
    t = page.get_text("text")
    if "Research framework connecting" in t:
        print("framework page", i + 1)
        (out / "figure2_page.png").write_bytes(
            page.get_pixmap(matrix=fitz.Matrix(2.8, 2.8), alpha=False).tobytes("png")
        )
    if "End-to-end protocol plumbing" in t:
        print("pipelines page", i + 1)
        (out / "figure3_page-09.png").write_bytes(
            page.get_pixmap(matrix=fitz.Matrix(2.8, 2.8), alpha=False).tobytes("png")
        )
        r = page.rect
        (out / "figure3_panel_b_crop.png").write_bytes(
            page.get_pixmap(
                matrix=fitz.Matrix(3.0, 3.0),
                clip=fitz.Rect(30, 40, r.width - 30, 480),
                alpha=False,
            ).tobytes("png")
        )
print("done")
