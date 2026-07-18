# Knowledge Tracing audit profile

Apply after the general audit.

## Data and split

- Identify interaction unit, learner, item, KC/skill, response, timestamp and multi-skill convention.
- Verify learner-based and temporal splits at learner/sequence level as claimed.
- For temporal split, test per learner that training events precede validation/test events.
- Fit scaler, encoder, feature selection and thresholds on training data only.
- Build Q-matrix additions, prerequisite/similarity/co-occurrence graphs and sparse buckets using the declared admissible partition only.
- Check duplicate interactions, sequence truncation, minimum-length filters and learner overlap.

## Sparse and cold-start evaluation

- Define thresholds, counting unit and whether counts are train-only.
- Separate zero-interaction cold start from very sparse KCs/learners/items.
- Report group sample size; flag unreliable AUC/metrics for small groups.
- Ensure the same entity does not change bucket because test interactions were counted.

## Model and metric

- Verify question/KC/response mapping, masking, next-step target alignment and padding exclusion.
- Check AUC aggregation level, micro/macro convention, ACC threshold, NLL/Brier/ECE implementation and calibration bins.
- For Brier decomposition, verify UNC/REL/RES definitions and bin weighting.
- Compare baselines on the same split, sequence length, feature access and tuning budget.
- Separate fallback baseline from the named intended baseline.

## Graph/SSL

- Check directed prerequisite orientation and DAG/cycle handling.
- Verify relation construction is train-only when claimed.
- Check augmentation preserves prerequisite constraints and does not expose labels/test structure.
- Trace graph version and edge provenance to each run.
- Require ablations for relation types, fusion and SSL components when claimed as contributions.

## Statistical reporting

- Record all seeds and failed runs; do not select the best seed.
- Pair comparisons by identical dataset/split/seed when appropriate.
- Correct multiple comparisons and report effect/CI where suitable.
- Do not generalize sparse-KC findings from datasets with no KCs in the defined sparse bucket.

