# 科学数值模拟原则

## 失败谱系最低要求

同时保留父级 attempt 状态和所有可得的终止原因。逐次证据至少包含 termination_reason、是否使用 fallback、事件数，以及异常或明确的空异常。分别汇总状态计数与终止原因计数，并让两者各自与原始 attempt 清单对账。顶层资源耗尽标签不能抹去求解器更具体的终止原因。

有时限的审计应尽早建立必需输出 schema，优先核验任务要求的不变量。只有相关实现变化、直接检查失败或任务明确要求时，才扩大到依赖包测试。

若请求同时要求 supplied tests 和新建 deterministic auditor，先建立能读取冻结配置与证据的 auditor，再运行一次覆盖 supplied tests 的命令；不要先跑全量 discovery、再重复跑其子模块。测试通过后直接执行两次 auditor 并比较完整输出 bytes，之后补齐报告和定向终检。

## 目录

1. 证据基础
2. 把模拟当作实验
3. ADEMP+R 设计
4. 场景、比较方法与公平性
5. 指标与 Monte Carlo 精度
6. 分析和报告
7. 最低论文披露项

## 1. 证据基础

本规范以 Morris、White 和 Crowther (2019) 的 ADEMP 框架为通用骨架，并吸收 Burton et al. (2006) 关于模拟设计与报告的原则。Morris et al. 将模拟研究明确视为经验实验，要求预先定义 aims、data-generating mechanisms、estimands/targets、methods 和 performance measures，按关键指标的 Monte Carlo standard error 选择重复次数，保存随机状态并报告模拟不确定性。

主要来源：

- Morris, T. P., White, I. R., & Crowther, M. J. (2019). *Using simulation studies to evaluate statistical methods*. Statistics in Medicine, 38, 2074–2102. DOI: 10.1002/sim.8086. 开放版：https://discovery.ucl.ac.uk/id/eprint/10066118/
- Burton, A., Altman, D. G., Royston, P., & Holder, R. L. (2006). *The design of simulation studies in medical statistics*. Statistics in Medicine, 25, 4279–4292. DOI: 10.1002/sim.2673.

下述对 econometric tests、quantile processes、bootstrap 和 adaptive selection 的具体扩展属于领域原则与本项目经验综合；不要误归因给上述论文。

## 2. 把模拟当作实验

模拟结果不是“真相表”，而是由有限 replication 得到的估计量。每个性能指标都同时受以下因素影响：

- 设计选择：DGP、样本量、参数、比较方法和调参；
- 实现误差：公式、随机流、优化、失败处理和环境；
- Monte Carlo error：有限 replication 带来的抽样误差；
- 内层近似误差：bootstrap/permutation draws、数值积分、网格和优化；
- 选择行为：在看到结果后改变场景、指标或展示范围。

科学模拟必须允许第三方回答：为什么运行这些场景、每个结果估计什么、误差有多大、失败了什么、怎样精确或统计地复现。

## 3. ADEMP+R 设计

### Aims

为每个目标写出可证伪句式：

- “在满足假设 A 的 null DGP 下，检验的 size 是否接近 \(\alpha\)？”
- “在局部方向 \(h\) 下，方法相对 benchmark 的配对 power gain 是否为正？”
- “违反 overlap/mixing/smoothness 后，coverage 如何退化？”

区分：

- proof-of-concept：证明方法在理想条件下能工作；
- comparative evaluation：公平比较方法；
- stress test：寻找失效边界；
- implementation validation：检查代码是否实现理论；
- computational benchmark：比较耗时、内存和扩展性。

不要让一个场景承担多个含糊目的。

### Data-generating mechanisms

为每个 DGP 写明：

- 完整联合分布或递推式、初始条件、burn-in 和依赖结构；
- 参数值、样本量、维度、误差分布、异方差/重尾/删失/缺失机制；
- 场景属于 null、fixed alternative、local alternative、tangent/absorbed direction 还是假设违反；
- 理论主张或风险与该场景的一一映射；
- 任何截断、winsorization、标准化或总体投影；
- 真值的解析来源或独立高精度近似程序。

至少覆盖：

1. 可由解析结果验证的基准；
2. 与主理论直接对齐的 null；
3. 代表性局部和固定备择；
4. 关键假设逐项违反的压力场景；
5. 数值困难场景，如弱信号、近奇异、重尾、边界、少簇或高持久性；
6. 与潜在应用相近的现实场景。

不要只挑 proposed method 擅长的备择。若用 training dictionary 学习方向，另设 dictionary 外的真实备择。

### Estimands and targets

区分：

- 生成参数与目标参数；
- estimand、estimator、test statistic 和 performance measure；
- pointwise、uniform、conditional 和 unconditional target；
- finite-grid 目标与 continuum 理论目标；
- model parameter 与 pseudo-true parameter。

若真值需模拟得到，使用独立随机流和足够大的辅助模拟，使其误差相对主实验可忽略，并报告构造方法。

