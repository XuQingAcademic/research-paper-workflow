# Upstream mechanisms and gap decisions — 2026-09-05

Public GitHub repository metadata and actual skill/source files were inspected
on 2026-09-05. Stars are repository-level snapshots, not per-skill quality or
scientific validation. Existing literature and review adaptations are reused.
No external repository code is vendored into this workflow: the stage protocols
and helpers are newly written to fit the local interfaces.

| Repository | Stars at inspection | Pinned revision | License status |
| --- | ---: | --- | --- |
| [superpowers](https://github.com/obra/superpowers) | 281,844 | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` | MIT |
| [scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 42,687 | `1e5eeffbdad3749125afe7ab48a39694e27f181c` | MIT |
| [planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 26,634 | `03128b278b0926180854703e43abd7ea2ff18c00` | MIT |
| [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | 15,735 | `e59008d7a42eea50a2797e55dd0d85bbbf6572f5` | MIT |
| [claude-scholar](https://github.com/Galaxy-Dawn/claude-scholar) | 5,326 | `6ed46dac03191c7a734f49ed48b41195012098ff` | MIT |
| [Auto-Empirical-Research-Skills](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills) | 3,678 | `129c45918c93c70a3a2cbf02a3e842341a0e5eae` | Root CC-BY-SA-4.0; mixed vendored licenses |
| [AI-research-feedback](https://github.com/claesbackman/AI-research-feedback) | 477 | `8abc36b5576eca04611b4d632260caace5f1a3b7` | MIT |
| [AER-skills](https://github.com/brycewang-stanford/AER-skills) | 48 | `85eae99fe5935c79c209f597a56c88899082a090` | MIT |

The last two entries were included for economics relevance, not described as
high-star repositories. Public metadata was obtained from the corresponding
GitHub `/repos/OWNER/REPO` REST endpoints; branch references supplied the SHA.

## Adopted mechanisms and exact source evidence

**Idea quality and falsification.** K-Dense's
[scientific-brainstorming](https://github.com/K-Dense-AI/scientific-agent-skills/blob/1e5eeffbdad3749125afe7ab48a39694e27f181c/skills/scientific-brainstorming/SKILL.md)
and [hypothesis-generation](https://github.com/K-Dense-AI/scientific-agent-skills/blob/1e5eeffbdad3749125afe7ab48a39694e27f181c/skills/hypothesis-generation/SKILL.md)
motivate independently generated candidates, rival explanations, discriminating
predictions, and falsification conditions. These appear in `stage-playbook.md`.
Their biological tool stack and generic statistical statements were not imported.

**Question-to-evidence handoff.** Claude Scholar's
[research contract](https://github.com/Galaxy-Dawn/claude-scholar/blob/6ed46dac03191c7a734f49ed48b41195012098ff/skills/research-ideation/references/research-contract.md)
motivates a question card with missing evidence and a minimum next action.
Stable evidence identities and wording ceilings are mapped to the existing
paper-v3 state, not copied into another competing claims ledger. No automatic
Zotero writes or arbitrary recent-years search window is inherited.

**Durable continuity.**
[planning-with-files](https://github.com/OthmanAdi/planning-with-files/blob/03128b278b0926180854703e43abd7ea2ff18c00/skills/planning-with-files/SKILL.md)
motivates persistent decisions, progress and next actions. Its
[catchup implementation](https://github.com/OthmanAdi/planning-with-files/blob/03128b278b0926180854703e43abd7ea2ff18c00/skills/planning-with-files/scripts/session-catchup.py)
was inspected; this workflow uses project receipts, not conversation-history
mining or external hooks. `workflow_state.py` rechecks artifacts on resume.

**Evidence before completion.**
[superpowers verification](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/skills/verification-before-completion/SKILL.md)
motivates tying completion to observable results. Software tests still do not
prove an econometric theorem. Automatic commits, model preferences and repeated
approval rituals were not imported.

**Stage receipts.** ARIS's Codex
[idea-discovery](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/e59008d7a42eea50a2797e55dd0d85bbbf6572f5/skills/skills-codex/idea-discovery/SKILL.md)
and [gate implementation](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/e59008d7a42eea50a2797e55dd0d85bbbf6572f5/tools/idea_discovery_gate.py)
motivate real artifact/reviewer records. The local implementation uses explicit
stage states and actual file hashes. It does not import autonomous GPU budgets,
notification integrations, fixed models, or an unrestricted novelty-confirmed label.

**Minimal routing.** AERS's
[entry point](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills/blob/129c45918c93c70a3a2cbf02a3e842341a0e5eae/SKILL.md)
motivates stage/method routing and minimal loading. Its
[license audit](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills/blob/129c45918c93c70a3a2cbf02a3e842341a0e5eae/docs/LICENSE_AUDIT.md)
lists unresolved and mixed-license collections, so the bundle is not installed.
Its [significance-search](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills/blob/129c45918c93c70a3a2cbf02a3e842341a0e5eae/skills/67-econfin-workflow-toolkit/significance-search/SKILL.md)
searches control combinations by t statistics; this is explicitly excluded from
confirmatory analysis in `empirical-bridge.md`.

**Economics review and identification.** Existing local review skills already
adapt [AI-research-feedback](https://github.com/claesbackman/AI-research-feedback/blob/8abc36b5576eca04611b4d632260caace5f1a3b7/Skills/review-paper/SKILL.md).
Reuse their current-version critique and record missing reviewer outputs.
The estimand/assumptions/diagnostics/inference interface in
[AER identification](https://github.com/brycewang-stanford/AER-skills/blob/85eae99fe5935c79c209f597a56c88899082a090/skills/aer-identification/SKILL.md)
informed the empirical bridge, but universal numeric thresholds and unqualified
method claims were rejected. Current method documentation and the actual design
govern estimator and inference choices.

## What was missing and what is now addressed

| Gap | Workflow response | Remaining boundary |
| --- | --- | --- |
| Idea generation before a draft exists | Candidate/rival/falsifier/feasibility cards | Originality requires real literature and scientific work |
| Literature tools not connected to contribution | Search record and nearest-neighbor evidence handoff | Search coverage remains open-world |
| Empirical execution between design and writing | Data provenance, pre-analysis plan, estimator/inference/result mapping | Actual data access and method-specific execution are task-dependent |
| Lost progress or repeated work across stages | Hash-bound stage receipts and next actions in `.paper/workflow/` | Local attestations cannot authenticate scientific truth |
| Production simulation cannot finish | Runnable handoff and explicit deferred status; re-open prose when results arrive | No completed simulation or submission claim until actual evidence exists |
| Upstream PARTIAL/FAIL can evade legacy release validation | New `check_release_handoff.py` checks dependency consumption and release consistency | Existing component validators and real evidence still required |
| Supervisor/roundtable absent from manager registry on 2026-09-05 | Explicit route entries and usage profiles | Historical gap: registration was fixed on 2026-09-06; inspect the current registry instead of using the old snapshot |
| R&R routed to paper review by broad keywords | Direct writer-v3 R&R route | Review and response are different tasks |

The existing manager audit also identifies uncompleted scientific-validation,
state-migration and mentor-corpus quality work. This workflow does not claim to
repair those entire systems. It isolates the confirmed cross-skill false-green
case with a tested bridge, preserves older installations, and requires precise
scientific receipts before claiming research completion.

## 2026-09-12 compatible adoption

The local patch connects the dedicated idea skill, adds advisory reverse claim coverage, evidence-first material re-review, explicit candidate reopen conditions and an optional bounded probe recorder. It reuses existing project IDs, ledgers and frozen-evaluation tooling. Implementations were written locally; third-party code was not vendored.

Design sources: [autoresearch program at 228791f](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/program.md) for bounded comparable attempts and retained failures; [academic-research-skills at f1a57bb](https://github.com/Imbad0202/academic-research-skills/tree/f1a57bbcabf5cf3da9654ac4d54d056dc6b4b7ea) for reverse-coverage advisory, re-review input order and explicit capability evidence. Their popularity does not establish local scientific performance. The manager's `references/capability-evidence.json` records actual local validation and unmeasured effects.

## 2026-09-27 research-workflow comparison and compatible adoption

Four popular, directly relevant public repositories were re-inspected on their
default branches. GitHub displayed approximately 31.5k stars for
[STORM](https://github.com/stanford-oval/storm), 29.6k for
[GPT Researcher](https://github.com/assafelovic/gpt-researcher), 14.6k for
[AI Scientist](https://github.com/SakanaAI/AI-Scientist), and 5.9k for
[Agent Laboratory](https://github.com/SamuelSchmidgall/AgentLaboratory). These
are popularity snapshots, not an exhaustive GitHub ranking or scientific-quality
evidence. README claims were checked against the repositories' principal
workflow, idea/novelty, experiment, report, and review implementations. No code
or prompts from these projects were copied into the local skills.

Adopted mechanisms, reimplemented for the existing local evidence contracts:

- STORM's perspective-guided curation and evolving knowledge structure motivate
  explicit named, functional, citation, version, implication, composition,
  cross-domain and contradictory-evidence search paths. The local controller
  binds actual sources and leaves material paths open; it does not treat a
  generated article or mind map as publication-ready evidence.
- GPT Researcher's configurable search breadth/depth, multi-source execution,
  progress reporting and cost tracking motivate a visible search frontier and
  append-only operational telemetry. The local implementation reports unknown
  cost separately and does not equate source count or web frequency with truth.
- AI Scientist's candidate portfolio and baseline-to-experiment loop motivate
  bounded independent candidate mechanisms, cheapest falsifiers, actual budgets
  and retained failures before design freeze. The local controller rejects LLM
  novelty scores and never converts “not found” into a global novelty claim.
- Agent Laboratory's phase telemetry, human checkpoints and review-to-plan
  return path motivate explicit blockers, next actions and resumable operational
  state. Scientific decisions stay in specialist records; same-model rewards or
  several reviewer personas are not treated as independent validation.

The compatible patch adds `idea_portfolio.py`, `research_operations.py`, and
`empirical_contract.py`, plus their routed references and tests. It preserves
existing workflow plan/revision schemas and legacy project state. The empirical
contract standardizes a project adapter, known-answer fixture, diagnostics,
machine-readable output and interpretation ceiling without claiming to be a
universal estimator library. Structural/functional success still does not prove
research efficacy, literature recall, identification, theorem truth or
cross-project portability.

## 2026-09-28 token-efficiency and offline-wait comparison

Twenty popular public repositories were inspected for mechanisms relevant to
context reduction, retrieval, durable state, caching, model routing, constrained
outputs, usage measurement, evaluation, and dependency-aware waiting. GitHub
stars were used only as a dated popularity proxy because “citation” is not a
native GitHub quality measure. The full repository table, approximate star
snapshots, adopted mechanism, rejected overclaim, and local rules live in
[token-efficiency.md](token-efficiency.md); they are not duplicated here.

The compatible local synthesis is deliberately fail-closed: remove redundant
work losslessly before compressing; protect equations, assumptions, source
locators, numerical evidence, code/config and author decisions; use cache and
lower-cost routing only with current input bindings and escalation triggers;
and require a frozen paired quality evaluation before claiming that an observed
token reduction preserved quality. `token_evaluation.py` implements that bounded
comparison. `research_operations.py` retains v1 records and adds v2 dependency
edges plus a handle-bound `waiting` state, so simulations and other offline jobs
can be awaited without repeated model polling while independent work continues.

No third-party code or prompt was copied. These mechanisms do not prove general
token savings or scientific non-regression; those effects remain project- and
evaluation-specific.

## 2026-10-15 source-level reinspection and selective integration

Read in this order: ARIS, research-epic-manager, mimeo, AutoResearchClaw,
Scientific Agent Skills. Repository snapshots and paper versions are distinct;
the reports describe earlier implementations than the inspected trees. This was
a focused reading of relevant skills, implementation paths, tests and reported
evaluation/limitations, not an execution or audit of every repository component.
No third-party code, prompt or skill bundle is imported. Root licenses at the
inspected revisions are MIT; vendored subcomponents are not relicensed by that.

| Project and inspected commit | Specific source evidence | Local decision |
| --- | --- | --- |
| [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/26b95cfa0d8747078e9e43b42e20952709e561b8) | `skills/shared-references/reviewer-independence.md`, `review-scope-limits.md`; Codex `result-to-claim` and `paper-claim-audit`; `tools/verify_paper_audits.sh`. [Report v1](https://arxiv.org/html/2605.03042v1), Sections 2.2, 3.1 and 5. | Reuse existing evidence-to-claim ownership. Clarify first-pass judgment versus repair verification, and require a concrete defect/consequence before admitting extra machinery. Do not import score thresholds, model-family acceptance labels, universal reviewer calls or a ban on useful existing hashes. |
| [research-epic-manager](https://github.com/alexchen5/research-epic-manager/tree/5551817dc26cf945854f623ac58bfb74fef5f688) | `skills/research-project-epic-manager/references/lifecycle-and-gates.md`, `reviewer-briefs.md`, `scripts/review_engine.py`; example `project/docs/verification/report.md`. [Paper v1](https://arxiv.org/html/2609.31683v1), Sections 2.1–2.3. | Reuse compact state, just-in-time planning and negative results. Reject whole-stage downstream invalidation, a second tracker, compulsory branch/ASCII conventions and score-derived scientific acceptance. Preserve actual dependency-scoped correction instead. |
| [mimeo](https://github.com/K-Dense-AI/mimeo/tree/a4cea1842a24515cda354a3aa9eb9763677a3cdd) | `src/mimeo/verify.py`, `refine.py`, `prompts/extract.md`. [Paper v1](https://arxiv.org/html/2609.00453v1), Sections 2–5. | Clarify that a card or matched quotation is a retrieval aid: attribution, context, conditions and implication still need source checking. Same-source derivatives are not independent corroboration. Do not import persona imitation, fuzzy/short-quote acceptance as scientific verification, or self-score refinement as demonstrated judgment transfer. |
| [AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw/tree/be4ba4755bf1b52220f25e13b2293b5956590070) | `researchclaw/pipeline/verified_registry.py`, `stage_impls/_analysis.py`, `copilot/controller.py`, `memory/decay.py`. [Paper v2](https://arxiv.org/html/2605.20025v2), Sections 3.3–3.6 and 4. | Clarify execution/measurement failure versus weak evidence versus valid scientific contradiction before repair/refine/pivot. Reuse specialist result contracts; numeric occurrence alone does not validate a claim's condition or denominator. Do not import score-based pivot, fixed intervention gates, best-only reporting, age-based truth decay or all 23 stages. |
| [Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills/tree/a1043ef544e3a100c28e70a736b6cf32554d0677) | `skills/scientific-critical-thinking/SKILL.md`, `hypothesis-generation/SKILL.md`, scientific-writing evidence rules; `tests/_meta/test_repo_contract.py`. [Paper v2](https://arxiv.org/html/2609.00065v2), Sections 2, 4–6. | Reuse progressive disclosure, rival explanations and task-specific tools already present locally. Do not bulk-install the collection, add clinical review frameworks to theory papers or turn every source check into a new approval. Tests and corpus measurements do not establish task-level scientific benefit. |

The paper evidence is bounded: ARIS reports observational deployment rather
than a completed controlled benchmark; epic-manager reports one research case;
mimeo separates knowledge access from unmeasured judgment transfer;
AutoResearchClaw mainly uses author-run, model-judged benchmarks; Scientific
Agent Skills measures documentation properties, not scientific outcomes. The
two K-Dense projects are not independent team-level confirmations.

The behavioral clarification has one owner, `goal-and-learning.md`; the
entrypoint only routes to it. Existing ledgers, state formats, scripts,
specialist scientific gates, author decisions and active projects are unchanged.
Retain old source snapshots above as historical evidence rather than replacing
their pins. Local validation and effects must be reported separately from these
design sources; no general quality, speed, cost or theorem-correctness gain
follows from reading or adopting them.
