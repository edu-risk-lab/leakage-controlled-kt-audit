"""DEPRECATED bootstrap/injection table generator (historical placeholders).

Table S18 (downstream_auc_injection) must come from verified GPU runs:
  python -m scripts.collect_injection_auc

This script refuses to overwrite injection artefacts. Bootstrap CI rows are
likewise superseded by scripts/bootstrap_auc_ci.py and generate_phase_c_tables.
"""

from __future__ import annotations

import sys


def main() -> None:
    sys.stderr.write(
        "create_fake_tables.py is deprecated.\n"
        "  Table S18: python -m scripts.collect_injection_auc\n"
        "  Bootstrap CI: python -m scripts.bootstrap_auc_ci\n"
        "Verified injection AUC (fold 0, 2026-07-23): see results/tables/downstream_auc_injection.csv\n"
    )
    raise SystemExit(1)


if __name__ == "__main__":
    main()
