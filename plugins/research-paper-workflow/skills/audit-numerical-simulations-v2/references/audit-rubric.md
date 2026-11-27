# 数值模拟审计量表

## 目录

1. 发现严重度
2. G0–G5 发布关卡
3. 证据状态
4. 标准输出
5. 最低验收测试

## 1. 发现严重度

### Fatal

满足任一项即阻止正式运行、power 解读或投稿：

- 代码计算的 estimand、null、statistic 或 critical value 与理论不同；
- DGP 不能识别声称的参数，或 nuisance Jacobian/variance 必然奇异；
- bootstrap/标准误没有复制实际依赖或选择机制，导致 size/coverage 无依据；
- adaptive selection 与 final calibration 数据复用违反所依赖理论；
- seed 碰撞、并行重复、checkpoint 逻辑或版本混合使 replication 身份不可恢复；
- 静默 fallback/丢弃失败足以改变性能指标；
- 相关方法未通过 size/coverage gate，却把拒绝率解释为 power/coverage；
- 结果无法追溯到唯一代码、配置和逐次输出。

### Major

可能实质改变数值结论，但通常可局部修复：

- DGP 范围不足以支持强主张，缺 oracle、关键 benchmark 或假设违反场景；
- R/B 精度不足，MCSE 可能改变方法排序或显著结论；
- 比较方法调参或计算预算明显不公平；
- 未报告重要失败、极端值、运行时间或配对不确定性；
- finite grid、截断、边界或标准化与论文表述不一致；
- pilot 后改变正式设计但未版本化。

### Minor

不太可能改变核心结论，但影响清晰性或复现：

- 命名、单位、表头、注脚或配置说明不准确；
- 缺次要敏感性分析；
- 表图可读性、文件组织或日志信息不足；
- 非关键环境信息缺失。

### Note

建议或可选增强，不作为通过条件。不得用大量 Note 淹没 Fatal/Major。

## 2. G0–G5 发布关卡

### G0 理论—实现契约

通过条件：

- estimand、null/alternative、nuisance、statistic、variance、critical value 和选择规则可明确定义；
- 每个对象都有论文—代码—输出映射；
- DGP 与理论假设/目标一致；
- 无未解释的参数化、网格、依赖或样本分割差异。

### G1 随机性与实现完整性

通过条件：

- 解析 special cases、单位测试和关键 invariance 通过；
- seed/stream 唯一且配对关系正确；
- 1-worker 与多-worker 在相同 replication IDs 上结果一致（允许已声明的浮点容差）；
- resume 不重复、不跳过、不覆盖；
- 失败不静默，配置指纹阻止版本混合。

### G2 Pilot 与数值稳定性

通过条件：

- 所有方法、DGP、样本量、stream role 和输出分支至少 smoke 一次；
- 非有限值、优化、边界、近奇异和环境兼容性已有处理；
- pilot 给出单 rep 耗时、内存、失败率和正式预算；
- pilot 只调整计算策略，统计设计改变已新建版本。

### G3 有效性 gate

对 test：所有拟比较 power 的方法先在相应 null 下验证 size。

对 CI：先验证 coverage 与 reported-SE calibration。

判定带必须预先写明，并结合 MCSE/Monte Carlo interval。不要把某个固定经验区间（如 0.035–0.065）当成通用标准；其宽度应由 nominal level、R、场景数量、同时检查策略和科学容忍度决定。

### G4 精度、完整性与稳健性

通过条件：

- 关键指标达到预设 MCSE；
- 所有计划 rep 完整，或任何减少有解释且不依赖结果；
- 报告 failure rate、有效分母和极端重复影响；
- 代表性格点通过更大 B/R、替代 seed 或独立实现复核；
- 配对比较使用 replication-level contrasts。

### G5 论文与复现包

通过条件：

- 正文/附录的 DGP、参数、方法、R/B、结果与代码一致；
- 所有主张不超过场景和指标支持范围；
- 一条命令或明确流水线可从配置和逐次结果生成表图；
- 提供环境、代码版本、配置、原始逐次结果、日志和审计报告；
- 不隐藏失败、负结果、实现近似或设计版本变化。

## 3. 证据状态

- `[已核验]`：直接读取相关公式、代码、配置、逐次结果或可复现运行。
- `[代码推断]`：从控制流/变量映射推断，尚未用数值测试确认。
- `[领域原则]`：通用统计或计算规范，不是目标论文的作者陈述。
- `[待核实]`：缺材料、版本不明、结果仅来自摘要/对话或无法定位。

对话摘要可用于发现风险，但不能独立支持“某篇论文证明/实现了某命题”。

## 4. 标准输出

### Verdict

使用且只使用：通过 / 有条件通过 / 未通过 / 证据不足。

### Findings

每项使用以下字段：

- `ID`：如 F-01、M-02。
- `Severity`：Fatal/Major/Minor/Note。
- `Evidence state`。
- `Observed`：可定位证据。
- `Why it matters`：影响 estimand、size、power、coverage、计算或复现中的哪一项。
- `Minimum fix`：最小充分修复，不给泛泛建议。
- `Acceptance test`：修复完成的可执行判断。

### Gate table

| Gate | Status | Evidence | Blocker | Acceptance test |
|---|---|---|---|---|
| G0 | pass/fail/not checked | ... | ... | ... |

### Precision table

| Scenario | Method | Metric | Effective R | Estimate | MCSE | Target | Status |
|---|---|---:|---:|---:|---:|---:|---|

## 5. 最低验收测试

根据任务选择，不要机械全部运行：

- 解析 moment/variance/drift 与代码数值一致；
- null 下 sample moment 均值接近理论值；
- tangent/absorbed DGP 与 null 在相同底层随机数下给相同 residual/process；
- projection 后与 nuisance score 正交；
- 同一 bootstrap path 的 index covariance 得到保留；
- selection/calibration stream 实际不重叠；
- weight-specific critical value 随 weight 重新计算；
- 1-worker、2-worker、分片、resume 和 fresh run 对同一 rep 一致；
- seed ledger 无跨 `(scenario, replication, stream_role)` 碰撞；
- 失败 rep 可按 ID 和随机状态重放；
- 表图从逐次结果可重新生成；
- size/coverage gate 与预设规则一致；
- 代表性格点增大 B/R 后结论稳定。
