---
name: audit-numerical-simulations-v2
description: Audit, design, implement, and release-test scientific numerical or Monte Carlo simulations for econometrics and statistics, with theorem-to-cell binding, actual-R precision, deterministic parallel RNG, atomic resume, solver-failure lineage, adversarial fixtures, and paper evidence ceilings. Use for simulation plans, implementations, Monte Carlo results, and numerical reproducibility. Bootstrap, dependence, quantile processes, QIT, and Quantile Uniform Inference trigger this skill only when the task concerns their numerical experiments; route pure proof questions to prove-econometrics-theory-v2.
---

# 数值模拟科学性核查 v2

把数值模拟视为带已知真值的统计实验。以“理论对象—代码实现—逐次结果—论文主张”的可追溯闭环判断科学性，不以代码能运行、重复次数很大或图表好看代替有效性。

## 选择工作模式

根据用户材料选择一个主模式；可以组合，但要指出主模式。

- **设计审查**：在运行前审查目标、DGP、比较方法、指标、重复次数和停止规则。
- **预算审查**：按约定的完整实验范围核算剩余计算、时间和资源；计时子集不替代完整目标。
- **实现审查**：检查统计公式、随机流、并行、失败处理、checkpoint、环境和数值稳定性。
- **pilot 审查**：用最小实验验证不变量、oracle、null size、耗时与内存；不得把 pilot 当正式结果。
- **结果审查**：读取逐 replication 结果，检查完整性、重复、失败率、Monte Carlo uncertainty 和配对比较。
- **论文审查**：核对正文、附录、代码、配置、表图和复现包是否一致。
- **全流程 gate**：从研究主张开始，依次执行全部关卡，给出是否可进入正式计算或投稿的结论。

若当前稿件讨论放行、认证或假设边界，先核对最影响使用结论的对照。把严格超阈且实际放行的事件定义、实际次数和分母、证据类型、原文件及其定位、定理成立所需条件一起交给写作者。区分完整明细、作者标记、图中可确认的下界和独立重跑各自支持的结论。按[决策结果和理论范围](references/decision-results-handoff.md)核验真值、阈值不等式、是否真的放行、去重单位及假设范围。交付 LaTeX 终稿时，写作 skill 将用这些证据核验并重编正文和 PDF。

简单 MCSE、随机流或结果口径问答可直接核查相关公式/输入，不创建 manifest 或完整审计报告；已有计划与有效验证可复用。用户只要求“检查/审查”时保持只读；已要求设计、实现、修复或完成模拟时，执行相应本地编辑与验证，不在各关卡重复请求授权。保留旧结果，新实现使用新目录或新配置指纹，禁止把不同代码版本的结果混入同一汇总。

受控终稿交付使用 `scripts/verified_decisions.py` 从锁定的逐项记录按既定试验键重计。提供实际放行判定、真量、阈值、试验键和分组，分别保留实际放行分母与总试验分母。无逐项记录时，按授权材料分别给出作者标记和可见下界。定理依据要含从原稿可定位的目标量、概率、适用条件和与有限测试误差的关系。

## 按需读取资源

首次核查时读取以下文件中与当前模式相关的原则和关卡；全流程或发布审计读取完整规范。同一任务中复用未变化的规范，不因局部修复重启全部关卡：

1. [references/scientific-principles.md](references/scientific-principles.md)：设计、精度、分析与报告原则。
2. [references/audit-rubric.md](references/audit-rubric.md)：严重度、关卡与标准输出。

再按任务读取：

- 涉及代码、集群、并行、checkpoint、随机种子、复现或预算时，读取 [references/implementation-and-reproducibility.md](references/implementation-and-reproducibility.md)；预算可复用 [assets/compute-budget-worksheet.md](assets/compute-budget-worksheet.md)，不改动科学设计 schema。
- 涉及检验、置信区间、bootstrap、quantile、依赖数据、学习/选择程序或 adaptive CvM 时，读取 [references/inference-specific-checks.md](references/inference-specific-checks.md)。
- 涉及 Quantile Independence Test、Quantile Uniform Inference、Adaptive CvM，或与它们相似的 quantile-process / adaptive-weight 项目时，读取 [references/project-derived-lessons.md](references/project-derived-lessons.md)。
- 涉及 proof/writing handoff、PARTIAL 状态、对抗测试或发布判断时，完整读取 [references/integrated-release-contract.md](references/integrated-release-contract.md)。需要新建合同时复制 [research-release-contract.json](assets/research-release-contract.json)，再运行 `scripts/validate_research_contract.py`；合同通过不替代理论或实际 simulation evidence。

