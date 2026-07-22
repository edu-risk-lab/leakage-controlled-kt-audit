import fitz
from pathlib import Path

pdf = fitz.open(r"D:/0. NCS/CODE/p0_project/paper/main_APIN_fig3.pdf")
out = Path(r"D:/0. NCS/CODE/p0_project/audit/2026-07-17-1541/figure4_page.png")
for i, page in enumerate(pdf):
    if "Train-only prerequisite construction pipeline" in page.get_text("text"):
        print("fig4 page", i + 1)
        out.write_bytes(
            page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False).tobytes("png")
        )
        break
else:
    print("figure 4 caption not found")