### Methods

比较集合通常包括：

- proposed method；
- 最相关的现有 benchmark；
- 简单且透明的 baseline；
- oracle 或理论上限（若可行）；
- 关键组件消融；
- 故意错误的实现只可作为诊断，不可冒充竞争方法。

为每个方法冻结版本、调参、初始化、优化预算、停止规则和失败规则。避免给 proposed method 精细调参，却对 benchmark 使用明显不利的默认值。

### Performance measures

让指标回答目标：

- estimation：bias、empirical SD、mean reported SE、RMSE/MSE、coverage、interval length；
- testing：type-I error/size、power、p-value distribution、critical-value error；
- selection：选择频率、regret、oracle gap、out-of-dictionary performance；
- computation：runtime、memory、iterations、convergence/failure rate；
- reproducibility：missing/duplicate replications、seed collisions、resume consistency。

写出公式并明确分母。不要把 distance covariance squared 标成 distance correlation，也不要把 pathwise separation 标成 power dominance。

### Reproducibility

冻结：

- design version 与配置指纹；
- 代码 commit/hash 与依赖环境；
- RNG 算法、master seed、stream key 和配对规则；
- 每个 replication 的输出、状态和错误；
- 从逐次结果生成表图的单一流水线；
- 原始、清洗、汇总和展示数据的层级。

## 4. 场景、比较方法与公平性

### 因素设计

选择 fully factorial、fractional factorial 或 one-factor-at-a-time 时说明理由。避免组合爆炸导致每个格点重复不足，也避免只改变一个因素而错过交互。

把场景表至少写成：

| scenario | claim/risk | null/alternative | factors | expected signal | primary metric |
|---|---|---|---|---|---|

涉及 nuisance learner 时，将两类因素分别记录：

- **真函数估计难度**：实际待估的条件均值、条件分位数或其他 nuisance 的线性、平滑、交互、异方差和维度；
- **检验信号难度**：依赖的位置、形状、强度、局部缩放及是否落入保留 instruments 的盲方向。

生成式里出现非线性项，不足以判定 nuisance 非线性。例如给定 Z，V 与 ε 独立标准正态，且 Y=m(Z)+s(Z){ρ(Z)V+√(1−ρ(Z)²)ε}、s(Z)>0、|ρ(Z)|≤1 时，Y 的条件分位数是 m(Z)+s(Z)Φ⁻¹(τ)。非线性的 ρ(Z) 可以改变与 V 的条件依赖，却没有改变这条真分位数曲线；以解析真值或独立可信计算分类。

检查每个可行 learner 的输入、基底和调参规则是否用了应用中不可见的 DGP 真函数信息。正确设定的基准有诊断价值，可以保留；若要评价第一阶段稳健性，则在约定范围内让同一组预先指定且适用的 learners 面对不同真函数 regime，而非按每个 DGP 事后挑选刚好正确的 learner。方法本身依赖已知结构时说明其适用范围，不强行把所有方法放入不适用场景。真分位数、真参数或真信号可供 oracle 与误差诊断使用；oracle 的好表现不证明可行方法有效，也不是未经证明的功效上界。

### Power family 的 null anchor

主要 power family 的拒绝率应与同族、同 nuisance regime、同 learner/调参/校准、同样本量与维度的 null anchor 对照。若信号参数取零确实产生目标方法的 null，使用该零信号单元；先核验其真值，不能仅凭参数名为零分类。若该 family 无合法零信号端点，构造并说明最接近的合法配对 null，或明确现有设计不能分离 size distortion 与 power。无需把每个正信号强度再变成不同 null，也无需重复运行配置及来源一致且已核验可复用的 anchor。

额外 null stress designs 可比 power 覆盖更多假设风险，不要求两张 DGP 表逐行相同；它们不能替代上述主设计基准。不同方法检验不同 null 时按方法单独分类，保留 diagnostic comparators 的解释边界。比较方法共享 DGP draw 属于下面的随机配对；它与 null/alternative 的设计匹配是两个不同条件。

### 公共随机数与配对

同一 replication 内让方法共享 DGP draw，通常可降低方法差异的 Monte Carlo variance。若两方法可共享 bootstrap multipliers 且不改变各自边际分布，也可配对；否则保持独立并说明。

配对比较以 replication-level contrast 为分析单位。例如 rejection difference：

\[
D_r=I_{r,A}-I_{r,B},\qquad
\widehat\Delta=R^{-1}\sum_rD_r,
\]

\[
\operatorname{MCSE}(\widehat\Delta)
=s_D/\sqrt R.
\]

不要把同一批数据上两个 rejection rate 当独立比例比较。

### 公平调参

检查：

- 所有方法是否看到相同信息；
- 是否对 benchmark 使用同等训练预算和数据；
- 是否用测试数据调参；
- oracle 是否明确标为不可行 benchmark；
- tuning failure 是否被记录；
- proposed method 是否从目标备择泄漏信息。

