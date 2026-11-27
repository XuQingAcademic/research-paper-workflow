# 项目状态与任务路由

## 目录

1. 轻量模式与受管模式
2. `.paper/` 状态包
3. JSON-compatible YAML
4. 生命周期与阶段门
5. 锁定决策和非主张
6. 影响等级

## 轻量模式与受管模式

使用轻量模式处理：

- 单句或单段语言修改；
- 边界明确的摘要压缩；
- 不涉及跨文件同步的局部解释；
- 用户只要求诊断且材料不足以建立完整项目状态。

轻量模式仍须守住证据、权限、术语和主张强度，但不强制创建 `.paper/`。

使用受管模式处理：

- 完整章节或全文；
- 多文件 LaTeX、附录、补充材料或复现包；
- 多轮修改、R&R、合作者交接；
- 任何改变问题、对象、方法、结果或结论的修改；
- 对完整论文或投稿包进行 `verified` / `submission-ready` 判定的任务；局部文本的“最终版”仍按局部范围处理。

若项目已有等价账本或状态系统，读取并适配，不建立相互竞争的第二套真相源。

## `.paper/` 状态包

`init_paper_state.py` 生成：

```text
.paper/
├── paper_state.yaml
├── claims.yaml
├── exhibits.yaml
├── citations.yaml
├── revisions.yaml
├── journal_overlay.md
└── unresolved_issues.md
```

### `paper_state.yaml`

记录：

- 活动稿、论文类型、生命周期、语言和版本；
- Question–Friction–Move–Guarantee–Value；
- 目标期刊及 overlay 状态；
- confidentiality、authorized operations；
- locked decisions、nonclaims、canonical terms；
- 声明式关键事实及禁止变体；
- release candidate hash、检查时间和人工批准状态。

### `claims.yaml`

每项主张至少记录：

- `id`、`claim_type`、`summary`、`status`；
- `allowed_wording`、`forbidden_stronger_wording`；
- `evidence_ids`、`locations`、`scope`、`risk`；
- `verified_by` 和 `verified_at`，未知时保持空值。

建议状态：`draft`、`needs-evidence`、`supported`、`rejected`、`superseded`。

### `exhibits.yaml`

把 theorem、lemma、algorithm、table、figure、simulation 和 empirical result 作为可追踪 exhibit。记录其 label、文件、生成程序、支持主张、样本/DGP、估计量、推断和状态。

### `citations.yaml`

分别记录 metadata verification 与 claim-support verification。一个文献可以存在且书目信息正确，但仍未验证当前句子。

### `revisions.yaml`

复用现有意见记录，保存审稿、合作者、用户直接或用户转述导师请求的来源定位与适用版本、A–D 影响等级、受影响主张和产物、采取动作、稿件位置、验证状态和剩余限制。来源归因、采纳决定和实施/核查状态分别判断，详见 [revision-and-referee.md](revision-and-referee.md)；项目已有 feedback/decisions 时引用同一记录，不另造 schema 或复制账本。

由 `research-paper-workflow` 的 `continuous-revision` 模式管理的问题仍写入
同一个 `revisions` 数组，并可增量使用 `cycle_id`、`severity`、`area`、
`source`、`manuscript_version`、`affected_objects`、`depends_on`、
`acceptance_criteria`、`author_gate`、`implementation`、`verification`、
`reopen_if` 和 `root_cause`。状态为 `queued`、`active`、`verifying`、
`blocked_author`、`accepted` 或 `deferred`；其中只有经过实际修改和独立复核的
`accepted` 可视为 release audit 中的已关闭修订。`deferred` 仍是开放修订，除非
原写作流程另有明确 waiver；P0/P1 不得通过延期获得作者审阅或发布资格。

这些字段是 schema version 1 的向后兼容扩展。写作 Skill 继续拥有修订记录，
控制器只在 `.paper/workflow/revision-cycle.json` 保存问题 ID、队列和哈希引用，
不得复制问题正文、主张或证据。

### Markdown 文件

`journal_overlay.md` 保存动态期刊规则及官方来源。`unresolved_issues.md` 保存缺失、冲突、waiver 和 release blockers；开放 blocker 不得从报告中消失。

## JSON-compatible YAML

为保持零第三方依赖，脚本生成的 `.yaml` 文件采用 JSON 语法；JSON 是 YAML 1.2 的兼容子集。这样既保留 YAML 生态兼容性，又可由 Python 标准库确定性解析。

不要加入 YAML 注释或改成非 JSON 语法，除非项目明确采用 PyYAML 并同步更新脚本和测试。

## 生命周期与阶段门

建议阶段：

1. `design`：问题、对象、摩擦和计划证据；不得把计划写成结果。
2. `draft`：已有部分结果，允许明显 placeholder；不声称完整。
3. `internal-revision`：主脊基本稳定，执行跨章节影响检查。
4. `pre-submission`：引用、表图、复现和期刊 overlay 全部进入检查范围。
5. `r-and-r`：每条意见与主张、证据和修改位置绑定。
6. `release`：冻结精确候选稿，禁止未记录的后续修改。

阶段变化必须由实际证据支持，而不是因为文件名包含 `final`。

## 锁定决策和非主张

将以下内容显式记录为 locked decision：

- 研究问题与 estimand；
- 允许的因果或描述性表述；
- 符号、术语和模型对象；
- 作者指定的主结果与次要结果；
- 不得改变的表图、文件或合作者文字。

将作者明确不主张的内容记录为 nonclaim，例如：

- 不声称 uniform validity；
- 不识别结构参数；
- 应用只作 illustration；
- simulation 不证明现实数据性能。

编辑时同时检查 locked decisions 与 nonclaims。

`canonical_terms` 中的每个规范术语还应记录 `provenance`。文献既有术语使用
`kind: literature`、非空 `citation_keys` 和精确 `source_locator`。确需作者定义
的新术语使用 `kind: author-defined`，并记录 `maps_to`、具体 `reason` 和已有
作者决定的 `decision_locator`。旧项目缺少来源字段时可以继续编辑，但发布审计
会把缺失来源视为错误；详细规则见
[terminology-governance.md](terminology-governance.md)。

## 影响等级

- A 类变化重开完整证据链、摘要、引言、结论和投稿摘要。
- B 类变化重开受影响的方法、理论、模拟、应用、附录、表图及摘要性文本。
- C 类变化重开所有投稿表单、声明和元数据。
- D 类变化执行局部语义差异和最终候选检查。

先检查变化是否改变对象、量词、假设、结果或依赖来确定等级；确有未消除的实质不确定性时，扩大相应检查。不要仅因措辞含糊就重跑整篇论文的最高等级流程。
