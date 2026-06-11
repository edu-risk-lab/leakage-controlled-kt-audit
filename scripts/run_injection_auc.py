import argparse
import logging
from pathlib import Path
import subprocess

import pandas as pd
import numpy as np

from src.io_utils import load_yaml, load_interactions
from src.split_checker import learner_based_folds
from src.graph_builder import build_q_matrix_from_train, infer_prerequisites_from_train
from src.dag_audit import prune_cycles

logging.basicConfig(level=logging.INFO, format='%(message)s')

def build_injected_graphs():
    cfg = load_yaml(Path("configs/xes3g5m.yaml"))
    dataset = cfg["dataset"]
    df = load_interactions(Path(f"data/processed/{dataset}.parquet"))
    
    ratios = tuple(cfg.get("split", {}).get("ratios", [0.7, 0.1, 0.2]))
    graph_cfg = cfg.get("graph", {})
    
    # Run only for fold 0
    fold, split_seed, splits = next(learner_based_folds(df, ratios, cfg.get("split", {}), default_seed=42))
    
    train_base = splits["train"].copy()
    train_base["split"] = "train"
    train_base["fold"] = fold
    
    test_base = splits["test"].copy()
    test_base["split"] = "test"
    
    q_train = build_q_matrix_from_train(train_base)
    
    injection_rates = [(0.0, "inject00"), (0.05, "inject05"), (0.20, "inject20")]
    out_dir = Path("data/processed") / dataset / f"fold_{fold}"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # We will log the graph statistics
    logs = []
    
    for p, tag in injection_rates:
        logging.info(f"Running injection for {tag} (p={p})")
        
        if p > 0:
            n_inject = int(len(test_base) * p)
            injected_test = test_base.sample(n=n_inject, random_state=42 + int(p*100))
            train_injected = pd.concat([train_base, injected_test], ignore_index=True)
            train_injected["split"] = "train"
        else:
            n_inject = 0
            train_injected = train_base.copy()
            
        pre = infer_prerequisites_from_train(
            train_injected,
            q_train,
            max_edges=int(graph_cfg.get("e_pre_max_edges", 5000)),
            top_k_per_node=int(graph_cfg.get("e_pre_top_k_per_node", 10)),
            support_quantile=float(graph_cfg.get("e_pre_support_quantile", 0.90)),
        )
        
        candidates = len(pre)
        
        # Production DAG audit / cycle pruning
        pruned, prune_log = prune_cycles(pre)
        retained = len(pruned)
        
        # Injected edge counts
        # We need to know which edges came from the injected data.
        # But wait, it's easier to just compute how many edges overlap with the test set
        # Actually, the prompt says "injected-edge count and retained_injected_ratio"
        # We can just count how many edges in `pruned` are NOT in the `p=0` baseline graph!
        # Let's save the pruned edges for p=0 as baseline.
        if p == 0:
            baseline_edges = set(zip(pruned["src_kc"], pruned["dst_kc"]))
            injected_count = 0
            retained_injected = 0
        else:
            injected_count = sum(1 for src, dst in zip(pre["src_kc"], pre["dst_kc"]) if (src, dst) not in baseline_edges)
            retained_injected = sum(1 for src, dst in zip(pruned["src_kc"], pruned["dst_kc"]) if (src, dst) not in baseline_edges)
            
        logs.append({
            "arm": tag,
            "candidate_edges": candidates,
            "retained_edges_after_pruning": retained,
            "injected_edges": injected_count,
            "retained_injected_ratio": (retained_injected / injected_count) if injected_count else 0.0
        })
        
        pre_path = out_dir / f"e_pre_{tag}.csv"
        sim_path = out_dir / f"e_sim_{tag}.csv"
        
        pruned.to_csv(pre_path, index=False)
        pd.DataFrame(columns=["src_kc", "dst_kc", "weight", "source"]).to_csv(sim_path, index=False)
        logging.info(f"Saved {tag} edges to {pre_path}")
        
    log_df = pd.DataFrame(logs)
    print("\nInjection Graph Logs:")
    print(log_df.to_string(index=False))
    
def run_baselines():
    dataset = "xes3g5m"
    tags = ["inject00", "inject05", "inject20"]
    models = ["simplekt", "gkt", "gikt"]
    fold = 0
    
    for tag in tags:
        for model in models:
            logging.info(f"==== Evaluating {model} on graph {tag} ====")
            cmd = [
                "python", "-m", "src.baseline_runner",
                "--config", f"configs/{dataset}.yaml",
                "--baseline-backend", "pykt",
                "--fold-idx", str(fold),
                "--graph-construction", tag,
            ]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to evaluate {model} on {tag}. Exit code: {e.returncode}")

def collect_results():
    dataset = "xes3g5m"
    tags = ["inject00", "inject05", "inject20"]
    models = ["simplekt", "gkt", "gikt"]
    fold = 0
    
    cache_dir = Path("results/cache")
    results = []
    
    for tag in tags:
        for model in models:
            res_path = cache_dir / f"{dataset}_fold_{fold}_{model}_{tag}_result.json"
            if res_path.exists():
                import json
                with open(res_path, "r") as f:
                    data = json.load(f)
                    results.append({
                        "Model": model,
                        "Injection Arm": tag,
                        "AUC": data.get("test_auc", 0.0),
                        "ACC": data.get("test_acc", 0.0)
                    })
    
    df = pd.DataFrame(results)
    if not df.empty:
        # Pivot the table to show Model rows and Injection Arm columns for AUC
        pivot_df = df.pivot(index="Model", columns="Injection Arm", values="AUC").reset_index()
        print("\nDownstream AUC Results (Fold 0):")
        print(pivot_df.to_string(index=False))
        
        Path("results/tables").mkdir(parents=True, exist_ok=True)
        pivot_df.to_csv("results/tables/downstream_auc_injection.csv", index=False)
        
        # Output simple LaTeX table
        tex = pivot_df.to_latex(index=False, float_format="%.4f")
        with open("results/tables/downstream_auc_injection.tex", "w") as f:
            f.write(tex)

if __name__ == "__main__":
    build_injected_graphs()
    run_baselines()
    collect_results()
