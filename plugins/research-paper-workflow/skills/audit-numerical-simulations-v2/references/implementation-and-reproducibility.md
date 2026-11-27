# 实现与可复现性核查

## 目录

1. 软件结构
2. 随机流
3. 并行与分片
4. Checkpoint 与 resume
5. 失败语义
6. 数值稳定性
7. 测试层级
8. 结果与环境
9. 完整范围下的资源预算

## 1. 软件结构

对于十分钟以内、输入与验收文件已给定的离线复现任务，先读请求、manifest
和运行指南，随后立即创建全部必交付文件与可运行的审计程序，再执行测试。
若请求给出唯一的覆盖命令，只执行该命令一次；不要先做广泛测试发现、再重复
运行同一子集。之后按顺序完成两次重放、统计汇总、正文追踪、审计报告和最终
文件核对。首次运行解释器时就应加载所需依赖；到时间预算一半时，必交付文件
应已存在，剩余时间用于验证和修正。

`audit.md` 在开始时就写入可追踪骨架，不在重放和源码巡检之后才创建。
运行指南已经给出测试入口时先执行该入口，不预读所有测试源码；只有失败的
测试才需要定向检查。第一次重放完成后立即回填报告中的公式、定位和当前结论，
第二次重放只验证字节一致性。三个必交付文件通过一次最终定向检查后结束。

把以下层分开，避免 notebook 状态和复制粘贴污染：

- `dgp`：只生成数据和已知真值；
- `method`：给定数据和配置返回估计/检验及诊断；
- `replication`：协调一个独立实验单元及其随机 stream；
- `runner`：分片、并行、resume、日志与原子写入；
- `aggregate`：验证完整性后计算性能和 MCSE；
- `report`：只从验证后的汇总/逐次结果生成表图。

正式参数与 smoke/pilot 参数使用不同配置文件和不同输出目录。不要让 notebook 顶部的临时变量悄悄覆盖正式配置。

为配置计算稳定指纹，至少覆盖：

- design version；
- DGP/方法/指标参数；
- R、B、nominal level；
- seed scheme；
- code version；
- precision/device 和关键依赖版本。

聚合时拒绝不同指纹混合。

## 2. 随机流

### 身份键

用结构化元组派生 stream，不用加权求和式 seed：

`(master_seed, design_version, stage, scenario, n, replication, stream_role)`

`stream_role` 至少区分：

- `dgp`；
- `method_tuning`；
- `bootstrap_selection`；
- `bootstrap_calibration`；
- `permutation`；
- `auxiliary_truth`；
- `diagnostic`。

优先使用语言原生的可分裂/层级 RNG（如 NumPy `SeedSequence`、R L'Ecuyer-CMRG、Random123/counter-based generators）。若跨语言复现，只承诺输入/统计意义复现，除非明确实现相同 RNG。

### 共享与独立

建立随机性矩阵：

| 对象 A | 对象 B | share/independent | 理由 | stream key |
|---|---|---|---|---|

常见正确关系：

- 方法 A/B 的 DGP：share，用于配对比较；
- replication r/s：independent；
- 同一 bootstrap path 的不同 index：share observation multipliers；
- selection/calibration bank：independent；
- 主实验/辅助真值模拟：independent；
- worker 0/1：分配不同 replication IDs，不由 worker ID 本身定义科学身份。

### 种子审计

检查：

- 不同科学单元是否得到同一 stream；
- 同一科学单元在 worker 数变化后是否仍得到同一 stream；
- resume 是否从 rep identity 恢复而不是消费顺序恢复；
- 方法配对是否有意共享，而非碰巧共享；
- RNG 状态能否重放失败 rep。

重复 seed 不必然是错误：同一 `(scenario, replication)` 跨方法共享 DGP 是设计。错误是同一 seed 映射到多个应独立的 `(scenario, replication, stream_role)`。

## 3. 并行与分片

### 分配原则

- 以 replication ID 或不重叠的 scenario-replication 单元分片；
- 每个 worker 写独立 shard/checkpoint；
- 聚合进程只读 shard，先验证再合并；
- 不让多个进程追加同一个 CSV；
- 不依赖任务完成顺序决定结果排序或 RNG。

