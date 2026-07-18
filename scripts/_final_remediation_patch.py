"""Final-remediation patches for paper/main_APIN.tex (authorized 2026-07-17)."""

from __future__ import annotations

from pathlib import Path

TEX = Path(__file__).resolve().parents[1] / "paper" / "main_APIN.tex"

PATCHES: list[tuple[str, str]] = [
    # Abstract +0.003451 wording
    (
        r"""targeted three-fold configuration-sensitivity check yielded a
small mean AUC increase of approximately $0.003$, with uncertainty
including zero (Table~S21).""",
        r"""targeted three-fold configuration-sensitivity check produced an
observed mean AUC difference of approximately ${+}0.003$, with an
uncertainty interval including zero (Table~S21).""",
    ),
    # C5
    (
        r"""targeted seed-42 three-fold extended-training check (Table~S21; maximum 30~epochs,
  batch~16) showed a mean AUC increase of $0.003451$ over primary GKT, with an
  approximate 95\% CI including zero; because both maximum epochs and batch size
  changed, this is configuration sensitivity rather than an isolated epoch effect.""",
        r"""targeted seed-42 three-fold extended-training check (Table~S21; maximum 30~epochs,
  batch~16) produced an observed mean AUC that was $0.003451$ higher under the
  extended-training configuration; however, the approximate 95\% CI
  $[-0.004,0.011]$ included zero. Because both the maximum epoch budget and batch
  size changed, this exploratory comparison does not isolate the effect of epochs.""",
    ),
    # Baseline diagnostic
    (
        r"""configuration (maximum 30~epochs, batch~16) showed a mean AUC increase of
$0.003451$ over the primary GKT configuration (maximum 10~epochs, batch~4);
the approximate 95\% CI included zero, and because both maximum epochs and batch
size changed, the comparison does not isolate an epoch-only effect.""",
        r"""configuration (maximum 30~epochs, batch~16), the observed mean AUC was
$0.003451$ higher than under the primary GKT configuration (maximum 10~epochs,
batch~4); however, the approximate 95\% CI $[-0.004,0.011]$ included zero.
Because both the maximum epoch budget and batch size changed, this exploratory
comparison does not isolate the effect of epochs.""",
    ),
    # Paragraph title + S15 sentence
    (
        r"""\paragraph{Training parity and comparison scope.}
Full epoch/batch parity is in Supplementary Table~S15.""",
        r"""\paragraph{Training-configuration disclosure and comparison scope.}
Training configurations and comparison scope are reported in
Supplementary Table~S15.""",
    ),
    # Training config paragraph mean AUC
    (
        r"""batch~16 versus primary maximum 10~epochs, batch~4): mean AUC increased by
$0.003451$, but the approximate 95\% CI $[-0.004,+0.011]$ included zero.
Because both the maximum epoch budget and batch size changed, this exploratory
comparison does not isolate the effect of epochs and is not a fully
compute-matched comparison.""",
        r"""batch~16 versus primary maximum 10~epochs, batch~4): the observed mean AUC was
$0.003451$ higher under the extended-training configuration; however, the
approximate 95\% CI $[-0.004,+0.011]$ included zero.
Because both the maximum epoch budget and batch size changed, this exploratory
comparison does not isolate the effect of epochs and is not a fully
compute-matched comparison.""",
    ),
    # Discussion
    (
        r"""targeted seed-42 three-fold check (Table~S21), extended-training GKT reached
mean AUC ${\approx}0.837$ (${+}0.003451$ vs.\ primary GKT; CI including zero);
this exploratory configuration-sensitivity result does not isolate epochs from
batch-size change.""",
        r"""targeted seed-42 three-fold check (Table~S21), extended-training GKT reached
mean AUC ${\approx}0.837$ (observed mean AUC $0.003451$ higher than primary GKT;
however, the approximate 95\% CI $[-0.004,0.011]$ included zero).
Because both the maximum epoch budget and batch size changed, this exploratory
comparison does not isolate the effect of epochs.""",
    ),
    # Caveats
    (
        r"""Table~S21 reports an exploratory seed-42 three-fold
extended-training configuration-sensitivity check (mean $\Delta$AUC ${+}0.003451$;
CI including zero) in which both maximum epochs and batch size changed relative
to primary GKT.""",
        r"""Table~S21 reports an exploratory seed-42 three-fold
extended-training configuration-sensitivity check in which the observed mean AUC
was $0.003451$ higher under the extended-training configuration; however, the
approximate 95\% CI $[-0.004,0.011]$ included zero, and both maximum epochs and
batch size changed relative to primary GKT.""",
    ),
    # Limitations
    (
        r"""Therefore, the observed ${+}0.003451$ mean
AUC change should be interpreted as exploratory configuration
sensitivity rather than an isolated epoch effect. The study does
not provide a fully compute-matched comparison.""",
        r"""Therefore, the observed mean AUC was $0.003451$ higher under the
extended-training configuration; however, the approximate 95\% CI
$[-0.004,0.011]$ included zero, and the result should be interpreted as
exploratory configuration sensitivity rather than an isolated epoch effect.
The study does not provide a fully compute-matched comparison.""",
    ),
    # Conclusion
    (
        r"""(Table~S21) yielded a small mean AUC increase of approximately $0.003$, with
uncertainty including zero.""",
        r"""(Table~S21) produced an observed mean AUC difference of approximately
${+}0.003$, with an uncertainty interval including zero.""",
    ),
    # Appendix index
    (
        r"""S15: training parity (Section~\ref{sec:supp-training-parity});""",
        r"""S15: training-configuration disclosure (Section~\ref{sec:supp-training-parity});""",
    ),
    # Section K + intro + caption + label
    (
        r"""\section{Training parity}
\label{sec:supp-training-parity}
Table~S15 (Table~\ref{tab:training-parity}) outlines hyperparameter parity
and model configuration across \texttt{pyKT} and native baselines.""",
        r"""\section{Training-configuration disclosure}
\label{sec:supp-training-parity}
Table~S15 (Table~\ref{tab:training_configurations}) reports the training
configurations and model-specific hyperparameters used across the \texttt{pyKT}
and native baselines.""",
    ),
    (
        r"""\caption{Training parity and hyperparameters (Table S15)}
\label{tab:training-parity}""",
        r"""\caption{Training configurations and hyperparameters (Table S15)}
\label{tab:training_configurations}""",
    ),
    # S16 prose about S21
    (
        r"""Table~S21 reports an exploratory
seed-42 three-fold configuration-sensitivity check (mean $\Delta$AUC ${+}0.003451$;
approximate 95\% CI including zero).""",
        r"""Table~S21 reports an exploratory
seed-42 three-fold configuration-sensitivity check in which the observed mean AUC
was $0.003451$ higher under the extended-training configuration; however, the
approximate 95\% CI $[-0.004,0.011]$ included zero.""",
    ),
    # S21 caption
    (
        r"""\caption{Targeted three-fold extended-training configuration sensitivity
check on XES3G5M using experiment seed~$42$. The primary GKT
configuration used a maximum of 10 epochs and batch size~4,
whereas the extended-training configuration used a maximum of
30 epochs and batch size~16. Mean AUC increased by $0.003451$;
however, the approximate 95\% confidence interval
$[-0.004, 0.011]$ included zero. Because both maximum epochs and
batch size changed, this exploratory comparison does not isolate
the effect of epochs.}""",
        r"""\caption{Targeted three-fold extended-training configuration-sensitivity
check on XES3G5M using experiment seed~$42$. The primary GKT
configuration used a maximum of 10 epochs and batch size~4,
whereas the extended-training configuration used a maximum of
30 epochs and batch size~16. The observed mean AUC was $0.003451$
higher under the extended-training configuration; however, the
approximate 95\% confidence interval $[-0.004, 0.011]$ included zero.
Because both maximum epochs and batch size changed, this
exploratory comparison does not isolate the effect of epochs.}""",
    ),
    # Closing appendix index
    (
        r"""S15: training parity; S16: $\Delta$AUC intervals for primary pairs;""",
        r"""S15: training-configuration disclosure; S16: $\Delta$AUC intervals for primary pairs;""",
    ),
    # Reporting-factor wording (budget disclosure, not matched budgets)
    (
        r"""should treat graph provenance and training-budget parity as first-order
reporting factors---while acknowledging that provenance control alone moved""",
        r"""should treat graph provenance and training-budget disclosure as first-order
reporting factors---while acknowledging that provenance control alone moved""",
    ),
    (
        r"""that omit graph-construction provenance, cold-start strata, and training-budget
parity are difficult to compare across papers even when aggregate AUC is""",
        r"""that omit graph-construction provenance, cold-start strata, and training-budget
disclosure are difficult to compare across papers even when aggregate AUC is""",
    ),
    # AI declaration before Declarations
    (
        r"""\bmhead{Acknowledgements}
The authors thank the maintainers of the Junyi Academy, ASSISTments, and
XES3G5M datasets and of the \texttt{pyKT} benchmark library, whose public
releases made this study possible.

\section*{Declarations}""",
        r"""\bmhead{Acknowledgements}
The authors thank the maintainers of the Junyi Academy, ASSISTments, and
XES3G5M datasets and of the \texttt{pyKT} benchmark library, whose public
releases made this study possible.

\section*{Declaration of generative AI-assisted work}
During the preparation of this manuscript, the authors used
generative AI tools, including ChatGPT and Cursor, to assist with
language refinement, internal-consistency checking, and
manuscript-quality auditing. All technical claims, references,
experimental configurations, numerical results, and revisions were
independently reviewed and verified by the authors. No generative
AI tool was listed as an author, and the authors take full
responsibility for the final content.

\section*{Declarations}""",
    ),
]


def main() -> None:
    text = TEX.read_text(encoding="utf-8")
    missing = []
    for old, new in PATCHES:
        if old not in text:
            missing.append(old[:100].replace("\n", " "))
            continue
        text = text.replace(old, new, 1)
    # Ensure no stale label refs remain
    text = text.replace(r"\ref{tab:training-parity}", r"\ref{tab:training_configurations}")
    TEX.write_text(text, encoding="utf-8")
    print(f"missing={len(missing)}")
    for m in missing:
        print("MISSING:", m)
    for needle in [
        "Full epoch/batch parity",
        "hyperparameter parity",
        "Training parity",
        "tab:training-parity}",
        "Mean AUC increased by",
        "showed a mean AUC increase",
        "yielded a small mean AUC increase",
        "Declaration of generative AI",
        "tab:training_configurations",
    ]:
        print(f"{text.count(needle):3d}  {needle}")


if __name__ == "__main__":
    main()
