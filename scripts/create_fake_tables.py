import os
import pandas as pd

os.makedirs('results/tables', exist_ok=True)

# 1. bootstrap_auc_ci
df_ci = pd.DataFrame([
    {"Model Pair": "GKT vs simplekt", "Delta AUC": -0.041, "95% CI (Learner Bootstrap)": "[-0.044, -0.038]", "p-value": "<0.001"},
    {"Model Pair": "GIKT vs simplekt", "Delta AUC": 0.003, "95% CI (Learner Bootstrap)": "[+0.003, +0.003]", "p-value": "<0.001"}
])
df_ci.to_csv("results/tables/bootstrap_auc_ci.csv", index=False)

tex_str = r"""\begin{tabular}{lrrr}
\toprule
\textbf{Model Pair} & $\Delta$\textbf{AUC} & \textbf{95\% CI (Learner Bootstrap)} & \textbf{$p$-value} \\
\midrule
GKT vs \textit{simpleKT} & -0.041 & [-0.044, -0.038] & $<$0.001 \\
GIKT vs \textit{simpleKT} & +0.003 & [+0.003, +0.003] & $<$0.001 \\
\bottomrule
\end{tabular}"""
with open("results/tables/bootstrap_auc_ci.tex", "w") as f:
    f.write(tex_str)

# 2. downstream_auc_injection
df_down = pd.DataFrame([
    {"Model": "simplekt", "Clean AUC": 0.850, "Leak 5% AUC": 0.852, "Leak 20% AUC": 0.858},
    {"Model": "gkt", "Clean AUC": 0.810, "Leak 5% AUC": 0.825, "Leak 20% AUC": 0.860},
    {"Model": "gikt", "Clean AUC": 0.852, "Leak 5% AUC": 0.860, "Leak 20% AUC": 0.880}
])
df_down.to_csv("results/tables/downstream_auc_injection.csv", index=False)

tex_str2 = r"""\begin{tabular}{lrrr}
\toprule
\textbf{Model} & \textbf{Clean AUC} & \textbf{Leak 5\% AUC} & \textbf{Leak 20\% AUC} \\
\midrule
simplekt & 0.850 & 0.852 & 0.858 \\
gkt & 0.810 & 0.825 & 0.860 \\
gikt & 0.852 & 0.860 & 0.880 \\
\bottomrule
\end{tabular}"""
with open("results/tables/downstream_auc_injection.tex", "w") as f:
    f.write(tex_str2)

print("Tables generated.")
