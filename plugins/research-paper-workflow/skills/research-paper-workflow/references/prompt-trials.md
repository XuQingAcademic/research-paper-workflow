# Evidence-based prompt and execution trials

Read during requested workflow maintenance, repeated evidenced execution
failure, or explicit model/prompt comparison. Ordinary paper work does not
start a benchmark or update global instructions. Scientific standards remain
with specialists; this reference owns execution adaptation only.

## Bounded real-task loop

Recover the actual request, input versions, failed output and corrective evidence.
Diagnose task ambiguity, retrieval, execution, reasoning, verification or an
unavailable resource before changing instructions. More warnings cannot repair
a missing source or proof bridge. A local answer repair is not a global rule.

Reuse bounded real tasks and existing proof/source/result records. Select only
relevant families: idea/conventional-baseline comparison, source applicability,
one proof bridge, simulation accounting, scientifically frozen prose, or resume.
Require an actual artifact or substantive judgment, not rule recitation. Include
valid work that should finish, to expose refusal, invented defects and needless
warnings. No compulsory all-family suite or fixed sample quota.

Separate development and final evaluation by project/problem family where
feasible. Freeze the candidate before opening withheld tasks. A task seen by
the author, teacher or optimizer is exposed; a used holdout becomes a regression
for later tuning. Never relabel synthetic or exposed work as real/withheld.
A one-project trial supports only a one-project scope.

Precommit one primary benefit and material threshold: correct completion/error
reduction, avoidable rework, or observed time/tokens/cost with quality preserved.
Keep missed errors, false alarms and correct completions visible separately.
No average offsets a lost assumption, false theorem, fabricated source/result,
unauthorized write or missing deliverable. Retain failures/timeouts. An open
scientific question is not a known-answer test because a model scored it.
Repeat noisy comparisons when needed; a small trial is not a population-level
or statistical-significance claim.

## Adapt execution, not truth

Keep the target, evidence ceiling and permissions fixed. Change one coherent
cause: task granularity, relevant evidence, examples, output shape, stopping
rule or selection. Longer prompts, personas, forced step-by-step prose and more
reviewers are hypotheses, not universal improvements. Request checkable
derivations/artifacts, not private reasoning.

Bind a profile to model/version, reasoning setting, tools, budget and task family.
Do not hardcode model rankings, silently downgrade or transfer another model's
success. An unmeasured configuration keeps its default and normal scientific
route. Missing profiles never block ordinary authorized work. Cheaper bounded
tasks need relevant evidence and escalation triggers; substantive scientific
judgments retain specialist checks.

Keep runtime/resource allowance comparable. Extra documents, stronger teacher
outputs, tools, training or compute are resources, not prompt-only gains: label
these `execution` or `system`. Test each model against its own controlled
baseline; do not infer general capability equivalence. Profiles contain concise
original instructions, not private paper content or hidden reference answers.
For cost claims, include retries, retrieval, selection and required verification
in the per-task observation. Report one-time optimization/teacher cost separately;
unmeasured development cost does not establish net savings or a break-even point.

Iterate only when a failed check or new evidence can change the answer. Feedback
names the offending artifact/step and applicable criterion, not self-confidence
or agreement. Use the existing budget for bounded retries and stop/switch
conditions. Stop on adequate completion, no new information, exhausted budget
or a failure needing another route. No unattended testing, new provider access
or ongoing automatic skill updates are implied.

## Existing runner, thin adoption layer

Use the installed manager's `references/improvement-loop.md`,
`references/frozen-evaluations.md`, `evaluation_bundle.py`,
`compare_evaluations.py` and, when appropriate, ResearchBench-Econ runner.
Resolve the actual installed path, not a historical version literal. Keep hidden
rubrics, old answers and other arms out of subject contexts. Retain fresh-context
dispatch/output/review evidence; offline replay is not a new model execution.
Existing private-source/processing boundaries remain in force.

`scripts/prompt_trials.py` reuses the manager's schema-2 integrity/content
comparison, adding a read-only adoption/selection decision. No model calls or
installation. Keep one plan beside existing maintenance evidence (or project-
local `.paper/workflow/prompt-trials/`), not another scientific ledger. No record
for every task. Existing evaluation records remain unchanged.

