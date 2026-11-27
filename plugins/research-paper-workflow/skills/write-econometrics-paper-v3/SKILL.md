---
name: write-econometrics-paper-v3
description: Draft, revise and audit econometrics or quantitative-economics manuscripts, from abstracts and paper prose to referee responses and submission packages, preserving evidence, source versions and cross-artifact meaning. Use for manuscript work; route standalone theorem truth, numerical experiments and bibliographic metadata to their specialists.
---

# 计量经济学论文写作 v3

把论文视为持续演化的证据系统，而不是彼此孤立的段落。先锁定实际对象、主张和证据，再降低读者成本；不要用更强的措辞掩盖识别、理论、模拟、计算或实证缺口。

## 路由任务

1. 识别动作：构思、提纲、起草、重写、压缩、诊断、全文审计、投稿准备或返修。
2. 识别范围：句子、段落、章节、单文件、完整 LaTeX 项目、附录、复现包或投稿包。
3. 识别论文类型：计量方法、应用实证、纯理论、结构/计算或混合型。
4. 识别生命周期：研究设计、初稿、内部修改、投稿前、R&R 或最终交付。
5. 识别权限：只读诊断还是获准修改；记录作者锁定的主张、符号、结果、术语和文件。
6. 按用途选择成品：论文正文/证明、理解讲解或导师简报；沿用用户要求的语言、长度和格式，不默认同时生成三份。

把当前成果整理进现有终稿时，先找到活动稿件和已有结果，核实关键主张后立即写入实际稿源。按照[交付核查参考](references/cross-artifact-and-release.md)的“现有终稿的交付顺序”使用原构建入口，构建并读回改后的全文。先交付这次实际需要的稿源和成品。仅在确实阻断当前稿或改变研究结论时恢复其他依赖。

当现有 LaTeX 论文的完整终稿包含实测放行或风险保证，按[终稿数字来源核验](references/final-numerical-handoff.md)先核对原始事件、实际分母、来源和定理前提，尽早写进正文。保留实际构建入口和图表、附录及参考文献。已接入受控交付的项目由工作流宿主在编辑会话结束后重计、处理来源和证书错述、重编及发布。编辑过程可以保存和预览工作稿；正式交件以宿主核验后生成的稿源和 PDF 为准。

已有受控交付的证据登记时，将共同数字口径放在一个主要结果段。正文其他段落保留解释、对照、附加统计量和不确定性，避免平行重写同一套严格误放计数。已经有表格或明确的结果位置时，正文引用其含义并补充必要的定理范围。

涉及起草、论证结构、证明呈现或符号含义时，读取 [references/reader-facing-writing.md](references/reader-facing-writing.md) 的相关部分；仅拼写、标点等不改变含义的修正可直接检查实际文本，不为其展开整篇框架。采用清楚、自然的计量论文表达：先让读者理解研究问题，再引出方法与结果；减少生造复合词、长句和与主线无关的技术限定，保留标准术语、必要条件与量词。内部审计记录与稿件表达分开。

改定理解释时先用该参考的“理论解释也是科学内容”核对控制界、对象、方向和范数；摘要与多结果分支使用“摘要与分支的取舍”，先选择主线和差异项再润色。交付时读回实际成品，不能仅以公式、标签或关键词未变确认语义保持。

需要英文计量方法/理论稿件的风格渲染时，读取
[style-rendering-handoff.md](references/style-rendering-handoff.md)，保持既定的冻结科学含义、
功能卡规划、证据核验、读者稿、防御性重复整理和语义/相似度检查顺序；风格处理不
改变数学 verdict。该参考还规定 humanizer 的条件调用与完整证明分层。

用户明确要求去 AI 味、humanize 或最终去模板化时，无论语言或论文类型，读取已安装
`humanizer/SKILL.md` 与本 skill 的 [academic-humanizer.md](references/academic-humanizer.md)。
保留正式学术语域和科学含义；若已运行 renderer，则 humanizer 在其核验与读者稿之后执行。

