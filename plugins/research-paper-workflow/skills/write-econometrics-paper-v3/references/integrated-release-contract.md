# Integrated research release contract

Use this contract when a theorem, simulation result, citation, manuscript sentence, table, or rendered artifact crosses skill boundaries or is considered for release. It governs traceability and eligibility; it does not establish mathematical truth, novelty, or external validity.

## 1. Identity and version registry

Every scientific object has an immutable, typed identity:

```text
object_id
object_type
schema_version
content_version
content_hash
scope_hash
status: active | superseded | withdrawn
supersedes
```

Names, theorem numbers, labels, DOI strings, citation keys, and table captions are display aliases. They never prove identity or equivalence.

A cross-skill foreign key must pass both:

1. referential integrity: the target object/version exists;
2. semantic integrity: null, estimand, population, conditioning, index, norm, process layer, critical law, algorithm role, and conclusion type agree.

Version transfer requires an explicit comparison map. Unknown fields make transfer not evaluable. A successor publication, matching title, or stable citation key is not a transfer receipt.

## 2. Claim-state product

For every required claim, record only applicable components:

```text
source_truth
version_coverage
proof_truth
proof_scope_coverage
project_applicability
implementation_reproducibility
simulation_inference_eligibility
citation_novelty_coverage
artifact_lineage_freshness
manuscript_wording_eligibility
```

Use these state semantics:

- `PASS`: the applicable predicate is verified for the exact object/version.
- `PARTIAL`: evidence is incomplete; descendants are `not_evaluable`.
- `FAIL`: a verified mismatch, implementation breach, or eligibility failure exists. It does not automatically make theorem truth false.
- `CONTRADICTED`: a proof or counterexample matches the exact object, version, assumptions, quantifiers, index, norm, and conclusion and establishes falsehood.
- `NOT_APPLICABLE`: the certificate does not govern this claim. This is not `PARTIAL`.

Missing assumptions, an unverified continuum bridge, incomplete dependence transfer, or a partial source receipt is `PARTIAL`, not `CONTRADICTED`. A DGP outside the theorem domain is an assumption-domain failure, not a counterexample.

## 3. Errors, blockers, ownership, and propagation

- `root_errors` contain verified mismatches or violations.
- `coverage_blockers` contain unknown or incomplete evidence.
- `not_evaluable` contains descendants whose prerequisite is a blocker or failed root.
- Every root has one owner certificate and any number of typed consumers.
- Propagate only over registered dependency edges.
- Preserve exact affected claim/artifact IDs; do not replace root errors with cascaded duplicates.

Test both directions:

- a missing edge must produce a missed-propagation or false-clean failure;
- a spurious edge must produce an overbroad-propagation or false-red failure.

An unrelated diagnostic cell must not invalidate an independently supported theorem or sentence. Once a required sentence uses that cell, the dependency becomes real and its state contributes to the sentence-level meet.

## 4. Source, locator, and citation eligibility

Track source work identity separately from source version and artifact role:

```text
work_id
version_id
artifact_role: preprint | journal-main | supplement | accepted-manuscript
content_hash
reading_status
exact_locator
claim_scope
project_applicability
```

Reading depth, locator precision, project applicability, and cross-material synthesis are separate axes. A supplement proof cannot supply missing main-text assumptions. A fixed-consistency locator cannot support local power.

Cross-material synthesis:

- requires at least two distinct canonical sources;
- is labelled as synthesis rather than attributed to one source;
- inherits the weakest required input;
- cannot repair missing technical coverage.

Source truth can remain valid while the current project sentence is ineligible or the rendered citation is stale.

## 5. Novelty and negative search

Absolute absence is generally not established by search. Freeze:

```text
object_coordinates
search_universe
databases_and_catalogs
queries
languages_and_date_range
cutoff_date
version_deduplication
citation_chaining
inclusion_exclusion
nearest_neighbor_matrix
unresolved_candidates
```

Word ceilings:

