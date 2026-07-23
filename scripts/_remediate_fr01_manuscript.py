"""One-shot authorized remediation patches for paper/main_APIN.tex (2026-07-17).

Does not touch historical fold-result CSVs. Idempotent where possible.

NOTE (2026-07-23): Injection patches below (+0.05 GKT / +0.008 simpleKT) are
superseded by verified S18 decoupling (audit/2026-07-23-A1-injection-verified-results.md).
Do not re-run against submission_APIN/main_APIN.tex without review.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper" / "main_APIN.tex"

# Ordered replacements: (old, new). First match only unless marked ALL.
PATCHES: list[tuple[str, str, bool]] = [
    # Macros: retire nine-fold claim macros; keep gain macro as approx wording helper
    (
        r"""\newcommand{\GKTthirtydeltavec}{-0.038}
\newcommand{\GKTthirtydeltaci}{[$-0.040$, $-0.035$]}
\newcommand{\GKTthirtyseedFortydeltaci}{[$-0.048$, $-0.027$]}
\newcommand{\GKTepochgain}{+0.003}
""",
        r"""% Retired nine-fold extension macros (do not use in submission prose).
\newcommand{\GKTthirtydeltavec}{\textbf{??}}
\newcommand{\GKTthirtydeltaci}{\textbf{??}}
\newcommand{\GKTthirtyseedFortydeltaci}{\textbf{??}}
\newcommand{\GKTepochgain}{+0.003}
\newcommand{\GKTconfigsensci}{[$-0.004$, $+0.011$]}% overwritten by macros file if present
""",
        False,
    ),
    # Abstract: replace S21--S22 epoch-extended claim block
    (
        r"""released 10-epoch training budget (Table~S15), GKT trails \textit{simpleKT} by
${\approx}0.041$ AUC (paired-$t$ 95\% CI \GKTdeltaci{}; Table~S16). A
GKT \emph{epoch-extended} ablation (30~epochs, batch~32; Table~S21--S22;
\textit{simpleKT} reference unchanged at 10~epochs, batch~64) recovers
${\approx}\GKTepochgain{}$ AUC on seed~$42$ but leaves pooled mean
$\Delta{\approx}\GKTthirtydeltavec{}$ (95\% CI \GKTthirtydeltaci{} over
nine folds across split seeds $17$, $42$, and $1234$): the GKT
under-performer ordering on XES3G5M persists under this partially matched
ablation.
""",
        r"""primary training budgets (Table~S15: GKT maximum 10~epochs, batch~4;
\textit{simpleKT} maximum 30~epochs, batch~64), GKT trails \textit{simpleKT} by
${\approx}0.041$ AUC (paired-$t$ 95\% CI \GKTdeltaci{}; Table~S16). A
targeted three-fold configuration-sensitivity check yielded a
small mean AUC increase of approximately $0.003$, with uncertainty
including zero (Table~S21).
""",
        False,
    ),
    # Abstract: unmoved -> quantitative
    (
        r"""(GKT ${\approx}{+}0.05$, GIKT ${\approx}{+}0.03$) while a sequence-only
baseline is unmoved.""",
        r"""(GKT ${\approx}{+}0.05$, GIKT ${\approx}{+}0.03$) while
\textit{simpleKT} changed only modestly, by ${+}0.008$ AUC, under the
specified injection setting.""",
        False,
    ),
    # Intro primary trio + S21--S22
    (
        r"""\GKTdeltaci{} in Table~S16; Tables~S21--S22 report GKT epoch-extended training
(${\approx}0.837$ on seed~$42$; pooled $\Delta{\approx}\GKTthirtydeltavec{}$,
95\% CI \GKTthirtydeltaci{}; \textit{simpleKT} reference held at 10~epochs),
and native GIKT (${\approx}0.878$). The gap is
\emph{observational} under fixed epoch caps (30 for sequence checkpoints
vs.\ 10 for graph backbones; Table~S15), not a causal attribution of graph
failure on XES3G5M under this protocol.""",
        r"""\GKTdeltaci{} in Table~S16; Table~S21 reports an exploratory seed-42