对局部语言编辑使用**轻量模式**，包括用户要求该段落的最终版本。对全文、多文件、反复返修、实质性主张变化或整篇论文投稿准备使用**受管项目模式**；按实际范围判断，不由“最终版”一词触发完整发布流程。需要读取、初始化或协调受管状态时，再读 [references/project-state-and-routing.md](references/project-state-and-routing.md)。不为局部编辑建立状态包或恢复完整论文历史。

起草和首次交付完整论文时，先读 [references/first-draft-review.md](references/first-draft-review.md)，在提纲、证据接收和成稿核查中处理已知的重复问题。交付前检查实际版本，先修复授权范围内能解决的问题。实质性改稿对受影响内容复用该检查。局部修改或先记录意见时按当轮范围执行。

## 先守住证据与权限边界

始终先读 [references/evidence-and-source-discipline.md](references/evidence-and-source-discipline.md)，并执行：

- 不虚构引用、数据、数字、定理、证明、模拟、稳健性、方法步骤、政策或期刊偏好。
- 区分来源直接支持、跨来源综合、本次推断和待核实；发现材料不等于验证材料。
- 保留作者数学对象和实质立场。未获授权时，不修改模型、定理、结果、引用含义或作者锁定的叙事。
- 不把合著成果外推为某位真实学者的私人偏好，不模仿真实学者的私人身份或口吻。
- 未获授权时，不把未发表稿件、审稿意见、受限数据或敏感材料发送到外部服务。
- 把当前作者指南、投稿政策和披露规则当作动态信息；需要时只从官方来源核验并记录访问日期。

## 建立或读取项目状态

受管项目中，优先读取论文已有的等价状态文件。用户已要求在项目中起草、修改或完成论文时，必要的本地状态初始化属于该任务，无需重复确认；纯审阅保持只读。需要初始化时运行：

```bash
python3 scripts/init_paper_state.py \
  --paper-dir /absolute/path/to/paper \
  --paper-type econometric-methods \
  --main-file main.tex
```

脚本只创建缺失文件，默认不覆盖任何内容。状态包位于论文项目的 `.paper/`，而不是本 skill 目录。先填写：

- 论文类型、生命周期、活动稿和目标期刊；
- Question–Friction–Move–Guarantee–Value 主脊；
- locked decisions、nonclaims 和保密边界；
- 主张、表图/定理/算法、引用、修订与未解决事项；
- 关键数字、术语及其允许或禁止的变体。

简单的一次性段落编辑不得强制创建状态包。

## 建立论文主脊和写作合同

研究设计、提纲或实质性章节/全文写作前明确以下主脊；已有有效主脊可沿用，单句润色不要求重新构建：

1. **Question**：在哪个环境中识别、估计、检验、预测或解释什么？
2. **Friction**：现有做法在哪个环节、为何失效或代价过高？
3. **Move**：本文实施哪个最小而决定性的概念、统计或计算动作？
4. **Guarantee**：理论、模拟和应用分别支持什么，条件和边界是什么？
5. **Value**：谁因此能可靠回答以前不能回答的问题？

把主脊压成一句可证伪陈述。若有缺项，记录研究设计或证据缺口，同时继续完成有支持的文本和已授权核查；缺项限制相关结果主张，不阻止局部语言编辑或无关章节。

重写研究问题或贡献定位时，沿用 [reader-facing-writing.md](references/reader-facing-writing.md) 的问题与最近邻检查；比较统计量变换、校准、条件和实际新增能力。已有证据允许的主要贡献应被准确覆盖，既不夸大，也不因沿用旧摘要而漏写已完成的扩展。

展开提纲前先执行该参考的“贡献主次与范围”，从当前记录恢复决定；主贡献调整时同步结果分析，而不只改摘要。首次采纳来源时闭合引用用途与版本；用户要求官方 BibTeX 原样一致时，按引用工作流分别保留官方原件与稿用条目，不把规范化后的条目冒称逐字原件。