## 5. 指标与 Monte Carlo 精度

### 比例指标

对 size、power、coverage 和 failure rate：

\[
\widehat p=R^{-1}\sum_{r=1}^RI_r,
\quad
\operatorname{MCSE}(\widehat p)
=\sqrt{\widehat p(1-\widehat p)/R}.
\]

设计阶段用预期 \(p_0\) 或 worst case \(0.5\) 选 R：

\[
R\ge p_0(1-p_0)/e^2.
\]

例：若预期 size 为 0.05 且希望 MCSE 不超过 0.005，R 至少约 1900。若要求所有比例无论真值如何 MCSE 不超过 0.005，则 R 至少 10000。

这些数字只演示精度换算，不定义论文资格。phase 由用途和设计过程决定：实现/资源计时、诊断调试、探索性比较与冻结后的确认性评估应在交付时明确；名称为 formal 或 R 较大不证明独立校准与确认性资格。增加 R 只能提高该配置下指标估计的精度，不能修复 size distortion、错误 DGP 或失效的 bootstrap。

启动前说明目标 MCSE、R/B 的理由和下一阶段；汇总时报告实际有效分母、已完成/尚未完成单元及证据用途。用户授权调整 R/B 后分别更新精度和预算，保留约定的场景覆盖；不得因少跑重复而改称缩减设计已完成，也不得因 R 低于某个惯用值自动拒绝有足够精度的结果。

### 均值型指标

若性能指标是 replication-level 量 \(Z_r\) 的均值：

\[
\widehat\mu=R^{-1}\sum_rZ_r,
\qquad
\operatorname{MCSE}(\widehat\mu)=s_Z/\sqrt R.
\]

因此 bias 可令 \(Z_r=\widehat\theta_r-\theta\)，MSE 可令 \(Z_r=(\widehat\theta_r-\theta)^2\)。RMSE 是 MSE 的非线性变换，可用 delta method 或基于 replications 的 bootstrap 估计 MCSE，并说明方法。

### 内层 resampling 精度

对 B 个 bootstrap/permutation draws：

- 报告 B、权重分布、分位数定义和有限样本 p-value 公式；
- 用 plus-one 形式避免零 p-value：\((1+\#\{T_b^*\ge T\})/(B+1)\)，除非理论明确规定其他随机化；
- 检查最小 p-value \(1/(B+1)\) 和分位数离散度是否足以支持显著性水平；
- 在代表性格点用更大 B 复核结论；
- adaptive selection 的 Monte Carlo noise 必须进入选择一致性或被样本/stream 分离处理。

## 6. 分析和报告

### 从逐次结果开始

保留每个 `(design_version, scenario, method, replication)` 的：

- seed/stream key；
- estimate、SE、CI、test statistic、critical value、p-value、rejection；
- tuning、迭代、收敛、耗时、warnings 和 failure type；
- learned object 的必要摘要；
- 配置指纹和代码版本。

聚合前验证唯一性、完整性和版本一致性。

### 失败不是缺失噪声

分别报告：

- DGP 生成失败；
- estimator/statistic 未定义；
- 优化不收敛；
- bootstrap 失败；
- 环境或资源失败；
- 代码异常。

给出 planned、attempted、successful 和 metric denominator。默认不要删除失败 rep 后只在成功样本上报告性能。若必须定义 conditional-on-success 指标，同时报告 unconditional failure rate 和替代编码的敏感性。

### 论文表述

正文至少说明：

- ADEMP 各项和选择理由；
- R 与 MCSE 依据；
- B、随机流、并行和失败处理；
- software/version/hardware 中影响结果的部分；
- 逐次结果和代码如何获得；
- 所有实现近似与理论差异。

表图并排展示 competing methods，并在表头/注脚给出有效 R、MCSE 或区间。不要只展示“赢”的场景；主文与附录的选择规则需预先说明。

对异常数值、方法间分歧和明显的规格敏感性，先核算实际结果，再区分已验证机制与可能解释，并随该表交付必要说明。稳健性结论绑定实际运行的配置组合：分别加密 grid 和增加 cutoffs，只支持这两次单因素变更；未运行的联合组合保持“未运行”，不能拼接或外推一个联合 p 值，也不能概括为所有组合均稳健。额外联合实验是否必要取决于当前主张和用户范围，不把它自动增加为所有项目的固定要求。

## 7. 最低论文披露项

- 研究目标和对应主张；
- 完整 DGP 与参数网格；
- estimand/null/alternative 真值；
- 方法实现、版本、调参和失败规则；
- sample size、replications、bootstrap draws、nominal level；
- RNG、seed/stream、配对和并行；
- 每项指标公式、分母和 MCSE；
- size/coverage gate 及其判定；
- 代码、配置、逐次结果和表图流水线；
- 理论与实现不一致、离散化、截断或近似；
- 所有负结果、失败率和敏感性分析。
