---
name: research-paper-workflow
description: Coordinate an econometrics or quantitative-economics paper from research ideas through literature, design, proofs, empirical evidence, manuscript, independent review, revision, and a submission package. Use for an end-to-end paper workflow or resuming a multi-stage research project; route isolated proof, simulation, or prose-editing requests directly to the specialist skill.
---

# Research Paper Workflow

Turn a research question into a source-grounded, reproducible manuscript using
the installed research portfolio. Own sequencing, handoffs, and continuity;
delegate scientific decisions to the relevant specialist. The deliverable may
be a complete paper or an explicitly simulation-deferred manuscript, depending
on the user's instruction and the evidence actually available.

For a complete LaTeX risk-results manuscript enrolled in controlled delivery,
the workflow host publishes through
[`scripts/deliver_manuscript.py`](scripts/deliver_manuscript.py). The editor
works on the draft and the host runs the evidence check outside the editing
session. Use the existing project entry and
[the controlled delivery instructions](references/controlled-manuscript-delivery.md).

## Start from the actual project

Discover the capabilities actually available. Read
[dependency-resolution.md](references/dependency-resolution.md) when a specialist
is missing or supplied by a different provider. Continue work independent of
the missing capability and leave dependent conclusions pending.

Read the active manuscript, project instructions, existing `.paper/` state, and
the smallest set of current results needed to identify the next unmet objective.
Respect existing filenames, language, programming environment, and author
decisions. Do not initialize a second claims database or rebuild finished work.
For a new project, recover a concrete working question and paper type, then use
the idea specialist to establish what the strongest available solutions already
deliver and develop mechanisms for the remaining obstacles. Continue bounded
discovery while material author choices are pending; no chosen idea is required
to start this work.