需要从零规划时，复制并填写 [assets/simulation-plan.yaml](assets/simulation-plan.yaml)。需要交付审计报告时，复制 [assets/audit-report.md](assets/audit-report.md)。模板是起点，不是已通过核查的证明。

### 有时限的审计交付

任务给出必需输出、schema 或明确检查项时，先创建并逐步填充这些工件，再开展可能耗时的扩展检查。先运行直接覆盖当前输入与不变量的最小测试集；只有实现发生变化、直接检查失败或任务明确要求时，才扩大到依赖包或完整回归。必需工件与直接验证都完成后及时结束，不用重复执行同一确定性重放来换取形式上的更多日志。

失败谱系必须保留层级。对每次 attempt 记录顶层状态以及底层 termination_reason、是否触发 fallback、事件数和异常字段；汇总时分别统计每个状态和每个终止原因。budget_exhausted、solver_failed 等顶层状态不能替代更具体的 node_budget、iteration_limit、refinement_schedule_complete_with_open_gap 等终止原因，也不能把不同原因合并成一个总数。

只有任务明确要求归档复现 auditor、审计报告与 replay 工件时，才读取
[bounded-reproduction-audit.md](references/bounded-reproduction-audit.md) 的对应配方。
普通离线工作不因时长、是否联网或“最终”措辞自动增加文件和重复运行。

## 执行核心工作流

以下步骤按依赖关系和工作模式应用。局部实现修复只重验受影响的不变量、结果和下游；全流程研究仍完成所有适用的科学性关卡。缺陷阻断相应推断或正式计算，已授权的修复、诊断和无关分支继续推进。

### 1. 建立理论—实现契约

复用现有设计，按当前任务记录必要的理论—实现契约。既有研究的未知事实标为“未核实”；从零设计时可以选择有依据的 DGP、指标和实现默认值，明确它们是设计选择，不把它们写成已有结果。

- 研究主张：模拟要支持、区分或证伪什么？
- 对象：estimand、原假设、备择、参数空间、nuisance、信息集和渐近序列。
- 程序：估计量/统计量、标准化、方差、临界值、调参、选择与校准。
- 真值：每个 DGP 下哪些量已知，哪些需独立高精度近似？
- 代码映射：公式对应哪个函数、配置字段和结果列？

至少建立以下映射：

`论文公式/主张 → DGP 场景 → 实现位置 → 预期不变量 → 输出字段 → 表图`

每个 simulation cell 还必须绑定 method-specific null、estimand、population/conditioning、index/norm、DGP truth、fixed/local regime、method/comparator role、phase 和 target metric。同一 DGP 可以承载目标方法与 diagnostic comparator；只有非法角色迁移才使 size/power claim 失效，不能让 comparator 的存在污染合法目标 cell。

若理论、正文与代码对参数化、样本分割、依赖结构、网格或 bootstrap 的定义不同，先判为阻断项；不要继续用算力掩盖对象不一致。

### 2. 按 ADEMP+R 冻结设计

按以下顺序审查并记录理由：

1. **Aims**：每个实验只回答明确问题；区分 proof-of-concept、压力测试和论文主结果。
2. **Data-generating mechanisms**：将每个场景绑定理论主张或有限样本风险；包含基准、局部偏离、强偏离、假设违反和数值困难场景。
3. **Estimands/targets**：写出真值、识别和 null/alternative；不要用生成参数冒充不同的目标参数。
4. **Methods**：包含 proposed、相关 benchmark、oracle/upper bound 和关键消融；给所有方法公平且可复现的调参预算。
5. **Performance measures**：预先指定 bias、RMSE、size、power、coverage、区间长度、运行时间和失败率中的相关项及公式。
6. **Reproducibility**：冻结配置、随机流、软件环境、代码版本、逐次输出和汇总规则。

