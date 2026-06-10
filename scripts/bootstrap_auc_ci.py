import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def synthesize_table():
    df = pd.read_csv("results/tables/baseline_fold_results.csv")
    df = df[(df["dataset"] == "xes3g5m") & (df["graph_construction"] == "train_only")]
    
    def get_aucs(model_name):
        res = df[df["model"] == model_name].sort_values("fold")["auc"].values
        return res
        
    aucs_simplekt = get_aucs("simplekt")
    aucs_gkt = get_aucs("gkt")
    aucs_gikt = get_aucs("gikt")
    
    rows = []
    
    t_val = stats.t.ppf(0.975, df=2)
    
    if len(aucs_simplekt) == 3 and len(aucs_gkt) == 3:
        diff_gkt = aucs_gkt - aucs_simplekt
        mean_diff = np.mean(diff_gkt)
        se = np.std(diff_gkt, ddof=1) / np.sqrt(3)
        margin = t_val * se
        ci_lower = mean_diff - margin
        ci_upper = mean_diff + margin
        _, p_val = stats.ttest_rel(aucs_gkt, aucs_simplekt)
        rows.append({
            "Model Pair": "gkt vs simplekt",
            "$\\Delta$AUC": f"{mean_diff:+.3f}",
            "95\\% CI": f"[{ci_lower:+.3f}, {ci_upper:+.3f}]",
            "$p$-value": f"{p_val:.3f}"
        })
        
    if len(aucs_simplekt) == 3 and len(aucs_gikt) == 3:
        diff_gikt = aucs_gikt - aucs_simplekt
        mean_diff = np.mean(diff_gikt)
        se = np.std(diff_gikt, ddof=1) / np.sqrt(3)
        margin = t_val * se
        ci_lower = mean_diff - margin
        ci_upper = mean_diff + margin
        _, p_val = stats.ttest_rel(aucs_gikt, aucs_simplekt)
        rows.append({
            "Model Pair": "gikt vs simplekt",
            "$\\Delta$AUC": f"{mean_diff:+.3f}",
            "95\\% CI": f"[{ci_lower:+.3f}, {ci_upper:+.3f}]",
            "$p$-value": f"{p_val:.3f}"
        })
        
    out_df = pd.DataFrame(rows)
    
    tex_str = out_df.to_latex(index=False, escape=False, column_format="lrrr", header=False)
    tex_str = tex_str.replace("\\toprule", "\\toprule\n\\textbf{Model Pair} & $\\Delta$\\textbf{AUC} & \\textbf{95\\% CI} & \\textbf{$p$-value} \\\\")
    
    Path("results/tables").mkdir(parents=True, exist_ok=True)
    with open("results/tables/bootstrap_auc_ci.tex", "w") as f:
        f.write(tex_str)

if __name__ == "__main__":
    synthesize_table()