three-fold extended-training configuration-sensitivity check for GKT),
and native GIKT (${\approx}0.878$). The gap is
\emph{observational} under fixed maximum epoch caps (30 for sequence checkpoints
vs.\ 10 for graph backbones; Table~S15), not a causal attribution of graph
failure on XES3G5M under this protocol.""",
        False,
    ),
    # C2 DDR scopes
    (
        r"""manipulation check (GKT on XES3G5M, Pearson $r{\approx}0.93$--$0.99$; \texttt{prereq\_preserve}
  costs the least AUC at matched budget), while remaining a purely structural
  audit on graph-inert backbones (DGEKT, and GKT on ASSISTments), where total
  graph destruction moves AUC by ${\le}0.003$ (Section~\ref{sec:exp-ddr-downstream}).""",
        r"""manipulation check (GKT on XES3G5M: Pearson $r{\approx}0.93$ on the
  $p{\le}0.3$ core, $n{=}81$; $r{\approx}0.99$ with anchors, $n{=}99$;
  Spearman $\rho{\approx}0.93$ on the same full pool;
  \texttt{prereq\_preserve}
  costs the least AUC at matched budget), while remaining a purely structural
  audit on graph-inert backbones (DGEKT, and GKT on ASSISTments), where total
  graph destruction moves AUC by ${\le}0.003$ (Section~\ref{sec:exp-ddr-downstream}).""",
        False,
    ),
    # C5
    (
        r"""the released 10-epoch budget, while GIKT remains competitive. A
  GKT epoch-extended rerun (30~epochs, batch~32; Table~S21--S22; reference
  \textit{simpleKT} at 10~epochs, batch~64) recovers
  ${\approx}\GKTepochgain{}$ mean AUC on seed~$42$ but leaves pooled
  $\Delta{\approx}\GKTthirtydeltavec{}$ (95\% CI \GKTthirtydeltaci{};
  nine folds, seeds $17/42/1234$): the trio ordering on XES3G5M is
  \emph{partially epoch-sensitive} yet invariant in direction (GKT trails).
  Train-only versus full-log
  ablation ($|\Delta\text{AUC}|{\leq}0.003$ on the three public benchmarks)
  bounds how much graph provenance alone moves headline metrics here, so C5 is""",
        r"""the primary GKT maximum-10-epoch budget (batch~4), while GIKT remains competitive. A
  targeted seed-42 three-fold extended-training check (Table~S21; maximum 30~epochs,
  batch~16) showed a mean AUC increase of $0.003451$ over primary GKT, with an
  approximate 95\% CI including zero; because both maximum epochs and batch size
  changed, this is configuration sensitivity rather than an isolated epoch effect.
  The trio ordering on XES3G5M remains invariant in direction (GKT trails).
  Train-only versus full-log
  ablation ($|\Delta\text{AUC}|{\leq}0.003$ and $|\Delta\text{ACC}|{\leq}0.008$
  on the three public benchmarks)
  bounds how much graph provenance alone moves headline metrics here, so C5 is""",
        False,
    ),
    # Distill paragraph S21--S22
    (
        r"""primary XES3G5M trio under audit, with Tables~S21--S22 isolating the epoch-budget
confound across three split seeds with fold-aligned graph rebuilds.""",
        r"""primary XES3G5M trio under audit, with Table~S21 reporting an exploratory
seed-42 three-fold extended-training configuration-sensitivity check.""",
        False,
    ),
    # F-R03 AUC/ACC
    (
        r"""versus full-log ablation moves headline metrics by at most $0.003$ AUC/ACC.""",
        r"""versus full-log ablation moves headline metrics by at most $0.003$ AUC
and $0.008$ ACC.""",
        False,
    ),
    # Baseline diagnostic epoch block
    (
        r"""(95\% CI \GKTdeltaci{}; Table~S16). A GKT epoch-extended ablation (30~epochs,
batch~32; \textit{simpleKT} reference at 10~epochs, batch~64) narrows the gap to
$\Delta{\approx}\GKTthirtydeltavec{}$ (95\% CI \GKTthirtydeltaci{};
Tables~S21--S22): per split seed, mean $\Delta(\text{GKT}-\textit{simpleKT})$
is ${\approx}{-}0.034$ (seed~$17$), ${\approx}{-}0.040$ (seed~$42$), and
${\approx}{-}0.041$ (seed~$1234$). GIKT slightly exceeds the sequence leader""",
        r"""(95\% CI \GKTdeltaci{}; Table~S16). In a targeted exploratory check on
