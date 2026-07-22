# Updated verification log (language final pass)

## Invariants

| Check | Result |
|---|---|
| No experiments | PASS |
| No result CSV edits | PASS |
| S21 values unchanged | PASS (0.834557/0.840181/…/mean 0.003451) |
| S22 absent | PASS |
| Findings not CLOSED | PASS |

## Builds

- Canonical: built as `main_APIN_rebuild.pdf` then copied to `main_APIN.pdf` (initial write failed because PDF was open/locked).
- Flat: `python scripts/build_submission_APIN_flat.py` then clean-room compile in `%TEMP%\apin_flat_clean_*`.
- Logs: `final_canonical_build_log.txt`, `final_flat_clean_build_log.txt`.

## PDF hashes

- Canonical: `BD73F04EFEDC5FBAA8D057B52B86428C8486DB706A7756A19314E3BB98A18EC1`
- Flat clean-room: `9EF13D4A3FF47DDA33CF65643497E4876CFB0A0D77A093E23B8B182A9655F8E6`

## Residual warnings

- Template font-shape warnings (`OT1/cmr/bx/sc*`)
- Pre-existing TikZ Overfull ~32pt
