# Theory revision and manuscript contract

Read this reference when an existing paper's assumptions, theorem statements,
proofs, notation, or theory exposition will change. It coordinates the proof
specialist and paper writer; it does not replace either one's scientific
judgment or records.

## Freeze the revision target

Before editing, recover and record in the project's existing revision notes:

- the active manuscript and proof versions;
- the maintained estimand, null or model, index domain, calibration, and target
  theorem scope;
- the branch to be changed, such as null, fixed alternative, local alternative,
  oracle, feasible, full-sample, split-sample, or cross-fitted;
- the exact author request and whether the present task is collect-only, plan,
  implement, or review;
- protected statements, evidence, code and results that are outside the change;
- any author-selected literature lineages and their priority for terminology or
  notation.

Honor a collect-first instruction: accumulate comments without editing until the
author requests implementation. Preserve the requested baseline; when the author
requires a separate candidate, never overwrite it. A proof or notation preference
learned from one project is project-local unless the author explicitly generalizes
it.

If the author asks to first explain, compare, or propose the workflow, treat the
current turn as plan-only: deliver the proposed actions and required evidence,
then stop before manuscript or proof edits. A later implementation request may
reuse that decision without asking for the same authorization again.

Classify a suspected defect from the original sentence before planning its
repair: scientific assumption, derived condition, maintained high-level input,
learner-specific sufficient condition, implementation choice, or explanation.
Do not infer a permanent asymptotic sequence from a finite implementation
setting. Distinguish condition repair, concrete-model verification and a new
theoretical extension; only the affected authorized work enters this revision.

## Keep verification and presentation separate but synchronized

Maintain two views of the same mathematical object.

**Verification view.** Preserve exact statements, quantifiers, conditioning,
topology, assumption-use locations, proof obligations, complete derivations,
external theorem interfaces, counterexamples, and known boundaries. A derivation
prepared for author checking does not skip a nontrivial step. “Standard” or
“similar to” is not a discharge unless the exact external result, inputs, and
output are identified and matched.

**Manuscript view.** Present only the mathematics a reader needs. Prefer
formula-led proofs with short transitions, assumption or lemma references, and
reasons for non-obvious steps. Keep theorem environments to their mathematical
scope and conclusion; place intuition and limitations immediately outside.
Ordinarily keep core results in the main text and let the appendix enter the
assumptions, lemmas, propositions, theorems and proofs directly. Remove tutorial
material, proof-route diagrams, “role of this theorem” headings, repetitive
remarks, and explanations of conventions the target readership can reasonably
be expected to know.

For each full reader-facing proof, classify the presentation into `goal`,
`route`, `key bridges`, and `technical closure`. The main text must retain the
first three, although a key bridge may use a precise cross-reference when the
same object and scope have already been established. Technical closure may move
to the appendix but may not be deleted. Keep closure in the main text when it
contains a novel idea, a nonstandard condition, a scope change, or a step needed
to understand the result. This separation governs reader attention; it does not
alter the verification view or authorize weaker mathematics.

At section or paper level, reverse-outline paragraphs against the reader-facing
question, insight, principal result and interpretation. Main-text implementation
detail must be necessary for understanding, reproduction or interpretation;
otherwise move it to the appendix or footnote. Remove duplicated caveats and
process history. Judge the resulting hierarchy semantically rather than by a
fixed word-share target.

Concise does not mean incomplete. Do not remove a quantifier, scope condition,
probability law, topology, positivity condition, proof bridge, or citation merely
to shorten the paper. The complete verification view remains available for audit
even when the manuscript view compresses routine steps.

After every material change, confirm that the statement, proof, main-text
interpretation, appendix, abstract-level claim, and any proof-to-simulation or
proof-to-writing handoff refer to the same object and version.

## Govern assumptions with evidence

For each assumption that is added, weakened, strengthened, or removed, establish:

1. its exact use in the proof and which downstream results consume it;
2. whether it is primitive, high-level, learner-specific, or only an exposition
   convention;
3. the closest verified literature conditions and exact source locators;
4. whether the proposed condition is weaker, stronger, or incomparable, and on
   which dimensions;
5. the additional models admitted or excluded and the proof cost of the change;
6. the replacement derivation, counterexample, or explicit reason for retaining
   the original condition.

