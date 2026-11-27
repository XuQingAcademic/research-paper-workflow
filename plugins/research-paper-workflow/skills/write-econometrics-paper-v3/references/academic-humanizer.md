# Academic Humanizer Profile

Use the installed upstream `humanizer` only as a prose-editing pass after the
scientific content, claim strength, source versions, and notation are settled.
Read its current `SKILL.md`, then apply this academic profile as the governing
constraint for econometrics manuscripts.

## Purpose and trigger

Use the pass when the user asks to remove AI-like prose, when a manuscript has
repetitive staging or formulaic cadence, or during an explicitly requested final
language edit. It is optional for ordinary scientific drafting. It does not
estimate whether text was written by AI and does not promise to evade a detector.

## Academic register

- Keep a formal, compact scholarly register appropriate to the manuscript and
  target journal. Do not introduce chatty openings, contractions, rhetorical
  questions, reader commands, jokes, personal reactions, or conversational
  fillers unless the supplied author sample already establishes that style.
- Prefer direct sentences, but retain passive voice where the actor is irrelevant
  or the convention improves precision. Do not vary a defined term merely to
  create lexical variety. Logical parallelism, enumerated assumptions, and
  repeated technical terms are not style defects.
- Follow [terminology-governance.md](terminology-governance.md). Do not coin a
  label, rename an established object, or replace a literature term with a
  more distinctive synonym to make the prose appear original. If the supplied
  text uses an unregistered label, leave it unchanged and flag it for the
  substantive terminology review.
- Remove generic staging, inflated importance, canned contribution language,
  forced triads, repetitive summary closers, vague attribution, and ornamental
  transitions. Replace them with the exact scientific relationship already
  supported by the project evidence.

## Immutable content during the pass

Preserve equations, symbols, theorem statements, assumptions, quantifiers,
modal verbs, causal language, comparison direction, novelty qualifiers,
uncertainty, numbers, units, table and figure references, citation keys and
placement, labels, cross-references, defined terminology, quotations, and source
locators. Do not add examples, mechanisms, interpretations, citations, firstness,
or policy claims. Do not edit BibTeX, code, data, ledgers, or generated results as
part of a prose-humanization pass.

If a sentence cannot be made natural without changing one of these elements,
leave it unchanged and record it for a substantive revision. Any change to the
claim AST is a scientific edit under the writer workflow, not a style edit.

## Pass order and verification

1. Freeze the before file or diff and the exact prose scope.
2. Apply upstream Humanizer's structural diagnostics to that scope under this
   profile. Edit paragraphs rather than mechanically replacing a word list.
3. Run `scripts/check_academic_humanization.py BEFORE AFTER --json`. Resolve any
   protected-token or register failure.
4. Re-read the changed sentences against their claim and citation records. For
   high-impact prose, compare estimand/null, population, quantifiers, condition,
   result direction, evidence tier, and source version explicitly.
5. Build and inspect the affected manuscript pages when the LaTeX source changed.

The checker is deliberately narrow. Passing it shows that selected surface
tokens and register rules were preserved; it does not prove semantic equivalence,
academic quality, or scientific correctness.
