# 计量模拟的常见核查问题

## 目录

1. 证据边界
2. Quantile Independence Test
3. Quantile Uniform Inference
4. Adaptive CvM
5. 跨项目共同原则

## 1. 证据边界

以下场景用于排查分位数过程和自适应检验中常见的实现问题。
针对当前研究的结论需要回到实际数据生成过程、代码、配置和逐次结果。

## 2. Quantile Independence Test

### 核查场景

1. 手工线性 seed 编码在不同 DGP、signal 和 sample size 间发生碰撞；同一格点内估计可能仍近似无偏，但跨格点比较产生非预期相关。
2. Checkpoint 只保存累计成功数，没有保存完成的 replication IDs；中间失败后继续会使 resume 重跑已成功 seed。
3. quantile-series fit 捕获所有异常后静默回退到 unconditional quantile；最终结果看似完整但目标方法已改变。
4. 某些 first-stage 方法在小样本 null 下 size 严重膨胀，却仍列入默认 power 方法；原始拒绝率不能直接解释为 power。
5. 环境只检查 PyTorch import 成功，但 Tensor→NumPy 的实际边界因 NumPy/PyTorch 二进制不兼容失败。
6. 名为 dCor 的实现实际计算 distance covariance squared；统计量值与论文命名不一致。
7. Cauchy 变量/结果被截断后仍被描述为 Cauchy DGP；实现改变了场景。
8. 不同维度的 Z grid 实际点数与全局配置/论文描述不一致；某些 “high-dimensional” DGP 与基准生成公式相同。
9. 理论使用 observation trimming \(\tau_0\)，代码只限制 index grid，实际相当于 \(\tau_0\equiv1\)。

### 提炼为硬规则

- 用结构化 SeedSequence/stream ledger，审计“应独立单元”的碰撞；方法间有意共享 DGP 不算碰撞。
- Checkpoint 以 replication identity 为核心，不以累计计数为核心。
- 任何 fallback 必须是预先定义的方法组成，记录触发率；否则失败并停止该单元。
- 先运行 size gate，再决定哪些方法可进入 power comparison。
- 对依赖边界做实际 smoke：tensor conversion、GPU、Parquet、multiprocessing、shell。
- 从公式检查方法名；从代码检查 DGP 真实分布，不以变量名为证据。
- 区分 index-domain truncation 与 observation trimming。
- 集群运行时按 rank 分配不重叠 rep、rank 独立写 shard、聚合验证完整性和配置指纹。

## 3. Quantile Uniform Inference

### 核查场景

1. 线性 location-scale 模拟在固定 quantile 下把 intercept 与 scale 同时当 nuisance，梯度列共线，理论要求的 \(L_\alpha\) 非奇异不成立；若实际代码逐 quantile QR，则论文参数化写错；若 pooled estimation，则现有逐 quantile influence theory 不适用。
2. GaR 的 overlapping multi-quarter outcome 引入 serial correlation，但推断使用 MDS/contemporaneous variance/iid multiplier；DGP 依赖与 bootstrap 不匹配。
3. adaptive penalty selector 用固定数量的 bootstrap rejection frequencies；固定模拟噪声可能阻碍 selector 收敛，不能无条件声称一致性。
4. 理论用随机辅助 quantile grid，代码用 deterministic dense grid；需要 Riemann-sum 或对应离散理论。
5. kernel density 辅助区间与测试 quantile 端点重合，违反离边界正距离条件，可能有不消失边界偏差。
6. 实现离散 alpha/gamma，却把 statistic 描述为 continuum/exact；有限网格只能检测网格可见方向。
7. “pathwise separation enhancement”不等价于 power enhancement，因为 critical value 也随 tuning 改变。
8. 论文中的 corrected score、长期方差和实际 nuisance estimation 必须在代码中完全一致。

### 提炼为硬规则

- 先做 identification/rank audit，再运行 Monte Carlo；生成公式能写出不代表 estimand 可识别。
- 时间序列/overlapping outcomes 用 long-run variance 与相应 dependent bootstrap，或缩小为支持 MDS 的设计。
- 选择器的内层 Monte Carlo error 是算法的一部分，必须进入理论、R 选择和敏感性。
- 理论与实现的随机/确定性积分、连续/有限网格和边界处理要一一匹配。
- 所有 power 声明必须直接比较 rejection probabilities 与各自 critical values。
- 离散实现要诚实标为 grid statistic，报告 grid-refinement sensitivity。

## 4. Adaptive CvM

### 核查场景

1. projected conditional-moment process 需要对 post-estimation influence contribution 做 multiplier bootstrap；不能对 raw moment 直接乘乘子。
2. bootstrap contribution 显式按方向中心化，observed statistic 则遵循理论使用未中心化样本和。
3. 同一 bootstrap path 的所有 index 使用同一组 observation multipliers，以保留 covariance kernel。
4. 每个 candidate weight 在 selection draws 上有 weight-specific critical value；最终 weight 选定后用全新 calibration bank。
5. 同一 replication 内所有方法共享 DGP 与适当的 multiplier banks，用 replication-level paired power gain；不同 replication 和 selection/calibration streams 独立。
6. 如果理论权重是 sample-specific，每个 outer replication 都必须重学，不能跨数据集固定一个 learned weight。
7. training dictionary 与真实评估备择分开；包含 dictionary 外 directions 以评估泛化。
8. 用总体投影和总体 \(L^2\) 范数 normalized alternatives，可避免样本随机缩放混入 signal strength；raw 版本作为敏感性。
9. 预设 size gate、tangent/null 数值等价、projection orthogonality、drift additivity、stream independence、resume 和 weight constraints 等测试。
10. learner 失败不静默回退 Uniform；保存 objective、初始化、termination、临界值、p-value、权重和错误。
11. 用 999/1999 multipliers 的代表性复核量化内层近似敏感性。
12. 若理论要求 sample splitting，核对实现的训练和检验样本是否独立。为同一样本设置独立 bootstrap banks 不能满足该条件。

### 提炼为硬规则

- 先画 selection/training/testing/calibration 的数据与随机性 DAG。
- 每个 learned/tuned statistic 都使用与其 weight/tuning 对应的 null calibration。
- 把 same-sample adaptive validity 当单独理论义务，不以 fixed-weight bootstrap theorem代替。
- 用解析 drift、tangent absorption 和 null invariance 设计 metamorphic tests。
- 正式 power 只在所有比较方法通过相应 size gate 后执行。
- 对计算昂贵 learner 先做 formal-parameter single-rep pilot，估计总成本而不启动长跑。

## 5. 跨项目共同原则

沿以下接口检查对象、算法和论文表述是否一致。

`理论对象 ↔ 参数化 ↔ DGP ↔ nuisance estimator ↔ influence/variance ↔ bootstrap ↔ random streams ↔ parallel resume ↔ 论文表述`

因此审计优先级应为：

1. 对象/识别错误；
2. 推断/依赖/选择校准错误；
3. 随机流、并行、失败与版本完整性；
4. size/coverage 与 Monte Carlo 精度；
5. 场景覆盖和比较公平性；
6. 报告、命名和排版。

不要先优化运行速度或增加重复次数，再回头确认模拟究竟估计了什么。
