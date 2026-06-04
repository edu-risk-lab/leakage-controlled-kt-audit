import pandas as pd
from pathlib import Path

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
    
    # Generate TeX
    tex_out = Path("results/tables/cold_start_comparison.tex")
    
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Comparison of Sequence-KT (No-Graph) vs Graph-KT (Graph) average AUC across frequency strata.}",
        "\\label{tab:cold-start-comparison}",
        "\\footnotesize",
        "\\setlength{\\tabcolsep}{4pt}",
        "\\begin{tabular}{@{}ll|cc|ccc@{}}",
        "\\toprule",
        "& & \\multicolumn{2}{c|}{\\textbf{No-Graph}} & \\multicolumn{3}{c}{\\textbf{Graph}} \\\\",
        "\\cmidrule(lr){3-4} \\cmidrule(l){5-7}",
        "Dataset & Stratum & DKT & SimpleKT & GKT & GIKT & DGEKT \\\\",
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
        
        dkt = f"{row['dkt']:.3f}" if not pd.isna(row['dkt']) else "-"
        simplekt = f"{row['simplekt']:.3f}" if not pd.isna(row['simplekt']) else "-"
        gkt = f"{row['gkt']:.3f}" if not pd.isna(row['gkt']) else "-"
        gikt = f"{row['gikt']:.3f}" if not pd.isna(row['gikt']) else "-"
        dgekt = f"{row['dgekt']:.3f}" if not pd.isna(row['dgekt']) else "-"
        
        lines.append(f"{ds_name} & {stratum_str} & {dkt} & {simplekt} & {gkt} & {gikt} & {dgekt} \\\\")
        
    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}"
    ])
    
    tex_out.write_text("\\n".join(lines), encoding="utf-8")
    print(f"Generated {tex_out}")

if __name__ == "__main__":
    main()
