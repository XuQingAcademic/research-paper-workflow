# 终稿数字来源核验

该步骤用于获准修改、带实测放行或风险保证结果的完整 LaTeX 终稿。先确认活动入口和构建方式。用原始明细、作者标记、可见图像或可复现重跑核实关键结果，同时查定理原文。能直接核实计数时立即进入写作，避免为恢复无关依赖耗尽时间。

确认实际放行的决策、严格阈值不等式、计数单位、有效分母和数字来源。按定理的对象、前提、概率及量词说明适用范围。图的颜色代表作者归类时，把归类数归于作者。图中可见路径不全时，独立辨认的次数只写下界。对照和实际保证使用不同规则或概率时分别保留。来源有限时，用证据确实支持的范围改写并说明计数限制。

在项目内保存 `numerical-handoff-plan.json`。把主句和适用范围放在科学结果正文。命令按来源类型生成主句，并核对同一段的定理范围。

```json
{
  "cwd": "paper",
  "entry": "main.tex",
  "pdf": "main.pdf",
  "build": [["latexmk", "-g", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]],
  "claims": [{
    "id": "main-risk-result",
    "file": "paper/main.tex",
    "old": "<copy one unique old sentence or temporary anchor verbatim from the results prose>",
    "count": 3,
    "total": 50,
    "basis": "full-records",
    "source": "the archived trial log",
    "unit": "calibration trials",
    "event": "an issued set and population risk strictly above the budget",
    "scope": "<verified adjacent theorem scope as final manuscript prose>",
    "evidence": [
      {"role": "count", "file": "outputs/trials.csv", "sha256": "<actual SHA-256>", "locator": "<rows, columns and strict count rule>"},
      {"role": "scope", "file": "evidence/theorem.txt", "sha256": "<actual SHA-256>", "locator": "<result and assumption locations>"}
    ],
    "also": [{
      "file": "paper/main.tex",
      "old": "<unique inaccurate sentence in abstract, caption, or conclusion>",
      "new": "<correct replacement in TeX syntax on one line>",
      "pdf_text": "<corrected words readers see in the PDF>"
    }]
  }]
}
```

`basis` accepts `author-labels`, `visible-lower-bound`, `full-records` or `replay`. Each claim needs `count` and `scope` evidence with their own locators. A single file can support both roles if it contains both pieces of evidence. For an uncertified baseline, locate the rule and the assumptions that restrict any separate certificate. Use `also` for secondary occurrences requiring correction or explicit readback. Omit `old` to verify an already correct sentence. File paths in claim and evidence records are relative to the project. Use an exact excerpt or a frozen source as evidence when editing a TeX file that also states the theorem, with the original file and label in the locator.

Run `python3 <this-skill>/scripts/finalize_numerical_handoff.py <project-root> numerical-handoff-plan.json`. It verifies the evidence fingerprints and unique source sites, applies the corrections, emits a fresh PDF, and reads back the required passages through Poppler or Ghostscript. Correct any failed check and rerun. The default passing receipt is `.numerical-handoff.json`. Rerun after changing the manuscript. Before delivery, also check that all repeats in the abstract, results, captions and conclusion use the supported wording.

The command verifies that the correction is bound to the evidence files and appears in the delivered PDF. Ground the number, denominator and scope in the evidence when preparing the plan. A receipt cannot detect unlisted claims or establish that an interpretation is scientifically sound.
