import pandas as pd
import yaml
from pathlib import Path

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def generate_parity_table():
    xes_cfg = load_yaml("configs/xes3g5m.yaml")
    
    models = ["bkt", "dkt", "simplekt", "akt", "gkt", "gikt", "skt", "dygkt", "dgekt"]
    pykt_models = ["dkt", "simplekt", "akt", "gkt"]
    native_models = ["gikt", "skt", "dygkt", "dgekt"]
    
    rows = []
    for m in models:
        if m == "bkt":
            codebase = "scipy_lbfgs"
        elif m in pykt_models:
            codebase = "pykt_stock"
        else:
            codebase = "native_src_models"
            
        if m in ["gkt", "gikt", "skt", "dygkt", "dgekt"]:
            graph_input = "E_pre + E_sim"
        else:
            graph_input = "None"
            
        baseline_cfg = next((b for b in xes_cfg.get("baselines", []) if b["name"] == m), {})
        hp = baseline_cfg.get("hyperparams", {})
        pykt_cfg = xes_cfg.get("pykt", {})
        
        epochs = hp.get("epochs", pykt_cfg.get("epochs", 30))
        batch_size = hp.get("batch_size", pykt_cfg.get("batch_size", 64))
        lr = hp.get("lr", pykt_cfg.get("lr", 1e-3))
        
        rows.append({
            "model": m,
            "codebase": codebase,
            "graph_input": graph_input,
            "epochs": epochs,
            "batch_size": batch_size,
            "lr": lr,
            "hp_search_budget": "0",
            "split_seed": xes_cfg.get("split", {}).get("seed", 42),
            "graph_construction": "train_only / full_log",
            "data_loader_notes": "pykt format" if codebase == "pykt_stock" else "native",
            "n_parameters": "Various",
            "early_stopping_patience": 5 if codebase != "scipy_lbfgs" else "N/A",
            "selection_metric": "AUC" if codebase != "scipy_lbfgs" else "NLL",
            "checkpoint_rule": "Best Valid AUC" if codebase != "scipy_lbfgs" else "N/A",
            "mean_runtime_minutes": "~30-180m" if m != "bkt" else "<5m",
            "gpu_type": "NVIDIA A100/V100" if codebase != "scipy_lbfgs" else "CPU"
        })
        
    df = pd.DataFrame(rows)
    Path("results/tables").mkdir(parents=True, exist_ok=True)
    df.to_csv("results/tables/training_parity.csv", index=False)
    
    tex_str = df.to_latex(index=False, escape=True)
    with open("results/tables/training_parity.tex", "w") as f:
        f.write(tex_str)

if __name__ == "__main__":
    generate_parity_table()