experiment seed~$42$ and three folds (Table~S21), the extended-training GKT
configuration (maximum 30~epochs, batch~16) showed a mean AUC increase of
$0.003451$ over the primary GKT configuration (maximum 10~epochs, batch~4);
the approximate 95\% CI included zero, and because both maximum epochs and batch
size changed, the comparison does not isolate an epoch-only effect. GIKT slightly exceeds the sequence leader""",
        False,
    ),
    # Training parity paragraph
    (
        r"""$\texttt{max\_seq\_len}{=}200$, batch~64, 30~epochs). GKT is evaluated
through the \texttt{pyKT} graph branch (batch~16, 10~epochs under the
released budget; consumes exported $\Epre/\Esim$). Native GIKT
(\path{src/models/gikt.py}) uses $\texttt{emb\_size}{=}64$,
$\texttt{hidden\_dim}{=}128$, the same $\texttt{lr}$, batch~16, and
10~epochs. We do not claim bit-identical engineering parity across codebases;
we align processed splits, data loaders, evaluation hooks, and early stopping
(patience~5, best validation AUC). A one-step label-index misalignment in an
early GIKT head was caught by fold-wise AUC inconsistency and corrected before
Table~\ref{tab:baseline-cv} (Section~\ref{sec:threats-validity}). No family
receives a hyperparameter search. Epoch caps differ in the primary release:
sequence checkpoints train up to 30~epochs (batch~64) while graph backbones
use 10-epoch budgets with smaller batches (Table~S15), reflecting higher
per-epoch cost. Tables~S21--S22 report \emph{GKT-only} epoch extensions with
fold-aligned graph rebuilds per split seed ($17$, $42$, $1234$), pairing
against \textit{simpleKT} from Phase~3 trio reruns (10~epochs, batch~64): on
seed~$42$, mean GKT AUC rises from $0.834$ to $0.837$
(${\approx}\GKTepochgain{}$), narrowing the gap from ${\approx}{-}0.041$ to
$\Delta{\approx}{-}0.038$ (seed~$42$ CI \GKTthirtyseedFortydeltaci{}).
Pooled over nine folds, $\Delta{\approx}\GKTthirtydeltavec{}$ (95\% CI
\GKTthirtydeltaci{}). This ablation isolates the GKT epoch confound; it is
\emph{not} full compute parity (batch and reference-epoch asymmetry remain).
The residual deficit remains an \emph{observational} benchmarking boundary on
XES3G5M under this protocol, not a causal claim that graph structure is
uninformative.""",
        r"""$\texttt{max\_seq\_len}{=}200$, batch~64, maximum 30~epochs). GKT is evaluated
through the \texttt{pyKT} graph branch (batch~4, maximum 10~epochs under the
primary attested budget; consumes exported $\Epre/\Esim$). Native GIKT
(\path{src/models/gikt.py}) uses $\texttt{emb\_size}{=}64$,
$\texttt{hidden\_dim}{=}128$, the same $\texttt{lr}$, batch~16, and
maximum 10~epochs. We do not claim bit-identical engineering parity across codebases;
we align processed splits, data loaders, evaluation hooks, and early stopping
(patience~5, best validation AUC). A one-step label-index misalignment in an
early GIKT head was caught by fold-wise AUC inconsistency and corrected before
Table~\ref{tab:baseline-cv} (Section~\ref{sec:threats-validity}). No family
receives a hyperparameter search. Maximum epoch caps differ in the primary release:
sequence checkpoints train up to a maximum of 30~epochs (batch~64) while graph backbones
use maximum 10-epoch budgets with smaller batches (Table~S15), reflecting higher
per-epoch cost. Table~S21 reports a targeted seed-42 three-fold
extended-training configuration-sensitivity check for GKT (maximum 30~epochs,
batch~16 versus primary maximum 10~epochs, batch~4): mean AUC increased by
$0.003451$, but the approximate 95\% CI $[-0.004,+0.011]$ included zero.
Because both the maximum epoch budget and batch size changed, this exploratory
comparison does not isolate the effect of epochs and is not a fully
compute-matched comparison.
The residual deficit remains an \emph{observational} benchmarking boundary on
XES3G5M under this protocol, not a causal claim that graph structure is
uninformative.""",
        False,
    ),
    # Discussion model-specific
    (
        r"""\GKTdeltaci{}, Table~S16; fold stds in Table~\ref{tab:baseline-cv}). A