When the author requires empirical-first discovery or a real application, apply
the [empirical-first entry gate](references/empirical-bridge.md#empirical-first-entry-gate)
at candidate recommendation, design freeze and resumption. Require documented
real-world mechanism, inspected usable data and an actual baseline probe before
advancing the empirical route. A prior recommendation, manuscript or change of
paper-type label does not discharge this dependency.

Classify the paper as `theory`, `methods`, `empirical`, or `hybrid`. Classify
simulation execution as `run`, `deferred`, or genuinely `not-applicable`.
Limited compute is `deferred`, never `not-applicable`. Default to bounded smoke
and pilot work until measured resource needs justify production runs.

For long/resumed work, recover the outcome and current bottleneck with
[goal-and-learning.md](references/goal-and-learning.md). For cross-stage feedback,
material iterative optimization, an explicitly activated continuous cycle, or
requested prompt/model adaptation, use the matching section of
[continuity-and-revision-routing.md](references/continuity-and-revision-routing.md).
Preserve the frozen objective, actual author decisions, scientific invariants,
bounded trade-offs and required independent checks; do not activate these
maintenance controllers for an ordinary bounded question. Unknown or tied prompt
trials keep the configured baseline.

At a consequential investment boundary or decision-changing evidence, apply
[strategic-review.md](references/strategic-review.md): reassess research value
and the route separately from local execution quality, then continue, pivot,
park or stop at the evidence-supported scope. Reuse existing design/review notes;
do not add a recurring panel, score or compulsory controller. A frozen design
is a comparison baseline, not a commitment to preserve a defeated idea.

Route isolated proof, simulation and prose work directly to its specialist.
A coordinated revision is needed when several specialist-owned objects change
together, including assumptions/scope, notation and manuscript placement.
For an actual multi-stage project, read [stage-playbook.md](references/stage-playbook.md)
and [handoffs-and-state.md](references/handoffs-and-state.md); use
[portfolio-routing.md](references/portfolio-routing.md) for ownership. Read each
selected skill's actual instructions and required resources. Reuse current
valid evidence and existing records; do not rebuild completed work.

## Move the paper forward

1. **Recover the question and strongest known solution.** Use
   `mine-econometrics-ideas` for discovery and scientific comparison, reading its
   current entrypoint. Reuse candidate IDs, source locators, actual derivations,
   probes and rejection reasons; consume its records rather than create a second
   idea ledger. Recover the original target, information, assumptions, guarantee
   and reason the question matters. Before an investment recommendation, consume
   an actual attempt to solve that same problem with the strongest applicable
   result or combination of results, including its achieved scope and exact
   remaining obstacle. A list of related papers or failed title search is not
   this comparison. `paper-lookup`, `citation-management` and `deepread` supply
   the exact source evidence needed by the idea specialist. Reopen only stale or
   material gaps for an already selected mature idea.
   For novelty-sensitive work, several candidates, a long/resumed search, or an
   autonomous run, read [search-and-portfolio-control.md](references/search-and-portfolio-control.md).
   Bind the existing idea record to its optional controller sidecar and use
   `scripts/idea_portfolio.py`; do not copy the scientific argument into a second
   ledger. The controller exposes candidate diversity, actual probes, search
   frontiers, stop reasons and reopen conditions but never certifies novelty.
2. **Develop and test a contribution from the remaining obstacle.** Let the
   idea specialist develop materially different mechanisms and run the cheapest
   decisive derivation, construction, counterexample or diagnostic for each
   promising route. Literature reconstruction and mechanism development iterate:
   a new mechanism may expose a stronger comparison, whose failure or success
   changes the next mechanism. Preserve the original target and make any change
   of information, assumptions or guarantees explicit. Bounded work on a hard
   load-bearing bridge is justified before the whole theorem is closed. Before
   recommending substantial investment, assess the actual increment beyond the
   reconstructed solution and why it matters, separately from correctness and
   feasibility, using [strategic-review.md](references/strategic-review.md).
   When the scope requires independent value assessment, consume the idea
   specialist's existing assessment rather than repeat it as a second panel.
   Preserve the first investment judgment and
   its evidence in the existing record so later changes can be explained.
   If the comparison defeats a route, use its exact obstruction to guide a new
   route or move on; a renamed or narrowed claim does not inherit the old verdict.
3. **Freeze the supported research design.** Select a route for substantial
   proof, production compute or manuscript expansion only after the preceding
   comparison, decisive probe and contribution judgment support that commitment.
   An unresolved discovery task can continue bounded exploration without a
   selected paper. Choose the claim and paper spine; establish
   identifying assumptions, proof obligations, data availability, computation
   needs, benchmarks, failure criteria, and evidence required for each claim.
   Before expanding the outline, recover the contribution hierarchy from current
   author decisions and verified nearest neighbors using the writer's
   `references/reader-facing-writing.md`; keep unresolved comparisons explicit.
   Specify exploratory versus confirmatory work before examining outcomes. For repeated preliminary probes, read [exploration-loop.md](references/exploration-loop.md); preserve baseline, actual costs, failed attempts and decisions.
   For a long, costly, parallel, multi-provider or autonomous run, also read
   [research-operations.md](references/research-operations.md) and use the
   append-only operations log. Keep unknown resource measures null; aggregate
   operational state without moving scientific truth out of specialist records.
   For a long, multi-stage, autonomous, or explicitly token-sensitive project,
   also read [token-efficiency.md](references/token-efficiency.md). Reduce work
   losslessly before considering compression, protect scientific objects, and
   require a frozen paired evaluation before claiming quality-preserving token
   savings.
4. **Develop the required evidence.** Use
   `prove-econometrics-theory-v2` for theory,
   [empirical-bridge.md](references/empirical-bridge.md) for real-data design and
   execution, and `audit-numerical-simulations-v2` for Monte Carlo design,
   implementation, validation, and eventual production results. Revisit strategy
   when material evidence changes the contribution case or a bounded phase fails
   to reduce its main uncertainty; do not default to another local repair. A proof gap
   blocks only its dependents; it does not prevent verified unrelated work.
   For theory-bearing cross-skill handoffs, use the bounded
   [proof lineage](references/proof-lineage.md) interface. A hash-valid lineage
   projection describes state and cannot certify the proof.
   For a theory-bearing revision, apply the theory revision contract before
   changing the manuscript: audit assumption strength against exact sources,
   preserve null/fixed/local and other scope boundaries, and do not generalize a
   learner-specific result to an unspecified method class.
   Separate a conditional theorem, verified source interface, concrete-model
   verification, and actual implementation coverage in the existing handoff.
   An implementation sentence is not an asymptotic assumption; recover its
   exact wording before proposing new grid, solver, or resampling theory.
   For manuscript-bearing empirical results, validate the hash-bound adapter,
   known-answer fixture, inference settings, diagnostics, output and
   interpretation ceiling with `scripts/empirical_contract.py`; a green
   structural contract does not establish identification.
   For a changed empirical outcome/window or dependence correction, apply the
   bridge's timing and inference-applicability check before using the new result;
   a request not to add a theory section does not validate an inference method.
   Independent branches may run in parallel in ordinary development. During
   item-by-item optimization, any delegated work must serve the same active issue;
   leave independent optimization items queued until their turn.
   When a simulation or other offline job is running, do not spend model turns
   polling it. Persist the actual process/job handle and wait. Suspend every
   result-dependent action; continue only work that remains valid under every
   plausible result. The wait barrier and dependency edges are recorded with
   `research-operation-event.v2` as described in the token and operations
   references.
5. **Compose the manuscript as evidence matures.** Use
   `write-econometrics-paper-v3`. For the first complete author-facing draft,
   open the writer's `references/first-draft-review.md` before outlining.
   Recover applicable author feedback and make the checks part of drafting and
   verification rather than waiting for submission or the author's first review.
   Begin useful setup and literature prose early,
   then write verified results and appendices, and finally reconcile abstract,
   introduction, title, and conclusion with delivered evidence. Drafting is
   allowed while evidence is pending; completing result-dependent claims is not.
   Use the writer's citation workflow at first adoption of a source, and its
   result/exhibit guidance before drafting captions or analysis. Contribution
   priority changes also reach simulation and empirical narrative, not just the
   abstract; preserve existing valid results and actual analysis chronology.
   For English methods/theory writing and full reader-facing proofs, apply
   [manuscript-handoff.md](references/manuscript-handoff.md) and the current writer/
   renderer rules. Preserve the fixed science-to-style order, applicable source
   cards, protected mathematical meaning, terminology and evidence ceilings.
   Main-text goal, route and key proof bridges remain recoverable; technical
   closure remains available in text or appendices. Internal audit detail stays
   separate from reader-facing prose. Do not create unrequested output formats
   or treat a clean token check as semantic verification.
6. **Reproduce and challenge.** Check data-to-table/code-to-theorem alignment,
   citations, numbers, assumptions, builds, rendered pages, and the reader-facing
   hierarchy. Before handing over the first complete draft, use the writer's
   first-draft review on the actual version to repair in-scope recurring issues
   and record any genuine evidence gaps in the existing project records.
   Confirm that the main text itself exposes the applicable problem,
   decisive insight, principal result and interpretation, and that auxiliary
   implementation or closure has not displaced them. Obtain fresh
   independent review; turn each supported finding into a bounded repair and
   verification task. Keep rejected findings with reasons. For a material
   revision, compare the current candidate with the frozen baseline against the
   primary objectives, protected scientific invariants, bounded trade-offs, and
   whole-candidate dimensions before treating the change as retained.
7. **Package and support revision.** Deliver manuscript source and rendered
   PDF, bibliography, appendices, reproducibility instructions, result provenance,
   limitations, and journal-specific materials. For material R&R re-review, use [evidence-first-review.md](references/evidence-first-review.md) to freeze criteria and assess manuscript evidence before revealing the response letter. Map every comment to
   evidence, edits, affected claims, and a verified response. Actual submission
   or external communication requires the user's instruction.

These are dependencies, not a rule to restart at step one. Resume at the earliest
stale or unfinished requirement and continue unaffected branches. Do not promise
that any arbitrary idea admits a new theorem or publishable conclusion; record
a falsified idea or infeasible design and develop a reviewable alternative.

## Mentor supervision and independent roles

Preserve explicitly requested mentor, roundtable, and review invocations and
authorizations across the active task. Do not interpret this workflow's name as
a literal invocation of an explicit-only component. For the optional governed
profile, use `research-mentor-supervisor`: its G1 covers the research contract,
G2 covers the first load-bearing candidate before expensive downstream work,
and G3 covers the exact scoped delivery. Run its own state tool and gates.
Mentor selection, evidence readiness, private-source boundaries, and any bounded
roundtable are owned by those skills. Read their actual instructions.

For ordinary end-to-end work, an independent generic reviewer can challenge the
design and final candidate without invoking a named mentor. When the user
authorizes `review-paper`, `review-paper-code`, or `audit-analysis`, use those
specialized reviews in their applicable scope. See the runnable prompt profiles
in [usage-profiles.md](references/usage-profiles.md).

Give reviewers the claim, exact artifacts and evidence, not the desired verdict.
For first-pass judgment versus checking a repair, use the scoped review guidance
in [goal-and-learning.md](references/goal-and-learning.md); a fresh assessment
does not erase unresolved findings, and a persuasive reply does not close them.
Use fresh contexts for final scientific checks. Batch parallel reviews within
available capacity; several roles in one worker are not independent reviewers.
Do not stack an eight-role review, three-mentor roundtable, and supervisor at
every step. Escalate a concrete unresolved question only when it warrants it.

## Handle incomplete simulations honestly

`deferred` applies to production computation, not to the entire simulation
branch. Complete the design, runnable implementation where feasible, tests,
resource estimate, frozen run instructions, expected result schema, resume
procedure, and table-generation interface. Report any part that remains blocked.
Never insert fabricated measurements or use pilot results as confirmatory ones.

Bind a compute estimate to the full requested experiment inventory, including
expensive learners, reusable completed cells, missing cells and invalidated cells
that need reruns. A reduced option is a separate scope, not completion of the
original inventory. Consume the simulation skill's timing and precision evidence.

Keep simulation-dependent sentences and exhibits explicitly pending. Deliver a
coherent manuscript covering verified theory, literature and real-data evidence,
plus a separately identified simulation handoff. The available outcome is
`manuscript-ready-except-simulations`, not `submission-candidate`. When production
results arrive, validate their versions and actual replication records, rebuild
exhibits, update affected claims, rerun independent review and final packaging.

## Persist progress without duplicating scientific truth

The writer's `.paper/` files own claims, citations, exhibits, and author locks.
Proof ledgers, simulation manifests, and `.research-supervision/` retain their
own authority. Use `.paper/workflow/` only for the orchestration plan and
hash-bound stage receipts pointing to those artifacts. An existing equivalent
workflow store may be adapted instead; do not overwrite it.

For qualifying long-running work, the optional operations log under the same
directory owns only execution telemetry and blockers. For qualifying idea work,
the project-local portfolio sidecar owns only candidate/search control and binds
the authoritative idea record. Neither store may duplicate or override claims,
source judgments, proofs, results, reviews or author decisions. At resume, check
their current status before repeating searches, probes or provider calls.
The optional token evaluation is likewise derived control evidence: it binds a
frozen task/rubric, protected checks, observed usage, and paired evidence. It
does not become a second scientific ledger or weaken any specialist gate.

The bundled `scripts/workflow_state.py` supports `init`, `record`, and `status`.
Mutations preview by default and need `--write`. It derives readiness from exact
artifacts, checks, and current prerequisite receipts. It does not certify
mathematics or infer that a reviewer really inspected a file. Human-readable
review evidence and specialist verification remain necessary. See
[handoffs-and-state.md](references/handoffs-and-state.md) for commands and scope.
For cross-skill contracts that need current file or explicit fragment checks,
use [content-bindings.md](references/content-bindings.md). Reuse the existing
object/artifact IDs and dependency graph; do not refresh a hash to conceal an
unreviewed version change.

For an explicitly activated continuous-revision cycle,
`scripts/revision_cycle.py` previews `init`, `add`, `select`, `transition`,
`review`, and `sync` mutations unless `--write` is supplied. Its status can
establish controller convergence only; it cannot certify a theorem, result,
source claim or reviewer independence. The v2 controller validates current
evidence hashes and the frozen non-regression decision, but the report's
substantive judgments still require specialist evidence and independent review.
Do not use its state as scientific evidence or bypass specialist release
contracts.

## Deliver the actual requested scope

For a time-bounded, artifact-scored, or externally evaluated task, begin by
reading the request and enumerating its exact required files and checks. Write
the required artifacts as soon as the needed evidence is available, validate
them directly, and preserve partial progress before optional exploration. Reuse
unchanged valid receipts. Do not run Git status or history commands in a
workspace that has no repository metadata.

With a deadline, prioritize the required artifacts, decisive evidence and direct
checks before optional expansion, reserving enough time for repair and delivery.
Choose the schedule from the actual task; no universal third-by-third template
or additional audit is required. Do not withhold valid scoped deliverables for
unrelated optional checks, and do not drop required evidence to meet the clock.

For a resume task, resolve the active pointer, verify the declared active-state
bindings and inspect the lock semantics, then write the requested resume
artifacts before opening large claim, citation, exhibit, or revision registries.
Read those registries only when a required output field remains unresolved.

Once the required artifacts exist and their direct checks pass, produce the
final response promptly. Run larger project audits or dependency test suites
only when the request calls for them, the implementation changed, a direct
check failed, or a material uncertainty remains. Reserve enough of the stated
time limit to serialize final artifacts and return a response; a broader clean
check must not turn an otherwise complete scoped delivery into a timeout.

In a deliberately partial resume workspace, absence of an artifact that is not
part of the authoritative active-state binding is an availability limit for
fresh reinspection. It does not by itself reopen completed work or create a new
freshness gate. Reopen a stage only when the active status records it as open,
a required dependency is incomplete, or a bound current artifact is missing or
has the wrong hash. Future submission-package files do not become prerequisites
for the current recorded next action merely because they are absent.

Lead with completed work, remaining scientific blockers, and next action.
Distinguish draft, simulation-deferred manuscript, and submission candidate.
Report actual tests and external checks, not proposed checks. An empirical-only
paper need not invent a theorem, a theory paper need not invent an application,
and unavailable optional tools should not block unrelated progress.

For the dated GitHub comparison and adopted mechanisms, read
[upstream-evidence.md](references/upstream-evidence.md). Stars prioritize source
inspection; they are not evidence of scientific correctness or novelty.
