import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score
from pathlib import Path
import logging
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

logging.basicConfig(level=logging.INFO, format='%(message)s')

def compute_delta(args):
    """
    args is a tuple: (user_indices_sampled, users_unique, groups, y_true, y_prob_a, y_prob_b)
    """
    user_indices, groups, y_true, y_prob_a, y_prob_b = args
    
    # We need to map the sampled user_indices to the actual row indices.
    # To do this fast, we can use np.concatenate on the pre-computed row indices for each user.
    resampled_rows = np.concatenate([groups[u] for u in user_indices])
    
    true_resampled = y_true[resampled_rows]
    if len(np.unique(true_resampled)) < 2:
        return np.nan
        
    prob_a_resampled = y_prob_a[resampled_rows]
    prob_b_resampled = y_prob_b[resampled_rows]
    
    auc_a = roc_auc_score(true_resampled, prob_a_resampled)
    auc_b = roc_auc_score(true_resampled, prob_b_resampled)
    
    return auc_a - auc_b

def bootstrap_pair(df_a, df_b, pair_name, n_resamples=10000, n_jobs=None):
    # Align rows
    if len(df_a) != len(df_b):
        logging.warning(f"Length mismatch for {pair_name}: {len(df_a)} vs {len(df_b)}")
        
    # We assume rows are already aligned by baseline_runner.py (same fold, same order)
    # Check if user_id perfectly matches
    if not np.array_equal(df_a["user_id"].values, df_b["user_id"].values):
        logging.warning("user_id arrays do not match exactly! Sorting or aligning required.")
        # We can just join them, but the output is already 1:1 matching from PyKT test sequence
        pass
        
    y_true = df_a["y_true"].values
    y_prob_a = df_a["y_prob"].values
    y_prob_b = df_b["y_prob"].values
    users = df_a["user_id"].values
    
    # Pre-group row indices by user
    # pandas groupby is fast
    # df_a["_row_idx"] = np.arange(len(df_a))
    # groups_dict = df_a.groupby("user_id")["_row_idx"].apply(np.array).to_dict()
    
    # A faster numpy way to group contiguous users (since they are contiguous in PyKT):
    # wait, PyKT keeps users contiguous!
    _, user_starts, user_counts = np.unique(users, return_index=True, return_counts=True)
    
    # groups_dict maps index i (from 0 to num_users-1) to an array of row indices
    groups = [np.arange(start, start + count) for start, count in zip(user_starts, user_counts)]
    num_users = len(user_starts)
    
    np.random.seed(42)
    # Generate all resamples
    # We sample indices from 0 to num_users-1
    resamples = np.random.randint(0, num_users, size=(n_resamples, num_users))
    
    args_list = [(resamples[i], groups, y_true, y_prob_a, y_prob_b) for i in range(n_resamples)]
    
    logging.info(f"Starting {n_resamples} resamples for {pair_name} with {num_users} learners and {len(y_true)} rows.")
    
    deltas = []
    if n_jobs is None:
        n_jobs = max(1, multiprocessing.cpu_count() - 2)
        
    with ProcessPoolExecutor(max_workers=n_jobs) as executor:
        for delta in executor.map(compute_delta, args_list, chunksize=100):
            if not np.isnan(delta):
                deltas.append(delta)
                
    deltas = np.array(deltas)
    delta_mean = np.mean(deltas)
    ci_lower = np.percentile(deltas, 2.5)
    ci_upper = np.percentile(deltas, 97.5)
    
    logging.info(f"{pair_name}: Delta={delta_mean:.4f} 95% CI=[{ci_lower:.4f}, {ci_upper:.4f}]")
    
    return {
        "Model Pair": pair_name,
        "$\\Delta$AUC": f"{delta_mean:+.4f}",
        "95\\% CI": f"[{ci_lower:+.4f}, {ci_upper:+.4f}]",
        "n_learners": num_users,
        "n_rows": len(y_true)
    }

def synthesize_table():
    dataset = "xes3g5m"
    folds = [0, 1, 2]
    
    # Load and pool
    dfs_simplekt = []
    dfs_gkt = []
    dfs_gikt = []
    
    for fold in folds:
        dir_path = Path("results/predictions") / dataset / f"fold_{fold}"
        try:
            df_s = pd.read_parquet(dir_path / "simplekt.parquet")
            df_g = pd.read_parquet(dir_path / "gkt.parquet")
            df_i = pd.read_parquet(dir_path / "gikt.parquet")
            dfs_simplekt.append(df_s)
            dfs_gkt.append(df_g)
            dfs_gikt.append(df_i)
        except FileNotFoundError:
            logging.error(f"Missing parquet files for fold {fold}")
            return
            
    df_simplekt_pooled = pd.concat(dfs_simplekt, ignore_index=True)
    df_gkt_pooled = pd.concat(dfs_gkt, ignore_index=True)
    df_gikt_pooled = pd.concat(dfs_gikt, ignore_index=True)
    
    res_gkt = bootstrap_pair(df_gkt_pooled, df_simplekt_pooled, "gkt vs simplekt")
    res_gikt = bootstrap_pair(df_gikt_pooled, df_simplekt_pooled, "gikt vs simplekt")
    
    out_df = pd.DataFrame([res_gkt, res_gikt])
    out_df.to_csv("results/tables/bootstrap_auc_ci.csv", index=False)
    
    tex_str = out_df.to_latex(index=False, escape=False, column_format="lrrrr")
    
    # Strict formatting demanded by the prompt
    custom_header = """\\begin{table}[h]
\\centering
\\caption{Learner-level bootstrap 95\\% CIs for $\\Delta$AUC (pooled folds 0-2).}
\\label{tab:bootstrap-auc-ci}
\\begin{tabular}{lrrrr}
\\toprule
\\textbf{Model Pair} & $\\Delta$\\textbf{AUC} & \\textbf{95\\% CI} & \\textbf{n\\_learners} & \\textbf{n\\_rows} \\\\
\\midrule"""
    
    # Remove pandas default header and bottom
    lines = tex_str.split("\n")
    data_lines = []
    capture = False
    for line in lines:
        if "\\midrule" in line:
            capture = True
            continue
        if "\\bottomrule" in line:
            break
        if capture and line.strip():
            data_lines.append(line)
            
    final_tex = custom_header + "\n" + "\n".join(data_lines) + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    
    Path("results/tables").mkdir(parents=True, exist_ok=True)
    with open("results/tables/bootstrap_auc_ci.tex", "w") as f:
        f.write(final_tex)
        
    logging.info("Bootstrap CI table successfully written.")

if __name__ == "__main__":
    synthesize_table()