- unresolved high-relevance candidate: describe the present object only;
- replayable but open-world search: “we did not identify … in the sources screened”;
- full nearest-neighbor comparison with a locator-supported difference: “differs from” or “extends”;
- “first/unique” only within an explicitly closed universe whose candidates are all resolved.

Simulation performance never proves novelty. Search updates stale only claims with a typed negative-search dependency.

## 6. Proof–simulation–writing handoffs

Proof outputs an immutable obligation bundle:

- theorem object/version and statement/assumption hashes;
- null, alternatives, population, conditioning, index and norm;
- pointwise/grid/continuum scope;
- nuisance rates, derivatives, projections and blind sets;
- dependence/filtration and resampling requirements;
- fixed/local-power family, rate, sign, and comparison scope;
- required boundary, ablation, and stress cells;
- unknown obligations and wording ceiling.

Simulation returns a cell certificate:

- method-specific null and DGP truth;
- diagnostic or confirmatory role and phase;
- config, code, RNG, fold, resampling, solver, and ledger versions;
- actual valid replication IDs, actual R/B, event definition, MCSE, failures;
- same-size and paired-comparison eligibility;
- maximum wording tier and stale status.

Writing binds each sentence to required and optional upstream claims. The sentence ceiling is the meet of its required dependencies, not a global minimum over unrelated artifacts.

Writing feedback creates a new, append-only receipt. A semantic change to quantifier, scope, assumption, formula object, source version, or citation role supersedes the old object and reopens actual descendants. A presentation-only change refreshes render status without reopening proof.

## 7. Reproducibility and artifacts

Random streams derive from scientific identity, including config/RNG schema, phase, cell, replication, fold, resample, role, and draw ID. Worker number and completion order are excluded.

Checkpoint completion is an atomic, idempotent terminal payload with a stable ID and checksum. Resume runs only expected IDs missing from the valid terminal set. Partial payloads, duplicate IDs, late conflicting commits, and cross-config merges are roots.

Solver and retry policy are versioned method components. Preserve every attempt. Outcome-dependent retry, deleted failures, survivor-only inference, or a fallback that silently changes the method are roots.

Tables and prose are rebuildable views:

```text
code/config -> raw replication ledger -> validated result cells
-> table/figure query -> manuscript claims -> rendered PDF
```

Display-semantic errors, scientific-object mismatches, ledger drift, and stale rendering have different meanings and propagate over different edges.

## 8. Adversarial acceptance

When creating or changing a validator or release-state propagation workflow, its regression suite must include the cases below. Applying an unchanged validated workflow to new research artifacts requires checking those artifacts and affected dependencies; it does not require rebuilding or rerunning the entire validator suite without a relevant change or failure:

- `CLEAN`: all applicable predicates verified and no blockers;
- `SINGLE`: one root mutation, exact root, exact descendants;
- `COMPOSITE`: actual roots equal the canonical union of validated singles;
- `PARTIAL`: unknown evidence becomes blockers/not-evaluable, never pass or contradiction;
- `FALSE_CLEAN`: fields are populated but evidence is unverified, circular, low-tier, stale, or hash-mismatched;
- `FALSE_RED`: an unrelated object is deliberately connected and must not be invalidated.

Compare deterministic root ordering and exact stale/not-evaluable IDs. First-error short-circuiting is a failure.

## 9. Release vector

Use a vector rather than one ambiguous GO:

```text
schema_GO
source_GO
proof_GO
implementation_GO
simulation_GO
writing_GO
artifact_GO
scientific_GO
submission_GO
```

For each claim, evaluate only its applicable certificates and take their typed-dependency meet. Governance integrity, checksum, acceptance receipt, code reproducibility, and render freshness never upgrade proof truth, novelty, or external validity.

A lineage-complete diagnostic artifact may survive a scientific blocker only when it is explicitly quarantined, has no strong inferential/novelty wording, and is not a required dependency of the submission claim.

The final report must state what the gate establishes, unresolved uncertainty, and the external-validity scope. Never translate `governance_GO=true` into “the theorem is true,” “the method is first,” or “the result is generally valid.”
