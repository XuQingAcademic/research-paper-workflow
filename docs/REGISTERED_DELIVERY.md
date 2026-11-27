# Registered manuscript delivery

Use this path for a complete LaTeX paper with an explicit release decision, a
risk or error threshold, and an inspectable source for the reported numbers.
The repository checkout and the full plugin bundle include the workflow,
simulation audit and writing skills as siblings. A single extracted skill does
not carry the companion modules used by the delivery command.

## Try it on synthetic records

Install Python 3.9+, `latexmk`, a TeX engine and Ghostscript. The example uses
`pdflatex` with the `article` class and the `geometry` package. Then run the
[public example](../examples/registered-delivery/README.md) from a checkout.
It produces an independently rebuildable PDF, checks the arithmetic and builds
a receipt you can inspect. The main delivery command can use `pdftotext` for
text readback if Ghostscript is unavailable. Use the TeX packages required by
your manuscript. The controllers target macOS and Linux.

## Register your own project

1. Keep a buildable draft tree, an original evidence directory and a trusted
   JSON profile. Keep the evidence and profile outside the editor's writable
   copy. Review the canonical draft entry, the unique results insertion anchor
   and the TeX build command before starting the editing session.
2. In the profile, map each planned trial to its identity, design cell, explicit
   release decision, true risk metric and threshold. Record repeated decisions
   within a trial with distinct keys. Choose the denominator that answers the
   research question. Equality with the threshold is excluded from the strict
   numerator. The [synthetic profile](../examples/registered-delivery/profile.json)
   shows the replay case. Original records and independent replays have distinct
   provenance. For supported archived vector curves with no trial records, keep
   the author's labels separate from the visible lower bound.
3. A domain reviewer confirms the cited theorem statement, exact TeX locators,
   assumptions, controlled quantity, and scope. The scope declaration should state
   whether the theorem controls a population risk, an expectation, a probability
   bound, or a finite-test error. Register narrowly targeted wording repairs when
   the draft contains a known conflicting statement.
4. After the editor returns the draft, have the project host run the command
   below. The host alone determines which output qualifies for delivery. The
   command needs a new output directory outside the draft and evidence trees.

```sh
python3 -B plugins/research-paper-workflow/skills/research-paper-workflow/scripts/deliver_manuscript.py --project DRAFT --evidence ORIGINAL_EVIDENCE --profile TRUSTED_PROFILE.json --output VERIFIED_OUTPUT
```

The command recomputes the registered counts, inserts the supported result,
recompiles the working copy and reads back the PDF before placing it in the
output tree. It can consolidate clearly matching repeated result prose in the
registered results subsection while retaining distinct quantities and
comparisons. Upon success, the output includes revised TeX, the PDF, and
`.delivery-receipt.json`. A failed check exits with an error and leaves the
input draft available for repair. Pass `--deadline-epoch` with a Unix timestamp
for a different time budget. The command defaults to 90 seconds for the controlled
delivery step. Time spent editing or generating simulation results is outside
that default.

See the [controller registration notes](../plugins/research-paper-workflow/skills/research-paper-workflow/references/controlled-manuscript-delivery.md) and [simulation handoff](../plugins/research-paper-workflow/skills/audit-numerical-simulations-v2/references/decision-results-handoff.md) for the expected evidence. The check covers the registered evidence and wording. Mathematical review of new theorems and editorial review of unregistered claims remain part of the research workflow.
