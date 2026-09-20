$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$zip = Join-Path $root "EAAI_latex_source.zip"
$stage = Join-Path $root "_em_stage"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null

$names = @(
  "main_EAAI.tex",
  "main_EAAI.bbl",
  "refs_EAAI.bib",
  "elsarticle.cls",
  "elsarticle-num.bst",
  "graphical_abstract.pdf",
  "supplementary_EAAI.tex",
  "bootstrap_ci_macros.tex",
  "ddr_slope_macros.tex",
  "audit_cost.tex",
  "dataset_stats.tex",
  "leakage_metrics.tex",
  "dag_audit_summary.tex",
  "baseline_results.tex",
  "baseline_cv_template.tex",
  "graph_ablation.tex",
  "m4_qk_census.tex",
  "m4_phase_b_auc.tex",
  "leakage_exposure.tex",
  "leakage_exposure_full.tex",
  "noise_floor_macros.tex",
  "ddr_raw.tex",
  "ddr_downstream.tex",
  "ddr_downstream_gkt.tex",
  "cold_start_summary.tex",
  "gt_validation_table.tex",
  "baseline_results_full.tex",
  "graph_ablation_full.tex",
  "significance_tests_public.tex",
  "autocorrelation_stats.tex",
  "gt_validation_extended.tex",
  "cold_start_by_stratum.tex",
  "cold_start_comparison.tex",
  "training_parity.tex",
  "bootstrap_auc_ci.tex",
  "gkt_epoch_ablation.tex",
  "gkt_epoch_ablation_macros.tex",
  "leak_injection.tex",
  "downstream_auc_injection.tex",
  "anova_baseline.tex",
  "anova_ddr_downstream.tex",
  "fig_autocorr_vs_auc.pdf",
  "fig_pr_curve.pdf",
  "fig_cold_kc_ego_xes3g5m.pdf",
  "fig_learner_timeline_xes3g5m.pdf",
  "fig_ddr_downstream.pdf",
  "fig_kt_graph_junyi.pdf",
  "fig_kt_graph_assist2012.pdf",
  "fig_kt_graph_xes3g5m.pdf",
  "fig_ddr_junyi.pdf",
  "fig_ddr_assist2012.pdf",
  "fig_ddr_xes3g5m.pdf"
)

foreach ($n in $names) {
  $src = Join-Path $root $n
  if (-not (Test-Path $src)) { throw "Missing $n" }
  Copy-Item $src (Join-Path $stage $n)
}

if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zip -Force
Remove-Item $stage -Recurse -Force
Write-Host "Wrote $zip"
(Get-Item $zip).Length