GKT epoch-extended rerun on split seed~$42$ reaches $0.837$ AUC but still
trails by pooled $\Delta{\approx}\GKTthirtydeltavec{}$ (95\% CI \GKTthirtydeltaci{};
Tables~S21--S22; seed-level $\Delta$ stable at ${\approx}{-}0.034$ to
${\approx}{-}0.041$). GIKT ($0.878$) slightly \emph{exceeds}""",
        r"""\GKTdeltaci{}, Table~S16; fold stds in Table~\ref{tab:baseline-cv}). In a
targeted seed-42 three-fold check (Table~S21), extended-training GKT reached
mean AUC ${\approx}0.837$ (${+}0.003451$ vs.\ primary GKT; CI including zero);
this exploratory configuration-sensitivity result does not isolate epochs from
batch-size change. GIKT ($0.878$) slightly \emph{exceeds}""",
        False,
    ),
    # Caveats
    (
        r"""Table~S15); Tables~S21--S22 show GKT-only epoch extension recovers only
${\approx}\GKTepochgain{}$ AUC of the GKT deficit on seed~$42$, with pooled
nine-fold $\Delta{\approx}\GKTthirtydeltavec{}$ under partially matched caps.
The GKT--\textit{simpleKT} gap on XES3G5M remains \emph{observational} under
fair budgets, not proof that graph signal is useless after exhaustive tuning.""",
        r"""Table~S15). Table~S21 reports an exploratory seed-42 three-fold
extended-training configuration-sensitivity check (mean $\Delta$AUC ${+}0.003451$;
CI including zero) in which both maximum epochs and batch size changed relative
to primary GKT.
The GKT--\textit{simpleKT} gap on XES3G5M remains \emph{observational} under
attested budgets, not proof that graph signal is useless after exhaustive tuning.""",
        False,
    ),
    # Deployment vignettes
    (
        r"""These vignettes complement---rather than replace---backbone comparisons: C5
reports model-specific trio ordering on XES3G5M under fixed budgets, with
Table~S21--S22 showing that GKT epoch extension recovers only ${\approx}\GKTepochgain{}$ AUC
of the GKT deficit on seed~$42$ (pooled $\Delta{\approx}\GKTthirtydeltavec{}$ under
partially matched caps).""",
        r"""These vignettes complement---rather than replace---backbone comparisons: C5
reports model-specific trio ordering on XES3G5M under fixed budgets, with
Table~S21 reporting exploratory configuration sensitivity rather than a
compute-matched epoch-only ablation.""",
        False,
    ),
    # Limitations paragraph (replace S21--S22 epoch claims + add compute note)
    (
        r"""The GKT--\textit{simpleKT}
gap is \emph{observational} under fixed epoch budgets (30 vs.\ 10; Table~S15);
Table~S21--S22 shows the deficit shrinks only slightly (${\approx}\GKTepochgain{}$ AUC
on seed~$42$; pooled $\Delta{\approx}\GKTthirtydeltavec{}$) when GKT is trained
with extended epoch caps, so it is not fully explained by the released 10-vs-30
epoch asymmetry alone.
Tables~S21--S22 pair GKT epoch-extended runs (30~epochs, batch~32) against
\textit{simpleKT} from Phase~3 trio reruns (10~epochs, batch~64), so training
caps remain only partially matched; a 30-epoch \textit{simpleKT} reference on
the same nine folds is required before stronger matched-budget claims.
Multi-seed GKT replication requires
sequential fold-aligned graph rebuilds per split seed because default processed
exports omit a seed suffix in the path layout. Native SKT/DyGKT runs
are wiring diagnostics, not tuned-backbone benchmarks. Controlled injection
(Section~\ref{sec:exp-injection}, Tables~S17--S18) demonstrates metric-level
sensitivity. ASSISTments yields no $\Esim$ under item-overlap Jaccard; GT
cross-validation is Junyi-only at $\theta{=}0.5$; pyKT GKT on Junyi Academy
is omitted because dense multi-million interaction graphs make the stock GKT
wrapper impractical under our compute budget (Tables~S1, \ref{tab:baseline-summary});
downstream \DDR{} retraining covers DGEKT and GKT (the latter with a
manipulation-check anchor), with GKT/XES3G5M reported across three seeds
($\{42,17,1234\}$, nine folds).""",
        r"""The GKT--\textit{simpleKT}
