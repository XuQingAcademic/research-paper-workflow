# 正文到主张账本的反向提示

受管项目新增或修改数字、引用或结果句时，用 `scripts/claim_coverage.py` 检查现有 `.paper/claims.yaml` 是否映射这些候选。独立脚本只读；也可在现有审计上添加 `--claim-coverage`。输入是现有主张，输出是可丢弃的定位视图，不建立第二份事实账本。

```bash
python3 scripts/claim_coverage.py /absolute/project --main main.tex --format markdown
python3 scripts/claim_coverage.py /absolute/project --path sections/results.tex --format json
python3 scripts/audit_paper_project.py /absolute/project --claim-coverage --coverage-path sections/results.tex --format json
```

重复 `--path`（或组合审计的 `--coverage-path`）限定已改文件。报告写明实际文件与输入哈希；局部结果不能称为全文检查。没有账本、定位模糊或文字过期时保留 unknown/unresolved，不通过猜测填满。不要只补记录来消除提示：打开句子及其实际来源/结果，决定是补充现有 claim 的精确位置、拆分复合主张、修正表述，还是确认它不是科学主张。映射到一个 supported claim 也不是重新核验其支持关系。

脚本的词法范围有限：带引用、数值或部分中英结果措辞的候选；公式、隐含理论结论和复杂排版仍需阅读。精确映射只表示该候选已有位置关联，不保证整句证据完整。宽泛章节定位不能覆盖整章；尚未细化的旧定位保持可用记录并显示待核查，不强制迁移历史项目。

advisory 提示本身不改变发布状态或权限。真实发现的错误沿用现有 findings/claims 修复流程；合法年份、公式、方法说明或实现文字可被判断为误报。没有提示仅表示在报告范围内未检测到候选遗漏，不是语义完整或论文正确证明。测试/实现支持的精确位置格式以脚本帮助和报告为准。

Optional precise locator (existing broad locators remain readable, but unresolved):

```json
{"path": "main.md", "line": 7, "text": "The estimate is 0.25."}
```

Use `start_line`/`end_line` for a wrapped sentence, or path plus exact `text` only when unique. Legacy `main.md:7` / `main.md#L7-L8` can use `summary` or `allowed_wording` as the exact text. A substring maps only that part of a compound candidate; stale or chapter-wide locations cannot register unrelated sentences. The combined audit returns 2 on invalid coverage input, 1 for its existing structural errors, and 0 for advisory gaps alone.
