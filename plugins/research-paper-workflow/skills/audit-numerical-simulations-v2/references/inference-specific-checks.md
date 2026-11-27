# 推断型模拟专项核查

## 目录

1. 理论对象与估计效应
2. 检验和置信区间
3. Bootstrap 与 permutation
4. 依赖数据
5. Quantile 与非光滑程序
6. Adaptive / learned procedures
7. Size/coverage gate

## 1. 理论对象与估计效应

### 分离四层

分别定义：

1. estimand 与识别；
2. estimator / restricted estimator；
3. influence contribution 或 moment process；
4. statistic、variance 和 critical value。

检查代码是否把估计一致性当成识别、把 raw moment 当成 post-estimation influence function，或漏掉 nuisance estimation effect。

### Point null、restriction 与 specification

- 所有参数固定的 point null：null tangent space 为零，一般无结构参数估计效应。
- 一般 restriction：只保留 null tangent directions 的估计波动；需要正确的 restricted influence function。
- specification test：null model parameters 都需估计，通常要完整 first-step correction。
- unrestricted Wald-type statistic：估计量自身仍有 influence variation；“无额外 orthogonalization”不等于“无估计误差”。

在 least squares 等特殊模型中，估计效应可表现为 instrument residualization；不要在一般 GMM/M-estimation 中把所有 orthogonalization 都称为欧氏 projection。

### Theory-code tests

- projection/orthogonalization 后与 nuisance score 的样本内积接近零；
- 解析 influence function 与数值有限差分/替代实现一致；
- null 与 model-space tangent DGP 在相同底层随机数下得到相同 residual/process；
- 原点或零方差 index 的处理在 observed statistic、variance 和 bootstrap 中一致。

## 2. 检验和置信区间

### Size、power 与 coverage

- size 必须在真正满足全部 null（包括 nuisance 和 dependence）的 DGP 下计算；
- power DGP 要明确 fixed/local alternative 及其强度单位；
- coefficient departure 与 specification departure 不可混淆；
- CI coverage 使用真实 estimand，不一定等于生成参数；
- 同时报 coverage 与 length，避免以过宽区间换 coverage；
- 报 empirical SD 与 mean reported SE，诊断 variance calibration。

### 多重性与统一推断

若统计量跨 quantiles、time、parameters 或 grid 取 sup/integral：

- bootstrap 必须复制完整 joint covariance；
- 不能给不同 index 独立 multipliers；
- 说明 finite grid 与 continuum 目标差异；
- 检查 grid refinement、boundary 和 zero direction；
- 若 claim 是 uniform size/power，场景也要覆盖 uniformity 的困难点。

## 3. Bootstrap 与 permutation

### 正确的 resampling unit

让 resampling 复制数据依赖：

- iid data：observation-level multipliers/resampling；
- clusters：cluster-level；
- time series/spatial：block、dependent multiplier 或相应 long-run covariance；
- few clusters：使用适配少簇的程序，不能机械套 iid bootstrap。

### Influence bootstrap

Multiplier bootstrap 通常乘完成估计效应修正后的 feasible influence contribution：

\[
\widehat\phi_{i,\lambda}
=g_\lambda(Z_i;\widehat\theta_H)
+\widehat{\dot\mu}_\lambda^{\top}\widehat\ell_{H,i}.
\]

对 bootstrap contribution 显式按 index 中心化；observed process 是否中心化遵循理论定义，不能混用。

同一 draw 的所有 \(\lambda\) 使用同一组 observation multipliers。若每个 \(\lambda\) 独立生成，joint covariance 被破坏。

### Critical value 与 p-value

- 对每个 weight/tuning 值重新计算其 null statistic 和 critical value；
- 最终 learned weight 固定后，用独立 calibration draws；
- 记录 quantile interpolation；
- 用 plus-one p-value 或明确的随机化公式；
- 代表性格点用更大 B 做敏感性；
- selection draws 估计的 local power 不能与 final calibration draws 混为同一任务。

## 4. 依赖数据

若 DGP 是 time series、panel、cluster 或 overlapping outcomes，检查：

