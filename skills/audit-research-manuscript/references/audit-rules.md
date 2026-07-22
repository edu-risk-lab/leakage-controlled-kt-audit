# Audit rule catalog

Use these IDs consistently. Add a project-specific suffix only when necessary.

| Prefix | Category | Representative checks |
|---|---|---|
| REF | Reference identity | nonexistent DOI, metadata mismatch, duplicate, retracted/corrected version |
| CIT | Citation support | source does not support claim, reversed meaning, secondary source used as primary evidence |
| INT | Integrity | fabricated data/log/result, unattributed paraphrase, undisclosed material AI use |
| STR | Structure | RQ–method–result–conclusion disconnect, missing limitation, related-work list |
| CON | Consistency | conflicting numbers, notation drift, main/supplement mismatch, unresolved reference |
| MTH | Method | under-specified design, unfair baseline, post-hoc protocol, wrong comparison |
| DAT | Data | wrong version/statistics/license, preprocessing leakage, weak anonymization |
| COD | Code | prose/formula/code mismatch, test-set tuning, incorrect metric, hard-coded result |
| STA | Statistics | wrong analysis unit/test, missing uncertainty/effect size, multiplicity, overclaim |
| REP | Reproducibility | missing seed/config/environment/commit/artifact lineage |
| FIG | Figures/tables | numbers not traceable, misleading axes, caption mismatch, illegibility |
| PRI | Privacy/security | identifiers, secrets, restricted data disclosure |
| LIC | License/copyright | unlicensed dataset/code/figure/table or missing attribution |
| AIP | AI policy | prohibited use, missing disclosure, AI as author, unverified AI output |
| VEN | Venue compliance | scope/template/limit/anonymity/submission requirement |

## Minimum rule set

- REF-001: identifier cannot be resolved or metadata cannot be verified.
- REF-002: DOI resolves but title/authors/year/venue materially mismatch.
- CIT-001: cited source does not support the adjacent claim.
- CIT-002: strong claim relies only on abstract/snippet/secondary summary.
- INT-001: result or data has no source artifact and may be fabricated or manually altered.
- INT-002: close paraphrase/structure lacks attribution; similarity score alone is not proof.
- CON-001: headline number conflicts across manuscript locations.
- CON-002: unresolved placeholder, citation, table, figure, equation or appendix reference.
- CON-003: symbols/terms change meaning or remain undefined.
- MTH-001: split/preprocessing/feature construction permits leakage.
- MTH-002: baseline comparison uses unequal data, tuning, features or selection budget.
- COD-001: code/config differs from described method.
- COD-002: test data influences training, tuning, checkpoint or model selection.
- STA-001: `significant` lacks suitable test/CI or effect evidence.
- STA-002: multiple comparisons lack planned correction or transparent scope.
- STA-003: seeds/runs are treated as independent samples without justification.
- STA-004: conclusion exceeds datasets, population, task or design.
- REP-001: reported table/figure cannot be traced to a run/artifact/script.
- REP-002: run lacks dataset version, split, commit, config, seed or environment.
- FIG-001: table/figure values conflict with source results.
- FIG-002: axis, scale, units, sample size or uncertainty presentation is misleading/incomplete.
- PRI-001: blinded manuscript or artifact contains identifying/private information.
- LIC-001: reuse/redistribution right or attribution is unverified.
- AIP-001: AI usage disclosure does not match verified policy or actual recorded use.
- VEN-001: mandatory venue requirement fails or is not verified.

## Evidence strength

Prefer, in order:

1. original raw/immutable artifact and deterministic regeneration;
2. official publisher/dataset/repository record;
3. versioned code/config/log with checksum;
4. author-maintained notes;
5. AI inference without source — only a lead, never final evidence.

