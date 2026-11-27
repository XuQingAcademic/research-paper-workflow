# Stage playbook

Read only the stages relevant to the active paper. Evidence is assessed on the
actual claim, not by a score or the number of populated template fields.

For a bounded artifact-scored stage, divide the stated time into delivery,
evidence, and finalization phases. All required files and schema fields exist by
the end of the first phase; decisive evidence is bound by the end of the second;
the last phase permits only targeted repairs and direct output checks. Do not
start broad optional audits during finalization.

## Problem, known solution, and candidate development

Use `mine-econometrics-ideas` for scientific discovery and comparison. It owns
the detailed work; this workflow consumes its existing record (default
`research/idea-mining.md`; preserve existing names), candidate IDs, source
versions, derivations, probes and decisions. An idea-only request ends at its
proposal scope; an end-to-end request carries those same objects into design.

Recover the original question, information available, target guarantee and why
the unresolved result would matter. Before treating a candidate as worth a full
paper investment, consume the specialist's actual attempt to solve this same
problem with the strongest known results, including applicable combinations.
Read the cited theorem/equation/code locators and the achieved scope,
not merely the comparison table's conclusion. This identifies the specific
obstacle left by existing knowledge and prevents an omitted standard solution
from becoming the proposed contribution.

Develop mechanisms from those obstacles, using the idea specialist's discovery
loop. When independent agents help, give each the problem and source evidence,
not a favored mechanism or requested verdict. Alternatives may challenge the
same obstacle through different constructions, information use or proof ideas.
Compare their actual increments and costs. Source comparison continues during
this work whenever a new route changes the relevant neighbors or equivalences.
Do not wait for a chosen idea before doing decisive literature work.

Consume an actual probe of the central bridge: a derivation, witness,
counterexample, small diagnostic or other scope-appropriate evidence. Record
what it establishes and what remains unknown. Full theorem closure is not a
prerequisite for bounded discovery. If a route is covered, inspect the reduction
for a useful unresolved boundary; a failure is information for further discovery,
not a requirement to manufacture a salvaged candidate.

The research brief links the known solution, remaining obstacle, actual new
mechanism, probe and assessment of the remaining contribution's value. Reuse an
independent assessment when it is required or already available; bounded
discovery does not require a new review panel. A theory result can matter by resolving a consequential uncertainty,
separating regimes, exposing a sharp limit or changing what can be identified or
proved; it need not invent an application or real-model experiment. Explain why
the particular increment has that value. Correctness, unfamiliar notation and
proof length are not evidence of importance.

Deliver the brief with the justified next commitment: further bounded discovery,
development of a supported candidate, or a reason no current route merits that
investment. No chosen working idea is mandatory. Preserve the first investment
judgment, support and open conditions in the existing record; later revisions
retain the original target and explain what changed. A narrower claim receives
its own value judgment rather than inheriting the original recommendation.

## Source evidence throughout discovery

Use `paper-lookup` for reproducible discovery and citation chaining, and
`citation-management` for deduplication/metadata. `deepread` reconstructs a source
argument; `pdf` assists when layout or equations require page inspection.
Zotero participates when the user uses their library; it is not a required
storage backend for every project. Use Deep research only if explicitly asked.

Maintain search date, queries, repositories/databases, inclusion decisions,
preprint/journal/supplement identities, and partial access. Use several targeted
queries and forward/backward citation chains. Reopen the exact source for every
claim-bearing citation. If full text is unavailable, separate what the abstract
actually establishes from what remains unknown.

For a bounded supplied corpus or registry, make a candidate census before writing
the synthesis: list every plausibly relevant record, its available evidence and
the role it might play. Answer both the relationship named in the request and
the corpus-nearest-neighbor question. Full text for one named paper does not
justify omitting a closer record whose supplied abstract, metadata or locators
already establish a more direct overlap. Record why each plausible candidate was
selected, distinguished, or left unresolved.

Reuse the idea specialist's source comparison and construction records; create
`research/nearest-neighbors.md` only if no equivalent record exists. Preserve
the aligned question, information, assumptions, guarantees and costs, exact
source versions and locators, and what the reconstructed solution actually
delivers. The idea specialist owns implication, equivalence and composition
checks. Missing decisive source evidence calls for a targeted retrieval or a
bounded unresolved comparison; negative search never proves global absence.
Use the writer's novelty contract when turning these results into paper prose,
without creating another comparison table or numeric novelty score.

Deliver verified bibliography, source map, nearest-neighbor comparison, and a
literature synthesis that leads to the actual research question.

## Design freeze

Consume the discovery comparison, actual central probe and contribution
assessment before a substantial commitment. Use
[strategic-review.md](strategic-review.md) in these same notes to decide the
investment, reusing an applicable independent assessment rather than adding a
panel. Freeze the author objective separately from the provisional route and
state the evidence that would change the next phase's decision. Revisit when
material evidence changes the case or that phase is uninformative; do not defer
the first serious comparison until after design freeze.

