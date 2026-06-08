from pathlib import Path

import pandas as pd


def _fmt_auc(value: float) -> str:
    return f"{value:.3f}" if not pd.isna(value) else "-"


def _fmt_delta(value: float) -> str:
    if pd.isna(value):
        return "-"
    return f"{value:+.3f}"


def main():
    csv_path = Path("results/tables/cold_start_metrics.csv")
    if not csv_path.exists():
        print("CSV not found.")
        return

    df = pd.read_csv(csv_path)
    
    # We want to compare AUC across strata
    # Models to compare: No-Graph (dkt, simplekt) vs Graph (gkt, gikt, dgekt)
    models_to_include = ['dkt', 'simplekt', 'gkt', 'gikt', 'dgekt']
    df = df[df['model'].isin(models_to_include)]
    
    # Order strata
    strata_order = ['very_cold', 'cold', 'warm', 'hot']
    df = df[df['stratum'].isin(strata_order)]
    
    # Average across folds/seeds
    agg_df = df.groupby(['dataset', 'model', 'stratum'])['auc'].mean().reset_index()
    
    # Pivot to get models as columns and strata as rows
    pivot_df = agg_df.pivot(index=['dataset', 'stratum'], columns='model', values='auc')
    
    # Reorder columns
    pivot_df = pivot_df[['dkt', 'simplekt', 'gkt', 'gikt', 'dgekt']]
    
    # Reorder index to follow strata_order
    # First, make dataset categorical so we preserve its order (assist2012, junyi, synthetic_c2, synthetic_c5, xes3g5m)
    # Then make stratum categorical
    datasets = ['assist2012', 'junyi', 'synthetic_c2', 'synthetic_c5', 'xes3g5m']
    pivot_df.reset_index(inplace=True)
    pivot_df['dataset'] = pd.Categorical(pivot_df['dataset'], categories=datasets, ordered=True)
    pivot_df['stratum'] = pd.Categorical(pivot_df['stratum'], categories=strata_order, ordered=True)
    pivot_df.sort_values(['dataset', 'stratum'], inplace=True)
    
    no_graph_cols = ['dkt', 'simplekt']
    graph_cols = ['gkt', 'gikt', 'dgekt']
    pivot_df['best_no_graph'] = pivot_df[no_graph_cols].max(axis=1)
    pivot_df['best_graph'] = pivot_df[graph_cols].max(axis=1)
    pivot_df['delta_best'] = pivot_df['best_graph'] - pivot_df['best_no_graph']

    # Generate TeX
    tex_out = Path("results/tables/cold_start_comparison.tex")
    
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Cold-start comparison of sequence-only (No-Graph) and graph-aware (Graph) KT models. "
        "Entries are three-fold mean AUC by KC train-frequency stratum; $\\Delta_{\\max}$ is the best Graph AUC "
        "minus the best No-Graph AUC in the same dataset/stratum.}",
        "\\label{tab:cold-start-comparison}",
        "\\footnotesize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabularx}{\\linewidth}{@{} >{\\RaggedRight\\arraybackslash}p{0.14\\linewidth} "
        ">{\\RaggedRight\\arraybackslash}p{0.11\\linewidth} *{6}{>{\\centering\\arraybackslash}X} @{}}",
        "\\toprule",
        "& & \\multicolumn{2}{c|}{\\textbf{No-Graph}} & \\multicolumn{4}{c}{\\textbf{Graph}} \\\\",
        "\\cmidrule(lr){3-4} \\cmidrule(l){5-8}",
        "Dataset & Stratum & DKT & SimpleKT & GKT & GIKT & DGEKT & $\\Delta_{\\max}$ \\\\",
        "\\midrule"
    ]
    
    current_ds = None
    for _, row in pivot_df.iterrows():
        ds = row['dataset']
        if pd.isna(ds): continue
        
        stratum = row['stratum']
        
        ds_name = ds.replace('_', '\\_') if ds != current_ds else ""
        if ds != current_ds and current_ds != None:
            lines.append("\\midrule")
            
        current_ds = ds
        
        # format stratum safely
        stratum_str = str(stratum).replace('_', '\\_')
        
        dkt = _fmt_auc(row['dkt'])
        simplekt = _fmt_auc(row['simplekt'])
        gkt = _fmt_auc(row['gkt'])
        gikt = _fmt_auc(row['gikt'])
        dgekt = _fmt_auc(row['dgekt'])
        delta = _fmt_delta(row['delta_best'])
        
        lines.append(f"{ds_name} & {stratum_str} & {dkt} & {simplekt} & {gkt} & {gikt} & {dgekt} & {delta} \\\\")
        
    lines.extend([
        "\\bottomrule",
        "\\end{tabularx}",
        "\\end{table}"
    ])
    
    tex_out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {tex_out}")

if __name__ == "__main__":
    main()
