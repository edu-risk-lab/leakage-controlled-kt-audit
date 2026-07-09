import os
import torch
import numpy as np
from pathlib import Path

# Fix CPU patching issue in pykt_engine
import src.pykt_engine as pykt_engine
if os.environ.get("FORCE_CPU") == "1":
    pykt_engine._patch_pykt_cpu_tensors()

from src.pykt_engine import run_pykt_fold

folds = [
    (0, 17, 12646),
    (1, 18, 12646),
    (2, 19, 12646)
]
operators = [
    ("edge_drop", 0.1), ("edge_drop", 0.2), ("edge_drop", 0.3), ("edge_drop", 0.9),
    ("node_drop", 0.1), ("node_drop", 0.2), ("node_drop", 0.3), ("node_drop", 0.9),
    ("prereq_preserve", 0.1), ("prereq_preserve", 0.2), ("prereq_preserve", 0.3),
    ("none", 0.0)
]

out_file = Path("results/q1/ddr_downstream_gkt/ddr_downstream_gkt_seed17.csv")

with open(out_file, "w") as f:
    f.write("dataset,model,fold,split_seed,operator,p,ddr,n_edges_orig,n_edges_pert,num_c,auc,acc,nll,status\n")

    for fold, split_seed, _ in folds:
        work_dir = Path(f"results/pykt_work/xes3g5m/fold_{fold}_seed_{split_seed}/ddr_downstream/gkt")
        for op, p in operators:
            print(f"Restoring {op} p={p} fold={fold}")
            if op == "none":
                graph_tag = "p0_protocol"
            else:
                graph_tag = f"{op}_{p:.2f}_seed17"
            
            # The .npz file is strictly used only if graph_tag != "p0_protocol". 
            # In run_pykt_fold, graph_npz is passed as work_dir / f"gkt_graph_{graph_tag}.npz"
            graph_npz = work_dir / f"gkt_graph_{graph_tag}.npz"
            
            # Call run_pykt_fold which will load the checkpoint and evaluate
            try:
                auc, acc, nll, note, _, _, _ = run_pykt_fold(
                    display_model="gkt",
                    pykt_name="gkt",
                    work_dir=work_dir,
                    num_q=863,
                    num_c=863,
                    graph_npz=graph_npz,
                    graph_tag=graph_tag,
                    hyperparams={"hidden_dim": 100, "emb_size": 100, "dropout": 0.5},
                    epochs=30,
                    batch_size=64,
                    lr=1e-3,
                    seed=17,
                    max_seq_len=200
                )
                f.write(f"xes3g5m,gkt,{fold},{split_seed},{op},{p},0.0,0,0,863,{auc},{acc},{nll},restored\n")
                f.flush()
            except Exception as e:
                print(f"Failed {op} {p}: {e}")

print("Done restoring!")
