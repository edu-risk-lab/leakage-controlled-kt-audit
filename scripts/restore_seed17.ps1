$seed = 17
$OUT = "results/q1/ddr_downstream_gkt/ddr_downstream_gkt_seed17.csv"

Write-Host "Restoring grid..."
python -m scripts.ddr_downstream --config configs/xes3g5m.yaml --model gkt --operators edge_drop node_drop prereq_preserve --ps 0.10 0.20 0.30 --experiment-seed $seed --perturb-seed $seed --out $OUT

Write-Host "Restoring anchors..."
python -m scripts.ddr_downstream --config configs/xes3g5m.yaml --model gkt --operators edge_drop node_drop --ps 0.90 --experiment-seed $seed --perturb-seed $seed --out $OUT

git add -f $OUT
git commit -m "Fix seed 17 data: replace incorrect assist2012 rows with restored xes3g5m results"
git push