Write `research/design.md`: paper spine (question, friction, move, guarantee,
value), intended claims, nonclaims, assumptions, proof obligations, data sample
construction, inference, benchmarks, planned exhibits, and decision criteria.
Bind each intended claim to the evidence that would establish or reject it.

Before expanding the outline, use the writer's contribution-hierarchy check in
`references/reader-facing-writing.md`: recover primary/secondary results,
inherited versus new work, nearest-neighbor differences, and the general
framework versus verified implementation examples. Reuse current author choices;
record unresolved scientific comparisons without inventing a contribution. Keep
this in the existing design/spine notes, not a second contribution registry.

For empirical work freeze a pre-analysis specification before outcome-driven
choices; exploratory analyses remain possible but must be labeled and versioned.
If preregistration is requested, prepare its concrete document; do not claim
that a local plan was externally registered. Check actual access restrictions
and ethics requirements of the chosen data when applicable.

For methods, separate mathematical correctness, computational approximation,
finite-sample calibration, and substantive usefulness. Feasibility checks should
precede a large proof/programming investment. A supervisor G1, if selected,
reviews this contract before research mutations; an idea's exploratory notes can
be the inputs to a new supervised contract.

Deliver design, assumption/identification map, evidence plan, and acceptance
criteria. Revisions create a recorded design delta and reopen only dependents.
For a material revision cycle, freeze the project-specific meaning of a positive
change using [non-regression-contract.md](non-regression-contract.md): primary
objectives, protected scientific invariants, bounded trade-offs, paired evidence,
rollback conditions, and applicable whole-candidate review dimensions.

## Theory branch

Use `prove-econometrics-theory-v2` and its required workflow. Freeze statement
and assumptions; define the estimand, rates, index, conditioning, and topology;
look for cheap counterexamples; decompose into obligations; prove and independently
review. An auxiliary lemma failure does not automatically refute the theorem.
Numerical non-rejection of a counterexample search is not proof.

Deliver exact LaTeX/Markdown assumptions, theorems, complete proofs, obligation
ledger, source locators, known boundaries, review findings, and the immutable
proof-to-simulation/writing handoff. A result can enter prose only at the
specialist's verified scope. A gap can remain visible in a draft but cannot be
recorded as a ready theory stage.

## Empirical branch

Follow [empirical-bridge.md](empirical-bridge.md), preserving the existing
language and packages. Default new implementations to Python when suitable.
Keep immutable raw data, explicit sample construction, executable analysis, a
data dictionary, failed checks, and reproducible generated tables. Distinguish
real-world data evidence from Monte Carlo evidence.

Deliver data provenance, sample/variable construction, design and inference
justification, analysis code and environment, actual outputs with uncertainty,
robustness/diagnostics, paper-code mapping, and interpretation at the justified
scope. If data are inaccessible, continue theory and writing that do not depend
on them, but do not mark the empirical stage ready.

## Simulation preparation and execution

Use `audit-numerical-simulations-v2`. Preparation includes a theorem-to-cell
map, ADEMP+R plan, comparisons and actual target metrics, deterministic RNG,
failure handling, per-replication schema, buildable code, tests, bounded pilot,
resource measurement and run/resume commands. Do not silently translate
`simulation deferred` to `simulation omitted`.

The handoff `simulation/HANDOFF.md` must name code/config versions, environment,
expected IDs, output schema, checksum and resume validation, MCSE target,
diagnostic versus confirmatory outputs, wall time/memory estimate, stop criteria,
the exact command to start, and how to regenerate tables after results arrive.
If a pilot cannot run, record why and which preparation is still unverified.

Production evidence requires actual valid IDs/R/B, raw outputs, failure lineage,
calibration, MC uncertainty, and independent representative checks. A large R
does not repair invalid size or data leakage. A computation request is a
separate resource decision only when it exceeds the user's existing authority
or available resources; do not ask again for authorized bounded work.

On return, check raw results against frozen code/config before importing them.
Do not replace a missing result with an expected value. Rebuild exhibits and
claims, then verification, review and packaging on the actual current candidate.

## Manuscript and exhibits

Use `write-econometrics-paper-v3` as the owner of `.paper/`, claims, citations,
exhibits, terminology and author decisions. Draft setup/literature while results
develop. Then write supported methods/results, complete appendices, limitations,
and interpretation; rebuild abstract/introduction/title/conclusion last.

For the first complete draft, use the writer's
`references/first-draft-review.md` when preparing the outline, accepting
specialist handoffs and reviewing the assembled manuscript. Apply the same
checks to the affected content after a substantive manuscript revision.
Recover accepted feedback from the current project and its author locks.
Use the existing verification and review stages for the resulting checks.
Some scientific work may remain deferred within the author's chosen scope.