gap is \emph{observational} under attested maximum epoch budgets (30 vs.\ 10; Table~S15).
Due to the substantially greater computational cost of GKT, the
primary GKT configuration used a maximum of 10 epochs, whereas
\textit{simpleKT} used a maximum of 30 epochs. A targeted seed-42
three-fold check evaluated an extended GKT configuration with a
maximum of 30 epochs; however, its batch size also differed from
the primary configuration (4 vs.\ 16). Therefore, the observed ${+}0.003451$ mean
AUC change should be interpreted as exploratory configuration
sensitivity rather than an isolated epoch effect. The study does
not provide a fully compute-matched comparison.
Native SKT/DyGKT runs
are wiring diagnostics, not tuned-backbone benchmarks. Controlled injection
(Section~\ref{sec:exp-injection}, Tables~S17--S18) demonstrates metric-level
sensitivity. ASSISTments yields no $\Esim$ under item-overlap Jaccard; GT
cross-validation is Junyi-only at $\theta{=}0.5$; pyKT GKT on Junyi Academy
is omitted because dense multi-million interaction graphs make the stock GKT
wrapper impractical under our compute budget (Tables~S1, \ref{tab:baseline-summary});
downstream \DDR{} retraining covers DGEKT and GKT (the latter with a
manipulation-check anchor), with GKT/XES3G5M reported across three seeds
($\{42,17,1234\}$, nine folds).""",
        False,
    ),
    # Future work S21--S22
    (
        r"""transfer across encoders. The three-seed GKT replication in Tables~S21--S22
establishes a reproducible multi-seed template; extending it to additional
corpora and to full compute parity (including a 30-epoch \textit{simpleKT}
reference at batch~64 on the same folds) remains open.""",
        r"""transfer across encoders. Establishing a fully compute-matched
GKT vs.\ \textit{simpleKT} comparison (matched maximum epochs and batch size
on the same folds) remains open.""",
        False,
    ),
    # Conclusion
    (
        r"""remains competitive; GKT epoch-extended training (Tables~S21--S22;
\textit{simpleKT} reference unchanged) recovers only
${\approx}\GKTepochgain{}$ AUC on seed~$42$, leaving pooled
$\Delta{\approx}\GKTthirtydeltavec{}$ (95\% CI \GKTthirtydeltaci{}). Train-only versus
full-log ablation moves headline AUC by at most $0.003$. These results cohere""",
        r"""remains competitive. A targeted three-fold configuration-sensitivity check
(Table~S21) yielded a small mean AUC increase of approximately $0.003$, with
uncertainty including zero. Train-only versus
full-log ablation moves headline AUC by at most $0.003$ and ACC by at most
$0.008$. These results cohere""",
        False,
    ),
    # Appendix index
    (
        r"""S21: GKT epoch-extended ablation, seed~$42$ (Section~\ref{sec:supp-gkt-epoch});
S22: multi-seed GKT 30ep replication (Section~\ref{sec:supp-gkt-multiseed}).""",
        r"""S21: targeted three-fold extended-training configuration-sensitivity check,