### 并行一致性

对相同 rep IDs 比较：

- single-worker fresh run；
- multi-worker fresh run；
- shard run + merge；
- interrupted + resume。

离散结果应逐位一致；连续结果根据已声明的 deterministic/nondeterministic backend 设容差。GPU 算子非确定性必须披露，不能只设置 seed 就声称完全可复现。

### 资源隔离

避免每个 worker 再启动全部 BLAS/OpenMP 线程导致 oversubscription。记录 CPU/GPU 绑定、线程数、内存峰值和 device/precision。不要在繁忙机器上自动提高并发。

## 4. Checkpoint 与 resume

Checkpoint 必须保存“哪些 ID 已完成”，不能只保存累计次数。

每个 rep 至少有状态：

- `planned`；
- `running`；
- `success`；
- `statistical_failure`；
- `optimization_failure`；
- `environment_failure`；
- `code_error`。

写入遵循：

1. 先写临时文件；
2. flush/fsync（风险高时）；
3. 原子 rename；
4. 更新 manifest；
5. 聚合时校验 schema、指纹和唯一键。

Resume 依据唯一键补缺，不根据已成功行数推断下一 rep。对中间失败后仍继续的运行尤其重要。

## 5. 失败语义

### 禁止行为

- `except Exception: continue`；
- 捕获错误后返回默认/无条件估计且不记录；
- 优化失败后静默回退到 baseline；
- 非有限值改为 0；
- 超时 rep 从分母删除；
- 只写文本日志，不在逐次结果保存 failure code；
- 聚合不完整 shard 仍生成“final”表。

### 必须记录

- exception type/message 和最小 traceback；
- scenario、method、replication、stream key；
- stage、iteration、objective、gradient/norm、condition number；
- fallback 是否发生及其预先定义；
- 失败前已生成的诊断，但不要把部分统计量当成功结果。

若 fallback 是方法正式定义的一部分，必须在论文中披露并报告触发率；否则默认判为失败。

## 6. 数值稳定性

### 精度与尺度

- 正式统计计算优先 float64，除非验证 float32/bfloat16 不改变结论；
- 对输入、moment、variance、loss 和 gradient 检查量级；
- 对 softmax 使用稳定 log-sum-exp；
- 对矩阵记录 rank、最小特征值/奇异值、condition number 和 regularization；
- 对极小方差方向预先定义删除/截断规则，并让统计量、bootstrap 和论文一致；
- 对分位数、核密度和边界使用明确的 interpolation/bandwidth/boundary convention。

### 优化

冻结：初始化、学习率、步数/容差、patience、梯度裁剪和 retry。区分：

- 正常达到 max iterations；
- 收敛到稳定 objective；
- 非有限 objective/gradient；
- 不同初始化给出显著不同解；
- 约束违反。

若算法预算固定，达到 max steps 可作为一种成功终止，但必须记录，不得把它冒充数学收敛。

### 环境兼容

不能只用“import 成功”判断依赖兼容。实际执行关键边界：tensor↔NumPy、CPU↔GPU、Parquet、LaTeX、multiprocessing、JIT/编译器和旧 shell。

## 7. 测试层级

### 解析与单元测试

- DGP moments/quantiles/covariances；
- estimator 在已知 special case 的解；
- statistic scaling 与 variance；
- bootstrap centering 和 p-value；
- normalized direction 的投影与范数；
- seed mapping 无碰撞。

### Metamorphic tests

不依赖完整真值，而检查理论不变量：

- 数据/参数平移或重标度后的等价性；
- tangent alternative 被受限估计完全吸收；
- permutation of observations/index order 不改变统计量；
- 组合 drift 的线性/可加性；
- 单/多 worker 与 resume 一致；
- old/new vectorized implementation 一致。

### Statistical tests of code

用足够 repetitions 检查：

- PRNG uniform/normal 生成的基本 moments（只作 sanity check）；
- null size 与解析/已验证 reference implementation；
- bootstrap covariance 与 empirical covariance；
- known oracle ordering；
- failure injection 后聚合是否拒绝不完整结果。

不要把某次随机测试未拒绝当成代码正确证明；设置可重现 seed 和误报控制。

