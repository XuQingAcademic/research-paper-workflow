# Registered delivery example

This example uses a small original TeX manuscript and six synthetic teaching records. The trusted profile names the manuscript entry, decision ledger, risk threshold and theorem location.

The demo counts a trial only when a release actually occurred and its population risk was strictly above 0.20. Two of six trials meet that criterion. A release at exactly 0.20 and a withheld rule at 0.45 are excluded from the numerator. The denominator includes all six trials, four of which were released. The manuscript distinguishes these teaching counts from the theorem's probability bound over independent calibration for a fixed, prespecified rule.

## Run the checks

From the repository root, use Python 3.9 or later and put `latexmk`, `pdflatex` and Ghostscript (`gs`) on your PATH. The TeX installation should provide the standard `article` class and `geometry` package.

```sh
python3 -B examples/registered-delivery/check_demo.py --output ./registered-demo-output
```

Use a new output directory. The verified manuscript is in `paper/main.tex`, the PDF is in `paper/main.pdf`, and `.delivery-receipt.json` hashes both artifacts, binds the profile and sources, and records the decision counts. Omit `--output` to run entirely in temporary storage.

The check exercises removal of a repeated count in the draft while preserving its 19.25 percentage-point Monte Carlo standard error. It also compares every submitted page with an independent rebuild and verifies that an invalid theorem locator prevents publication.