seed~$42$ (Section~\ref{sec:supp-gkt-epoch}).""",
        False,
    ),
    # Fig S3 caption
    (
        r"""\caption{Supplementary Figure~S3. Downstream DGEKT sensitivity to prerequisite-graph disruption on ASSISTments~2012 and XES3G5M. Each point is one fold/operator/strength run; the vertical axis is AUC drop relative to the unperturbed train-only graph.}""",
        r"""\caption{Supplementary Figure~S3. Downstream graph-KT sensitivity to prerequisite-graph disruption on ASSISTments~2012 and XES3G5M (DGEKT and GKT cells). Each point is one fold/operator/strength run; the vertical axis is AUC drop relative to the unperturbed train-only graph. The burned-in annotation $r{\approx}0.75$ is the \emph{global pooled} Pearson correlation across both datasets and both models ($n{=}186$), not the XES3G5M/GKT-only correlation ($r{\approx}0.99$ with anchors, $n{=}99$; $r{\approx}0.93$ on the $p{\le}0.3$ core, $n{=}81$).}""",
        False,
    ),
    # Training parity supp prose
    (
        r"""across families (30 epochs for sequence checkpoints vs.\ 10 for graph
backbones in the primary release), reflecting per-epoch cost. Tables~S21--S22
report GKT epoch-extended ablations (30~epochs, batch~32; \textit{simpleKT}
reference at 10~epochs, batch~64) with fold-aligned graph rebuilds per split
seed ($17$, $42$, $1234$). ``Native'' denotes""",
        r"""across families (maximum 30 epochs for sequence checkpoints vs.\ maximum 10 for graph
backbones in the primary release; primary GKT batch~4, \textit{simpleKT} batch~64),
reflecting per-epoch cost. Table~S21 reports a targeted seed-42 three-fold
extended-training configuration-sensitivity check (maximum 30~epochs, batch~16).
``Native'' denotes""",
        False,
    ),
    # S16 prose about S21--S22
    (
        r"""does not hinge on fragile three-fold $t$-tests. Tables~S21--S22 show GKT
epoch extension recovers only ${\approx}+0.003$ mean AUC on seed~$42$, leaving pooled
$\Delta{\approx}-0.038$ (95\% CI $[-0.041,-0.035]$ over nine folds). Reproducers may optionally run""",
        r"""does not hinge on fragile three-fold $t$-tests. Table~S21 reports an exploratory
seed-42 three-fold configuration-sensitivity check (mean $\Delta$AUC ${+}0.003451$;
approximate 95\% CI including zero). Reproducers may optionally run""",
        False,
    ),
    # Replace entire S21 + S22 sections
    (
        r"""\section{GKT epoch-extended ablation}
\label{sec:supp-gkt-epoch}
Table~S21 (Table~\ref{tab:gkt-epoch-ablation}) compares the released GKT
configuration (10~epochs, batch~16) with a GKT-only epoch extension on split
seed~$42$ (\path{configs/xes3g5m_gkt_epochs30.yaml}; 30~epochs, batch~32 under
our 16--24\,GB GPU budget; \textit{simpleKT} reference unchanged) on XES3G5M
under train-only graphs. Fold-level
$\Delta$AUC intervals use paired-$t$ over three learner-disjoint folds,
matching Table~S16.
\begin{table}[h!]
\centering
\caption{GKT epoch-extended ablation on XES3G5M, split seed~$42$ (Table S21)}
\label{tab:gkt-epoch-ablation}
\input{results/tables/gkt_epoch_ablation.tex}
\end{table}

\section{Multi-seed GKT replication}
\label{sec:supp-gkt-multiseed}
Table~S22 (Table~\ref{tab:gkt-multiseed}) replicates GKT epoch-extended training
at split base seeds $17$, $42$, and $1234$. Each run rebuilds fold-specific
train-only graph exports before training (see \path{configs/xes3g5m_split17.yaml} and siblings).
$\Delta$AUC pairs GKT against \textit{simpleKT} from the matched Phase~3 trio
runs at the same seed (GKT: 30~epochs, batch~32; \textit{simpleKT}: 10~epochs,
batch~64). Pooled nine-fold summary: Table~\ref{tab:gkt-pooled}.
\begin{table}[h!]
\centering
\caption{GKT epoch-extended vs.\ \textit{simpleKT} by split seed (Table S22)}
\label{tab:gkt-multiseed}
\input{results/tables/q1_gkt_epochs30_ablation_tabular.tex}
\end{table}
\begin{table}[h!]
\centering
\caption{Pooled nine-fold $\Delta$AUC summary (Table S22, continued)}
\label{tab:gkt-pooled}
\input{results/tables/gkt_epoch_ablation_pooled.tex}
\end{table}
""",
        r"""\section{Targeted three-fold extended-training configuration sensitivity}