## 8. 结果与环境

逐次结果建议包含：

`design_version, config_fingerprint, code_version, scenario_id, method_id, replication_id, seed_key, status, failure_type, estimate, se, ci_low, ci_high, statistic, critical_value, p_value, reject, runtime, iterations`

另存：

- resolved config；
- environment lock/list；
- stdout/stderr 或结构化日志；
- shard manifest 与聚合审计；
- table/figure 生成命令；
- 硬件和线程设置；
- 所有修改历史或 design changelog（可在实验 manifest 中，不需额外文档）。

发布前从空输出目录重跑一个小而完整的复现子集，确认没有依赖 notebook cache、绝对路径或未提交文件。

## 9. 完整范围下的资源预算

用户询问全部实验、剩余任务或工期时，先从现有设计和最新已接受反馈恢复其范围，再计算。实验矩阵至少覆盖约定的 family/regime、方法、信号、样本量、维度、阶段与 R/B；正文、附录、昂贵 learner、必要诊断及失败重跑只按用户已约定的范围纳入，不因手头只有低维/便宜方法的计时而删减。尚未冻结的设计单列待定量和区间，不能悄悄选定较小方案，也不把资金预留的上沿组合当作已批准的新实验。

按已有科学单元 ID 划分“已完成且可复用”“待补”“需重跑”，说明扣除和重跑依据。复用核对 DGP、learner、网格、校准、代码/配置版本、有效 rep IDs 与所需证据角色；文件存在或同名不等于可复用。已验证且依赖未变的单元不重复计费。预算表可用 [compute-budget-worksheet.md](../assets/compute-budget-worksheet.md)，或直接复用项目已有等价表。

### 计算量与计时依据

按真实执行结构建立互不重复的计算组：多个统计量/显著性水平可能共享拟合和同一 bootstrap process，不把结果列数当独立任务数。共享计算只有在算法与随机性合同允许、实现确实复用时才扣除；不同 learner、fold、训练 seed 或独立校准 bank 的工作仍分别计入。先给每组剩余 replication 数 N，再按计时拆分，例如

T_work ≈ Σ_g N_g {t_fit,g + t_stat,g + B_g t_resample,g}。

若 resample 会重新拟合，t_resample 必须包含该拟合；若调参、warm start 或批处理非线性缩放，则按实现修正并说明。改变 R 通常同时减少拟合和 resampling，改变 B 只减少相应内层工作，因此不能未经计时把 R/B 同时减半直接换算为工期四分之一。

计时记录正式规格、机器/device、线程、并发、峰值内存、有效单元数和计时范围。可用短 pilot 覆盖预计主导成本的样本量、维度及昂贵 learner；未测分支给有依据的上下界并标明外推。测速只缩小测量集合，不缩小总预算矩阵。只求预算不启动长跑；新机器无实测时按吞吐量情景报告，不凭内存、核心数或设备名称承诺精确天数。

### 资源、工期与价格

- 并发同时受实际 CPU/GPU 配额、每 worker 线程、峰值内存、共享开销和机器当前负载约束；先给系统与其他工作留资源，再用实测吞吐量确定并发，不按核心数直接假定线性提速。
- 将计算总工作量、资源分配后的 wall time 与费用分别报告。单线程 CPU 工作秒可换算核小时；多线程、整节点或 GPU 计费按实际占用/申请单位与平台规则计算，不混用 worker 小时和核小时。GPU 无同规格有效计时，不能假定更快或更省钱。
- 分开列开发/实现验证、排队/资源申请、实际计算、失败重跑与结果整理的时间。高优先级或更多请求核心不能保证排队结束时间；并行可缩短计算而不必减少总工作量。
- 标明实测、同机外推、跨机情景及尚未知四类依据；重跑余量附理由，不用单一精确数字掩盖未知分支。费用注明计费日期、来源与固定/存储等已适用费用；需要当前价格时核验当期官方规则。

当算力不足时，先给保持完整目标的调度/精度情景和相应代价。若某方案删维度、learner 或信号范围，明确它改变了目标并保留原方案预算；用户仅要求加快或估时，不等于授权收缩科学问题。