起草时检查段落功能、可辩护主张、证据、推断边界和前后逻辑；仅对新主张、高影响修改或需交接的内容保存写作合同，不为每个段落另建文件或审批。详细章节工作流见 [references/econometrics-writing-playbook.md](references/econometrics-writing-playbook.md)。

## 执行主张—证据关卡

受管稿件在已有主张记录中追踪摘要、引言和结论的核心主张；局部编辑直接核对相关内容，不为未变主张另建记录：

- 主张 ID、类型和允许措辞；
- 禁止的更强措辞；
- 正文、定理、算法、表图或设计落点；
- 假设、总体、备择、数据和版本范围；
- 支持状态、风险和未解决事项。

执行以下硬检查：

- 区分 estimand、identification、estimation、inference、computation 和 empirical interpretation。
- 删除正文没有落点的贡献，或将其标记为待证据，而不是润色成既成事实。
- 拆开由不同证据层级支持的复合主张。
- 将“首次、统一、稳健、有效、因果、普遍、最优”降到证据允许的强度。
- 把边界、负面结果和失败条件放到读者首次可能误解的位置。
- 不把研究计划、文献动机或模拟直觉当作论文自身结果。

引用必须走 [references/citation-workflow.md](references/citation-workflow.md) 的“发现—元数据—全文主张—BibTeX—正文”闭环。

涉及定理、模拟、引用版本或 novelty 的实质变化时，核对其真实证据依赖；需要创建/修改跨 skill 交接、状态传播或正式发布判断时，完整读取 [integrated-release-contract.md](references/integrated-release-contract.md)。已有有效合同可沿用，不因局部文字编辑新建或重签合同。确需新建时复制 [research-release-contract.json](assets/research-release-contract.json)，再运行 `scripts/validate_research_contract.py`。结构通过只说明版本、依赖和状态自洽，不能证明稿件主张正确。

## 选择论文类型适配器

读取 [references/study-design-adapters.md](references/study-design-adapters.md) 中与当前论文匹配的部分；不得把某一类型的惯例提升为普遍规则。

- 计量方法论文：对象 → 识别 → 可行程序 → 理论 → Monte Carlo → 应用。
- 应用实证论文：问题 → 设计/变异来源 → 估计 → 推断 → 经济量级 → 稳健性与边界。
- 纯理论论文：环境 → 机制 → 正式结果 → 直觉 → 证明路线 → 边界/反例。
- 结构/计算论文：模型 → 识别 → 估计/求解 → 拟合和验证 → 反事实 → 不确定性。
- 混合论文：显式映射命题、估计对象、回归/统计量和证据。

涉及定理证明或证明审计时，若可用则调用 `prove-econometrics-theory-v2`，再由本 skill 负责论文级解释和跨章节同步。涉及 Monte Carlo 科学性、实现和复现审计时，若可用则调用 `audit-numerical-simulations-v2`；本 skill 仍负责主张—模拟—正文一致性。

## 按证据顺序起草和修改

1. 先写结果卡：对象与条件、结论、机制/直觉、下游含义。
2. 再写主结果、理论说明、模拟说明和应用说明。
3. 从已兑现结果重建摘要和引言，而不是让早期摘要约束后续证据。
4. 最后重建结论、标题、投稿材料和面向读者的贡献摘要。

优先修复信息结构、逻辑依赖和主张强度，再处理句法与风格。沿用作者术语和锁定符号；获准整理表达时，可按用途简化未锁定记号并同步对应关系，不改变数学对象或通过同义词轮换掩盖术语重复。

涉及方法命名、定义新对象、贡献表述或全篇术语统一时，读取
[terminology-governance.md](references/terminology-governance.md)。优先采用最近且已核验文献对同一对象使用的名称；不能用近义改写或新标签制造贡献差异。作者定义术语只有在现有名称不能准确覆盖对象时使用，并记录现有术语来源、差别、形式定义、对应关系和作者决定。未完成这些记录的临时标签不得进入标题、摘要、贡献清单、定理名称或结论。