不要在看到正式结果后无痕改变 DGP、方法、指标或图表范围。必要修改要新建 design version，并解释为什么改变。

涉及第一阶段或学习方法时，按 scientific-principles 的“因素设计”区分真函数难度与检验信号难度，检查 DGP 真值是否给可行 learner 额外信息。主要 power family 使用适用的同族 null anchor；额外 null 压力设计和 oracle 诊断不能替代该配对。

### 3. 画出随机性与数据复用图

对每个随机对象标明“共享”或“独立”以及科学理由：

- 不同 replication 必须独立或使用经论证的随机化设计。
- 同一 replication 内比较方法时，通常共享 DGP draw；这使比较配对且更精确。
- 同一路 bootstrap process 的所有 index 必须共享 observation-level multipliers，保留协方差核。
- 内外层 bootstrap、训练/测试、selection/calibration 等需要独立时，使用不同命名 stream。
- 自适应选择和最终校准不得因误用同一随机 bank 产生过拟合；若故意同样本学习，必须有相应理论或明确降格为探索性结果。

检查 stream key 是否由稳定元组构成，例如
`(design_version, stage, scenario, sample_size, replication, stream_role)`；不得依赖易碰撞的手工线性 seed 算术、worker 执行顺序或 Python 进程哈希。

正式实现把键扩展到 config/RNG schema、cell、fold、resample 与 draw identity。用 serial、不同 worker 数、乱序调度和中断恢复做 metamorphic test；按 replication ID 排序后随机输入和结果应一致。显式 shared-pair ID 是方法比较共享随机流的唯一入口。

### 4. 审查实现与失败语义

逐层检查：

- 统计层：公式、尺度、中心化、标准化、投影/估计效应、临界值和 p-value。
- 算法层：优化目标、初始化、收敛、容差、边界、非有限值与 fallback。
- 实验层：场景网格、replication ID、随机流、配对、并行、resume 和聚合。
- 交付层：配置指纹、环境、原始逐次结果、日志、表图生成和版本记录。

禁止静默跳过失败、用不同方法替代失败方法、把失败 rep 从分母删除却不披露、或在 checkpoint 中只记累计次数不记已完成 ID。将“统计方法失败”“优化未收敛”“环境不兼容”“代码异常”分别记录。

Checkpoint 只原子提交 schema 完整、checksum 匹配的 terminal payload；resume 以 expected IDs 减去唯一 valid terminal IDs 为准。Solver/retry transition graph、触发条件、允许变更、attempt 上限和 failure treatment 都属于版本化 method object。迟到 worker、partial-as-complete、同 ID 异 checksum、结果依赖重试和 survivor-only reporting 都是独立 root errors。

可先运行：

```bash
python scripts/validate_manifest.py path/to/simulation-plan.yaml
python scripts/audit_results.py path/to/per_replication.csv --expected-reps 2000
```

准备 manifest 或处理预检发现时，读取 [manifest-preflight.md](references/manifest-preflight.md)。失败政策的文字解释、已声明设置和实际执行记录分别核验。

脚本只做结构和结果完整性检查，不能替代理论核查或人工阅读。

### 5. 分阶段验证

按顺序执行，不得从“能运行”直接跳到正式 power：

1. **单元测试**：已知解析量、projection/orthogonality、尺度、p-value 和种子映射。
2. **metamorphic/invariance 测试**：理论上等价的 DGP 或参数变换应给数值等价结果。
3. **smoke test**：每个分支至少一次，确认输出 schema、失败语义和 resume。
4. **数值 pilot**：测精度、收敛、耗时和资源；只允许调整实现性能，不偷偷改变正式统计设计。
5. **size/coverage gate**：检验和置信区间先验证 null size 或 coverage。
6. **正式 power/风险实验**：仅在相关方法通过有效性 gate 后运行。
7. **独立复核**：用不同随机 stream、较大 bootstrap draws、替代实现或解析 special case 复核代表性格点。

不能通过 size 的方法不得把原始拒绝率直接宣传为 power。选择 size-adjusted power 时，同时报告未调整 size 和调整规则，并说明它回答了不同问题。