Do not weaken a condition merely because generality sounds preferable. A weaker
replacement is retained only after every affected obligation, bootstrap or
calibration result, and downstream claim is checked. Conversely, do not retain a
convenient strong condition without noting its scope when verified neighboring
work uses a materially more general route.

Prefer primitive, verifiable conditions when the proof can establish the needed
limit. A high-level interface remains acceptable when it protects genuine
generality or depends on a future learner-specific analysis, but label it and do
not describe its conclusion as derived from weaker primitives. A specific fixed
dictionary, series construction, or learner corollary never establishes validity
for an unspecified nonparametric or machine-learning class.

Use the proof specialist's assumption audit at its point of use: check exact
proof use, the actual domain needed, and compatibility with representative
models the paper claims to cover. Compare complete condition packages, not an
isolated weaker inequality. Removing unused strength requires a replacement
argument; a model excluded by a declared condition is not a counterexample to
the conditional theorem. No general minimal-assumption claim follows from
these checks.

## Preserve branch and scope boundaries

Audit separately whenever applicable:

- null, fixed-alternative, and local-alternative laws;
- exact, near, and absent orthogonality;
- pointwise and uniform statements;
- compact-index, trimmed, retained-domain, and global claims;
- oracle and feasible processes;
- deterministic and estimated grids, cutoffs, or tuning parameters;
- full-sample, split-sample, and cross-fitted implementations;
- each learner class covered by a claimed sufficient condition.

If the author selects one proof route, remove superseded route-specific
assumptions, lemmas, corollaries and citations only where they are no longer
used by retained results. Keep failed alternatives in the audit record. This
does not authorize deleting scientifically distinct result branches.

Never transfer an assumption relaxation or proof from one branch to another
without establishing the bridge. State orthogonality at the distribution and
nuisance value where its derivative is zero; cross-fitting does not itself create
orthogonality. Restrict consistency and power language to the domain and
directions actually covered. A compact or trimmed test is not automatically
omnibus on the full support.

## Govern notation, terminology, and citations

When the author specifies reference authors or papers, freeze a project-level
priority order. Build a small semantic map from each maintained mathematical
object to the selected notation and source locator before performing a global
rename. Use the highest-priority verified source that contains the corresponding
object; fall back to the next source only when necessary. Check the main text,
assumptions, results, proofs, figures, tables, and supplements for the same
meaning after the change.

Prefer the established term used by the closest verified literature. Do not coin
compound labels to make a familiar argument sound new. If no standard term fits,
use a descriptive phrase or follow the writer's author-defined-term protocol.
Verify that every claim-bearing citation supports the attributed object, result,
and scope; matching authors and metadata alone is insufficient.

The writer checks nearby interpretation as scientific content: what condition
or decomposition does, which object converges, and in what norm and direction.
Stronger wording, even with unchanged formulas, is a scientific edit. In the
existing handoff distinguish an exact external tool, background precedent and
the paper's own adaptation; source identity cannot discharge project inputs.

## Accept or reject the candidate

Bind the revision to the current project's
[non-regression contract](non-regression-contract.md). For a material theory
change, protect at least:

- the maintained scientific object and theorem scope;
- all retained proof obligations and known boundary cases;
- calibration or bootstrap validity where applicable;
- claim strength and citation fidelity;
- notation semantics and manuscript-proof congruence;
- unaffected simulation, empirical, and reproducibility evidence.

Compare the baseline and candidate under the same criteria. Required evidence is
proportional to the change, but usually includes the affected statement/proof
diff, assumption-use comparison, source verification, downstream dependency
check, build, and affected-page inspection. A build proves syntax and layout, not
mathematics. Obtain a fresh independent theory review for a material mathematical
change; give the reviewer the claim and artifacts, not the desired verdict.

Retain the candidate only when its declared objective improved, protected
invariants remain supported, trade-offs stay within their frozen bounds, and the
assembled manuscript is internally consistent. `Unknown` is pending evidence,
not a pass. Rework or restore according to the frozen rollback rule when an
obligation fails.

## Minimum handoff

Use existing project records rather than creating a second database. The final
handoff should make it possible to recover:

- the baseline and candidate versions;
- the author requirement and literature/notation priority;
- the assumption and result branches actually changed;
- the complete verification artifact and concise manuscript locations;
- accepted, rejected, and unresolved changes with reasons;
- actual validation and review evidence;
- the strongest wording the current proof release permits.