对 Monte Carlo，要求每个 DGP 对应理论命题、边界、失效模式或有限样本风险；报告随机种子策略、重复次数、调参、拒绝率/覆盖率/偏差等定义和 Monte Carlo 不确定性。对实证应用，说明方法改变了哪个实质判断，不把应用当作“代码能运行”的装饰。

按写作工作台的 Monte Carlo 与图形解释规则，先确定主要现象、设计目的和图表对象，再写简洁、客观的分析。实证推断适用性由 workflow 的 empirical bridge 或已有等价方法核验负责；写作不能替未验证的修正方法发放有效性结论。

结果首次出现时就解释影响读者判断的异常、零结果和失败：区分已核查机制、待验证解释与数值故障；分别通过的稳健性不能写成联合稳健性。具体范围与写法见写作工作台的“经济量级、零结果与边界”。

Simulation handoff 不是一张表，而是每个 result cell 的证据证书：phase、diagnostic/confirmatory role、null/DGP/population、pointwise/grid/continuum event、实际有效重复数、MCSE、失败率、same-size/paired comparison 资格、版本与最大允许措辞。每个句子的 wording ceiling 只取其 **required dependency edges** 的最低层级；无关 diagnostic cell 不得压低整篇稿件，有限 DGP、pilot、边际 coverage 或未校准 raw power 也不得升级成 uniform validity、dominance 或 omnibus。

## 管理实质性变化

修改前分类：

- **A 类：语义合同**——问题、对象、贡献、因果/识别或外推表述；重新打开完整证据链和所有摘要性文本。
- **B 类：证据或方法**——假设、算法、证明、DGP、数据、数字、表图；重新检查所有受影响章节、附录和产物。
- **C 类：元数据**——作者、基金、声明、版本、链接；重新检查投稿包。
- **D 类：表层文字**——不改变科学含义的语法、标点和局部清晰度；执行局部语义差异检查。

语义差异不要只比较字符串。对高影响句子比较 claim AST：estimand/null、量词、index/norm、formula/theorem object、source version/citation role 与 wording tier。pointwise→uniform、main→supplement、preprint→journal 等变化必须生成新版本并重新打开真实后代；纯排版且 semantic hash 不变时只刷新 render。

不得跨公式、引用键、标签、字段代码或元数据执行未经保护的全局替换。详细影响图见 [references/cross-artifact-and-release.md](references/cross-artifact-and-release.md)。

## 执行跨文件和发布审计

对于同步任务，先修改实际稿件，再运行直接覆盖受影响主张的检查。已有项目状态可用于确定当前稿源和证据。范围内确有需要时再更新状态记录。局部证据同步按受影响依赖核查，整篇投稿准备才应用全稿发布审计。完成要求的文件和定向检查后及时交付；如正文范围扩大、检查失败或出现新的跨文件疑点，沿受影响路径扩大验证。

恢复一个有意裁剪的派生工作区时，只以 authoritative active-state binding 中列出的对象判断当前字节是否缺失或漂移。未进入该绑定的历史证据或未来投稿文件在当前快照中不可复查，并不自动使已记录完成的工作失效，也不自动增加新的恢复 gate。

受管项目确需相应结构或引用核对时运行以下只读审计；局部文本只检查受影响内容，不因项目在本地就扫描整篇：

```bash
python3 scripts/audit_paper_project.py /absolute/path/to/paper --format markdown
python3 scripts/check_citations.py /absolute/path/to/paper --format markdown
```

对受管稿件中新增或改动的数值、引用和结果表述，按 [claim-coverage.md](references/claim-coverage.md) 运行反向漏登记提示；纯局部编辑没有账本时不强制初始化。

审计递归读取 LaTeX 输入图，检查 label/ref/cite/BibTeX、状态账本、表图路径、锁定术语和声明式关键数字。脚本发现只是诊断证据，不能证明定理、识别或引用主张正确。