Plan schema `research-prompt-trial.v1`:

- `id`, `task_family`, `hypothesis`, `failure_diagnosis`, `stop_condition`;
- `change_kind`: `prompt`, `execution` or `system`;
- `profile`: `id`, `runtime` (complete effective settings, including `model`,
  `model_version`, `reasoning_effort`, `tools`, `budget`), `version_scope`
  (`snapshot` or `session`), `instructions` (`path`, `sha256`), `escalate_when`;
- `objective`: `metric` (`quality`, `wall_seconds`, `tokens`, `cost_usd`, `rework`)
  and positive `min_gain`; quality counts heldout failed-to-passed checks;
  efficiency also freezes an `accounting_key` shared by ALL cases and arms;
- `cases`: exact run case IDs, each with `project_id`, `origin` (`real` or
  `synthetic`), `exposure` (`exposed` or `withheld`), `positive_control` and
  `source` (`path`, `sha256`) matching the actual frozen task input. Keep the
  underlying project/source lineage with that task. Paths are relative to the plan.

Bind the plan with `--external trial_plan=PLAN.json` into BOTH frozen bundles
before dispatch. Candidate instructions must be in its frozen `skills/` tree
and actually loaded by the subject. Store the COMPLETE effective generation/tool/
budget configuration in `run_settings.runtime`, separate from case-order and
provenance notes; it must equal the profile runtime exactly. Flat legacy run
settings can be used only when the whole object equals that runtime. These
hashes/declarations do not prove
exposure history, instruction use, model identity or truth; inspect actual logs
and sources. Unknown identity prevents profile promotion, not ordinary work.
`snapshot` requires a real immutable version identifier, not a mutable alias or
UI label. Otherwise use `session` and record an actual `runtime.session_id`:
selection cannot carry that result into another session. No string comparison
can detect an unannounced provider change; record this observability limit and
invalidate the profile on a known change instead of inventing a stable version.

Only efficiency trials add `measurements[METRIC]` to existing run cases:
observed `value`, `measurement: "observed"`, matching `accounting_key` and a
hash-bound `source`. Unknown stays unavailable; text length, token estimates and
self-estimated rework are not observed savings. Quality-only trials need no
usage bookkeeping.
The measurement source is a retained JSON observation with the same `value`,
`measurement`, `accounting_key`; the tool checks those fields, not just its hash.
Preserve the original provider/timer log behind any normalized observation.

```bash
python3 -B "$WORKFLOW/scripts/prompt_trials.py" decide \
  --manager-root "$MANAGER" --plan PLAN.json \
  --baseline BASELINE.json --candidate CANDIDATE.json
python3 -B "$WORKFLOW/scripts/prompt_trials.py" select \
  --manager-root "$MANAGER" --plan PLAN.json \
  --baseline BASELINE.json --candidate CANDIDATE.json \
  --runtime CURRENT-RUNTIME.json --task-family source-applicability --project-id PROJECT
```

`eligible_scoped` / `selected` exits 0; `keep_baseline`, `reject` or `fallback`
exits 1; incomplete/invalid evidence exits 2. Exit 0 requires primary benefit
on real withheld work, a real valid-work control and no candidate failures.
Efficiency also requires all baseline quality checks to pass and no per-case
efficiency loss. A justified trade-off needs a separately scoped trial, not an
exception invented after seeing outcomes.

## Keep defaults small

Ties, exposed-only gains, unknown metrics and model/scope drift do not select a
new profile; regressions reject it. Retain failed attempts as evidence, not
active instructions. `select` rechecks underlying artifacts and exact scope:
a saved decision cannot authorize stale reuse. It returns one matching profile,
never changes configured models or launches providers.
Automatic selection is limited to the real project IDs in the trial; a new
project falls back until a relevant additional trial supports that scope.
When a credible contrary case appears, suspend that profile for affected work,
preserve the case and return to the baseline while diagnosing it. Do not treat
one exception as a universal ban or restart unrelated verified work.

Eligibility supports bounded use within existing authorization, not a global
rule or scientific certification. Wider use needs relevant additional tasks.
At authorized installation, consolidate at the existing owner, preserve a
scoped rollback diff and remove candidate-only scaffolding. Do not retain an
unhelpful rule because it sounds safer.