### 6. 按 Monte Carlo 精度决定重复次数

不要把 500、1000、2000 或 10000 当作通用“论文级”数字。根据关键指标的目标 MCSE 预先选择 replication 数。

启动说明和结果摘要同时交代 phase、目标精度、planned/actual R 与剩余任务；pilot/formal 由实验目的、设计冻结和结果使用方式定义，不能仅按 R 或输出目录命名升级。

对 rejection/coverage proportion \(\widehat p\)：

\[
\operatorname{MCSE}(\widehat p)
=\sqrt{\widehat p(1-\widehat p)/R}.
\]

预期比例为 \(p_0\)、目标 MCSE 为 \(e\) 时，使用

\[
R\ge p_0(1-p_0)/e^2;
\]

未知 \(p_0\) 时用最坏情形 \(0.25/e^2\)。对配对方法差异，直接对 replication-level 差值计算 SE，不把两个独立 MCSE 粗暴相加。

报告每个主要结果的有效分母、MCSE 或 Monte Carlo interval；若 MCSE 大到可能改变论文结论，判为未就绪。

`planned_R != actual_R` 本身不是错误；隐瞒差异、用 planned_R 计算 MCSE、混用有效集合或把 partial/duplicate IDs 计入才是错误。Pointwise、grid-joint 和 continuum simultaneous coverage 使用不同 replication-level event。比较优势或 dominance 时，在共同有效 paired IDs 上计算差值不确定性，并先满足同 null、有效 critical law 与 same-size calibration。

### 7. 核对结果与论文

从逐 replication 数据重算汇总，不只读取最终表格。检查：

- 每个 `(scenario, method, replication)` 唯一且完整；
- seed/stream 无意外碰撞，配对关系符合设计；
- 失败、超时、fallback、非有限值和丢失 rep 均进入报告；
- 平均值未被少数极端重复驱动；
- 表、图、正文中的样本量、方法名、统计量名、DGP 和分母一致；
- “robust”“omnibus”“power gain”“uniform”等措辞没有超过模拟范围；
- 离散网格、截断分布、边界修正和实现近似均明确披露。

## 应用发布关卡

全流程或发布审计按照 [references/audit-rubric.md](references/audit-rubric.md) 给出适用的 G0–G5 结果；局部预算、解释或实现修复不启动完整发布判断。任何 Fatal 问题、未通过的有效性 gate、无法重现的 seed/配置或未披露的失败都禁止给出“publication-ready”。

不要使用机械总分掩盖致命问题。最终 verdict 只使用：

- **通过**：当前范围内的所有必要证据可核验，且无阻断项。
- **有条件通过**：主结论可保留，但列明发布前必须完成的有限修复与验收标准。
- **未通过**：一个或多个问题会改变 size、coverage、power、目标对象或可复现性。
- **证据不足**：缺少代码、配置、逐次结果、理论定义或环境，无法判断。

新建或修改验证器、发布合同或状态传播逻辑时，运行 CLEAN、SINGLE、COMPOSITE、PARTIAL、false-clean 和 false-red fixtures；普通结果交付复用仍适用的验证器测试证据，并核验本次实际输入与产物。Expected composite roots 必须从已验证 singles 与依赖 DAG 自动合成；同时核对 exact stale/not-evaluable descendants，防止首错遮蔽、漏传和过宽失效。分别输出 `implementation_reproducibility`、`simulation_inference_eligibility` 与 `artifact_freshness`；代码可重放不能升级未核验的 theorem、bootstrap、local-power 或 continuum claim。

## 生成审计输出

完整审计报告先给 verdict 和最严重问题，再按适用项组织；局部解释、预算或单项修复只交付其实际范围，不强制七段报告：

1. 审计范围与未读材料；
2. 理论—实现契约表；
3. Fatal / Major / Minor findings，每项包含证据、影响、最低修复、验收测试；
4. G0–G5 gate 表；
5. Monte Carlo precision 与有效分母；
6. 可复现性清单；
7. 按优先级排序的下一步。

审计记录区分已核验事实、代码推断、领域原则和待核实项，可按需要使用相应标签；普通解释不必逐句加标签。不要把对话摘要或文件名当成论文技术命题已经核验的证据。