整篇论文进入投稿准备时，先解决可处理的科学与产物 blocker，再冻结**最后一个实际候选稿**。局部交付不运行完整发布审计。候选稿准备和本地交付不以作者提交批准为前提；下列 `--release` 若仅报告尚缺作者批准，应如实标为待作者审阅，继续完成其余准备，不请求重复授权：

```bash
python3 scripts/freeze_candidate.py /absolute/path/to/paper
python3 scripts/audit_paper_project.py /absolute/path/to/paper --release --format markdown
```

冻结后任何受管源文件、参考文献或状态账本变化都会使候选 hash 失效。完整四遍审查、reverse outline 和发布标准见 [references/cross-artifact-and-release.md](references/cross-artifact-and-release.md)。

## 适配期刊而不伪造规则

对 JOE、JBES、ET 的叙事重心及期刊 overlay 使用 [references/journal-overlays-confidentiality.md](references/journal-overlays-confidentiality.md)：

- JOE：突出计量摩擦、方法增量、理论性质、有限样本后果和应用意义。
- JBES：突出统计任务、可实施程序、相对基准、诊断/软件价值和真实数据表现。
- ET：突出对象、条件边界、极限理论、证明创新和反例。

这些是可观察的写作重心，不是编辑规则。格式、篇幅、数据政策和 AI 披露必须根据当前官方指南另行核验。

## 处理返修和审稿回复

读取 [references/revision-and-referee.md](references/revision-and-referee.md)。先更新主张、证据和影响图，再改正文。每条意见记录：是否成立、动作、证据、位置、影响等级、验证结果和剩余限制。

普通作者建议和用户转述导师意见也复用已有修订/反馈记录；建议被采纳、文件被改动、结果经核查分别判断。来源归因与跨阶段交接见该参考，不为局部写作另建反馈系统。

同意时说明具体改变；不同意时给推导、反例、模拟或文献证据。先恢复本次修改与暂不修改的范围；“先记录、之后统一修改”在后续明确执行指令覆盖的范围内解除，其余范围继续保留。语言偏好在当前已授权修改的段落、章节或全文内应用，不擅自扩到范围外；收集意见不等于已经改稿。不得用新增大量稳健性掩盖识别错误、定理缺口或比较不公平，也不得声称尚未复核的意见“已解决”。

## 交付

按任务范围交付最小必要集合：

1. 总体判断和最高优先级问题；
2. 可直接使用的成品文本或审计报告；
3. 会帮助后续修改的关键结构选择；
4. 新增、改变或仍未支持的主张；
5. 已检查的文件、关卡和脚本，以及明确未检查的部分；
6. 未解决问题、发布阻断项和下一步完成标准。

不得把局部检查报告成全文检查，不得把干净的自动化报告写成“论文正确”或“可投稿”。只有确切候选稿满足适用科学、证据、跨文件、引用、格式要求及作者提交批准时，才标为 `submission-ready`。本次任务的最终文本或待作者审阅候选稿可以先行完成和交付；不得把 `final` 一词等同于对外提交授权，也不得把已授权的内容修改误报为仍需批准。

## 验收

交付前确认：

- 问题、对象、理论、模拟、应用、摘要和结论保持同一语义合同。
- 每项核心主张有正文落点、适用范围和可定位证据。
- 经济量级、零结果、不确定性和计算限制得到准确解释。
- 最近邻比较公平、版本明确；引用元数据和所支持主张分别核验。
- 关键数字、表图、公式、附录、代码和投稿材料跨文件同步。
- 作者锁定内容、保密边界和写入权限得到遵守。
- 最终交付物本身通过适用检查；任何后续修改都会重新打开相应关卡。
- 正文中的每个段落能说明其对问题、insight、主结果、解释、必要实施或承重证明桥的边际作用；其余内容已移入适当位置或删除。
- 完整论文证明明确区分证明目标、主路线、关键桥梁和技术闭合；前三者在正文可恢复，第四类保留于正文或附录而未被删除。
