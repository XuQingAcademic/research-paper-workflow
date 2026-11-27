# Manifest preflight interpretation

Read when preparing or resolving findings from `scripts/validate_manifest.py`.
Preflight checks declared settings; actual attempt logs and scientific validity
still require the simulation audit.

## Failure handling

The existing `execution.fail_policy: record_and_stop_unit` remains supported.
Simple explicit recording/prohibition clauses are also recognized, including
`record every failure; do not skip or silently replace`. Arbitrary conditional,
quoted, contradictory or otherwise unsupported prose is not classified from a
single keyword. `UNVERIFIED_FAILURE_POLICY` asks for a checkable interpretation;
it does not assert that the policy is unsafe.

For conditional handling use an explicit compatible mapping:

```yaml
fail_policy:
  mode: predefined_method_branch
  preserve_attempts: true
  preserve_denominator: true
  report_failures: true
  branch:
    definition: methods.md#solver-branch
    defined_before_run: true
    report_rate: true
```

Other modes are `record_and_stop_unit` and `record_and_continue`; omit `branch`
for them, keeping the three preservation/reporting booleans. `false` is an
unsafe declaration; strings such as `"true"`, missing fields and unknown modes
are unresolved input, not verified settings. A definition locator is a reference
to inspect, not proof that the branch was specified before results were seen.
Keep the attempt lineage, method definition and reported branch rate consistent
with these declarations; never replace failed runs silently or change the
planned denominator to obtain a favorable result.

## Check the actual experiment target

Null-DGP checks apply to testing targets, including the testing part of a mixed
study. Bias/RMSE estimation studies and interval coverage studies do not require
an invented hypothesis-testing null. Their estimands still need an explicit
truth source, and coverage measures need a defined coverage event; these entries
state what must be checked and do not themselves verify the scientific claim.

The optional `study.task_type` identifies `estimation`, `testing`, `interval`,
`mixed` or `diagnostic`. Existing manifests can infer a target from recognized
measure IDs such as `bias`, `rmse`, `size`, `power`, `coverage`, `interval_length`,
`runtime` and `failure_rate`. For a custom metric, declare its
`performance.measures[].target_type` and a concrete definition. A custom ID
can instead use `kind` to identify a recognized metric (for example `coverage`);
known IDs, kinds and target types must agree. Unknown or
contradictory declarations need interpretation, not a guessed exemption.
Calling a study estimation does not remove the null requirement when it reports
size/power; declaring a known testing metric to be estimation is a conflict.
Diagnostic-only metrics do not establish inferential validity.

Classify an actual null explicitly as `null`; labels such as `non_null` do not
establish one. When `truth_by_method` is supplied, a null for a benchmark does
not establish a null for a proposed/confirmatory method; explicit method truth
must cover the testing targets. Without it, the legacy `classification: null`
is accepted as a declaration. This checks declared applicability and consistency,
not actual DGP truth. The actual method-specific null, same-family calibration
and any required per-cell anchors remain scientific checks under the existing
simulation audit. Derived `task_scope` labels explicitly retain this boundary.