- stationarity、initialization、burn-in、structural breaks；
- MDS、mixing、cluster independence 等是否真由 DGP 满足；
- overlapping horizon 是否引入 serial correlation；
- variance 是 contemporaneous 还是 long-run；
- bootstrap 是否复制 serial/cluster dependence；
- 同一时间序列内不同样本量是否嵌套，以及这种配对是否有意；
- preprocessing 是否改变 null 或 dependence。

不能在代码生成重叠未来变量后仍使用 iid multiplier，除非另有证明/修正。

## 5. Quantile 与非光滑程序

检查：

- quantile index 是否远离 0/1 或使用边界修正；
- conditional density 在目标 quantile 附近是否存在、远离零并可稳定估计；
- quantile crossing、rearrangement 和 monotonicity；
- first-stage cross-fitting 是否真正隔离 evaluation fold；
- threshold indicator 的 shrinking-strip 和 product-rate 条件；
- series/basis/NN 的维度、正则化与 estimator-specific rate；
- nuisance 参数化在固定 quantile 下是否可识别。

特别检查 location-scale DGP：固定 \(\alpha\) 时，intercept 与 scale×\(\Phi^{-1}(\alpha)\) 可能完全共线。若代码逐 quantile QR，只应估计 quantile-specific intercept；若跨 quantile pooled estimation，则理论 Jacobian/influence function 也必须 pooled。

对 trimming：限制 index grid 不等于 observation trimming。若理论使用 \(\tau(Z)=1\{Z\in\mathcal Z_0\}\)，代码必须显式乘 mask，或论文说明全局条件允许 \(\tau\equiv1\)。

对重尾 DGP：截断 Cauchy 后不再是严格 Cauchy。必须更名或披露截断。

## 6. Adaptive / learned procedures

### 学习目标与可实施检验

分开：

- training dictionary / prior；
- 真实评估 alternatives；
- learned object；
- selection criterion；
- final observed statistic；
- weight-specific calibration。

不要用真实评估备择标签训练后再声称 out-of-sample power。至少包含 dictionary 外备择。

### 数据分割

明确下列哪种理论覆盖实现：

- 独立 training/testing sample；
- cross-fitting；
- 同一样本学习 + 独立 bootstrap bank；
- 同一样本选择与校准的 selection-aware bootstrap。

“独立 selection/calibration multipliers”不能替代独立 training/testing data；它只解决随机 bank 复用的一部分。若同样本学习，需证明 learned weight 的稳定/oracle replacement 或相应 uniform bootstrap。

### 每 replication 重学

若理论权重是 sample-specific \(\widehat w_n\)，每个 Monte Carlo dataset 必须重新训练。用一个数据集训练后固定到所有 rep 估计的是不同程序。

### Weight constraints 与 fallback

- 验证非负、归一化、lower safeguard、entropy/concentration 约束；
- 记录优化 objective、hard objective、initializations 和 termination；
- 不允许失败后静默用 uniform weight；
- 若权重不可识别到加常数，score 需归一化；
- 比较 learned weight 与理论 drift/signal 图只作诊断，不当作 size 证明。

### Selection Monte Carlo noise

若 selection 依据 B/R 次模拟的估计 power，固定 B/R 的噪声可能阻碍 selector 收敛。理论需要 R 随 n 增长、严格 gap/tie rule，或将选择限定为有限样本算法而不声称一致性。

## 7. Size/coverage gate

### 预先定义 gate

基于以下内容定规则：

- nominal level \(\alpha\)；
- 每个格点 R 与 MCSE；
- 同时检查的方法/场景数量；
- 是否关心 pointwise 或 familywise false alarms；
- 科学上可接受的 material band；
- tangent/null 或 oracle checks。

可使用二项区间、预设 material band 或同时检验，但必须预先固定且解释。避免看到结果后选择最有利的 gate。

### Gate 失败

若未通过：

1. 先区分代码错误、bootstrap/variance 失效、有限样本失真和 MC noise；
2. 不运行或不解释正式 power，直到问题分类；
3. 若仍报告 raw rejection，明确它不是可比 power；
4. 可补 size-adjusted power，但保留原始 size 与调整过程；
5. 若只有特定场景失败，缩小主张范围而不是隐藏场景。