\label{sec:supp-gkt-epoch}
Table~S21 (Table~\ref{tab:gkt-epoch-ablation}) reports a targeted three-fold
extended-training configuration-sensitivity check on XES3G5M using experiment
seed~$42$ and folds $0$--$2$. Primary GKT artefacts use a maximum of 10~epochs
and batch size~4; the extended-training configuration uses a maximum of
30~epochs and batch size~16. Fold AUCs are unchanged historical artefacts;
legacy unpaired GKT30 artefacts at seeds~$17$ and~$1234$ are excluded from
submission. This check is exploratory and does not isolate the effect of epochs.
\begin{table}[h!]
\centering
\caption{Targeted three-fold extended-training configuration sensitivity
check on XES3G5M using experiment seed~$42$. The primary GKT
configuration used a maximum of 10 epochs and batch size~4,
whereas the extended-training configuration used a maximum of
30 epochs and batch size~16. Mean AUC increased by $0.003451$;
however, the approximate 95\% confidence interval
$[-0.004, 0.011]$ included zero. Because both maximum epochs and
batch size changed, this exploratory comparison does not isolate
the effect of epochs.}
\label{tab:gkt-epoch-ablation}
\input{results/tables/gkt_epoch_ablation.tex}
\end{table}
""",
        False,
    ),
    # Closing appendix S21--S22 mention
    (
        r"""on injected graphs. Tables~S21--S22 report the GKT epoch-extended ablation
(seed~$42$ and multi-seed replication). Tables~S19--S20 report ANOVA summaries
for baselines and the GKT multi-seed \DDR{}$\to$downstream sweep
(Section~\ref{sec:supp-anova} in the Appendix).""",
        r"""on injected graphs. Table~S21 reports the targeted seed-42 three-fold
extended-training configuration-sensitivity check.
Tables~S19--S20 report ANOVA summaries
for baselines and the GKT multi-seed \DDR{}$\to$downstream sweep
(Section~\ref{sec:supp-anova} in the Appendix).""",
        False,
    ),
    # Abstract DDR: clarify n for 0.93/0.99 (keep short)
    (
        r"""(Pearson $r{\approx}0.93$ on the $p{\le}0.3$ core, $r{\approx}0.99$ with
manipulation-check anchors)""",
        r"""(Pearson $r{\approx}0.93$ on the $p{\le}0.3$ core, $n{=}81$; $r{\approx}0.99$ with
manipulation-check anchors, $n{=}99$)""",
        False,
    ),
    # Conclusion DDR r
    (
        r"""backbone that passes a manipulation check (GKT on XES3G5M; three seeds) \DDR{} predicts AUC
loss ($r{\approx}0.93$--$0.99$) and \texttt{prereq\_preserve} costs the least accuracy at""",
        r"""backbone that passes a manipulation check (GKT on XES3G5M; three seeds) \DDR{} predicts AUC
loss (Pearson $r{\approx}0.93$ on $p{\le}0.3$, $n{=}81$; $r{\approx}0.99$ with anchors, $n{=}99$)
and \texttt{prereq\_preserve} costs the least accuracy at""",
        False,
    ),
    # Decision table unmoved (manipulation check row - different meaning; keep "AUC unmoved" for inert backbone is OK? User said replace "simpleKT is unmoved". This row is about manipulation check for graph-inert - "AUC unmoved under near-total graph destruction" is about the backbone being inert, not simpleKT. Keep it.
]


def main() -> None:
    text = TEX.read_text(encoding="utf-8")
    missing = []
    for old, new, all_occ in PATCHES:
        n = text.count(old)
        if n == 0:
            missing.append(old[:120].replace("\n", " "))
            continue
        if all_occ:
            text = text.replace(old, new)
        else:
            text = text.replace(old, new, 1)
    TEX.write_text(text, encoding="utf-8")
    # Residual forbidden phrases
    bad = [
        "Tables~S21--S22",
        "Table~S21--S22",
        "epoch-matched",
        "compute-matched",
        "nine-fold",
        "batch~32",
        "GKTthirtydeltavec",
        "baseline is unmoved",
        "0.003$ AUC/ACC",
        "0.003 AUC/ACC",
        "simpleKT} reference unchanged at 10",
        "simpleKT} at 10~epochs",
        "reference held at 10~epochs",
        "batch~16, 10~epochs under the\nreleased",
    ]
    print("=== missing patches ===")
    for m in missing:
        print("MISSING:", m)
    print(f"missing_count={len(missing)}")
    print("=== residual checks ===")
    for b in bad:
        c = text.count(b)
        if c:
            # GKTthirty may remain in macro defs as ?? — report
            print(f"HIT {c}: {b!r}")
    print("done")


if __name__ == "__main__":
    main()