An explicitly requested de-AI prose pass uses the installed `humanizer` through
the writer's academic profile after claim-bearing content is stable. It removes
formulaic staging and cadence while retaining formal register, fixed terminology,
equations, quantifiers, numbers, citations, uncertainty and evidence ceilings.
It is a prose edit, not an authorship detector or a scientific review.

Make numbers and tables generated outputs when possible. Scientific figures use
standard plotting tools and retained source data. Image generation is suitable
for a conceptual illustration only if requested/useful, never for inventing a
scientific plot or experimental evidence. Use document/slides/spreadsheet skills
for those actual output formats; do not convert a LaTeX project unnecessarily.

Before interpreting exhibits, use the writer's Monte Carlo and figure guidance
in `references/econometrics-writing-playbook.md`. Select the main patterns and
the evidence changing their interpretation; do not narrate every cell or label
an uncalibrated rejection difference a power advantage. Carry plot transformations
and their interpretation ceiling into the caption and surrounding prose.

For deferred simulations, mark all pending result cells and sentences in the
working state. Use an explicit pending section in the internal manuscript and a
separate simulation handoff; do not hide the absence from the abstract or final
delivery status. Verified theoretical statements need not be weakened because
an unrelated diagnostic simulation is pending.

## Verification, independent review, and repair

Run appropriate specialist validators and retain their outputs alongside actual
scientific evidence. Build the manuscript with the existing toolchain; inspect
the PDF where visual layout matters. Check cross-file references, citations,
numerals, appendix coverage, figure paths, and table-to-code provenance.
For a first draft, bind the result of the applicable checks to the draft and
the artifacts actually delivered. An internal partial draft may be delivered
with precise remaining work. Author review of a complete scoped draft does
not require a submission package or submission approval.

Independent reviewers inspect the frozen claim and current artifacts without
the worker's desired verdict. Use a generic fresh reviewer when named review
skills were not selected. If explicitly authorized, `review-paper` contributes
economics referee roles, `review-paper-code` checks reproducibility and mapping,
and `audit-analysis` reviews a valid Git diff. Batch eight-role reviews within
available capacity; never invent a Git base or manufacture independence.

Save findings with locator, severity, evidence, minimum action and a test of
closure. Repair accepted findings; reject unsupported findings with evidence;
independently verify material repairs. No claim becomes stronger just because a
reviewer voted for it. Serious unresolved objections prevent final eligibility.

For a material iterative cycle, compare the candidate with the frozen baseline
under the same criteria. Check that required objectives improved, affected
scientific invariants were preserved, permitted trade-offs stayed within bounds,
and paired evidence is current. Then review the assembled manuscript across the
frozen whole-candidate dimensions. Local passes do not establish a positive
combined revision when their interaction creates a new regression.

Freeze a new candidate after material edits. A receipt for the old version
cannot approve the new one. An ordinary revision cycle can continue as needed
under the user's request; if governed by the supervisor, honor its bounded
gate/roundtable contract and create the required superseding task when necessary.

## Package, submission, R&R, and communication

For a submission candidate deliver current manuscript and compiled PDF,
bibliography, full appendices, code/config/environment, reproducibility commands,
data availability and provenance, required declarations, and any requested
cover letter. Verify the target journal's current official requirements before
asserting compliance; an overlay in memory is not a current policy source.

Save `delivery/STATUS.md` stating what is complete, what remains, the exact
candidate, unresolved scientific limitations, and what actions the author must
take. Paper-workflow readiness never implies actual submission or acceptance.
For simulation-deferred delivery the package explicitly excludes a submission
claim and includes runnable simulation preparation.

R&R reuses `write-econometrics-paper-v3` and its referee protocol: keep the
original comment, decision, supporting evidence, changes and locations,
verification, and response text. Update downstream claims and artifacts before
writing that an issue was resolved. Presentation and dissemination are optional
follow-ons: `presentations`, `documents`, `sites`, and `visualize` may turn verified
results into appropriate outputs. External publishing remains a separate action.

## Modified manuscript coverage

When the paper writer changes result-bearing prose in a managed project, use its `claim_coverage.py` on the affected manuscript paths. Carry unresolved candidate locations into the existing findings/claims work; never turn a clean lexical scan into full semantic coverage or duplicate the claim ledger.

## Resuming candidate exploration

Use the idea specialist's existing candidate IDs and `reopen_if` notes. Read the original rejected claim, source version and reason before generating a similarly named idea. Reopen only comparisons affected by actual new evidence or substantive changes; author interest can authorize rechecking but cannot establish novelty. Link real variants to their predecessors and keep unaffected findings. For bounded repeated probes use [exploration-loop.md](exploration-loop.md).

For material re-review, follow [evidence-first-review.md](evidence-first-review.md). Preserve existing issue IDs and closure records; the staged packet is only a derived input boundary.
