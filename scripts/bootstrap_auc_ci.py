import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def synthesize_table():
    """Fold-level paired Delta-AUC with t-distribution 95% CI (n=3 folds, descriptive).

    NOTE: this is NOT a learner-level bootstrap; it summarises the three
    learner-disjoint CV folds with a paired t interval. The manuscript must
    describe it as such.
    """
    df = pd.read_csv("results/tables/baseline_fold_results.csv")
    df = df[(df["dataset"] == "xes3g5m") & (df["graph_construction"] == "train_only")]

    def get_aucs(model_name):
        return df[df["model"] == model_name].sort_values("fold")["auc"].values

    aucs_simplekt = get_aucs("simplekt")
    pretty = {"gkt": "GKT", "gikt": "GIKT"}

    rows = []
    t_val = stats.t.ppf(0.975, df=2)

    for model in ("gkt", "gikt"):
        aucs = get_aucs(model)
        if len(aucs) != 3 or len(aucs_simplekt) != 3:
            continue
        diff = aucs - aucs_simplekt
        mean_diff = np.mean(diff)
        se = np.std(diff, ddof=1) / np.sqrt(3)
        margin = t_val * se
        _, p_val = stats.ttest_rel(aucs, aucs_simplekt)
        p_str = "$<$0.001" if p_val < 0.001 else f"{p_val:.3f}"
        rows.append({
            "Model Pair": f"{pretty[model]} vs \\textit{{simpleKT}}",
            "$\\Delta$AUC": f"{mean_diff:+.3f}",
            "95\\% CI": f"[{mean_diff - margin:+.3f}, {mean_diff + margin:+.3f}]",
            "$p$-value": p_str,
        })

    out_df = pd.DataFrame(rows)

    tex_str = out_df.to_latex(index=False, escape=False, column_format="lrrr", header=False)
    tex_str = tex_str.replace("\\toprule", "\\toprule\n\\textbf{Model Pair} & $\\Delta$\\textbf{AUC} & \\textbf{95\\% CI (paired $t$)} & \\textbf{$p$-value} \\\\")
    
    Path("results/tables").mkdir(parents=True, exist_ok=True)
    with open("results/tables/bootstrap_auc_ci.tex", "w") as f:
        f.write(tex_str)

if __name__ == "__main__":
    synthesize_table()
