# 英文计量稿件的风格渲染交接

当当前任务需要英文计量方法/理论论文的结构、读者稿或去模板化处理时读取。
保留已有约定的顺序、来源功能与科学保护；仅拼写/标点等表层修正不为此启动风格检索。
全部命令与外部 skill 路径按当前安装解析，不把本页当成独立数学核验协议。

英文计量方法或理论论文可调用已安装的 `econometrics-style-renderer`，但它只负责结构和读者稿表达，不判断数学真值。执行顺序固定为：冻结科学含义；在起草前按章节、任务和 proof move 检索 3--5 张结构卡；完成证明与证据核验；内容稳定后用 reader-facing 卡生成论文稿；执行段落必要性、主线篇幅和证明分层检查；合并重复防御性表达；最后运行语义、读者注意力结构与来源重合检查。普通方法论文默认使用 `sxj` 功能卡；high-level/primitive、sieve、efficiency 提高 `chen` 优先级；specification、omnibus、projection、power、empirical-process 提高 `escanciano` 优先级。不得为表面多样性强行混合来源，也不得把合著论文特征写成某位作者的私人风格。无适用卡时回退到本 skill 的 reader-facing guidance，不凭记忆模仿作者。

保持两种同步文本：完整核验稿保留全部量词、条件、余项、proof obligations、边界和失败记录；论文稿使用连续论证、公式主导、短过渡和必要交叉引用。每项会改变定理范围、识别、解释或实施的限制都必须保留，并指定一个首次出现的规范位置；其他位置删除重复警告或使用短交叉引用。`ledger`、`gate`、`fingerprint`、`verified interface`、`non-regression contract` 等内部流程词不得进入论文稿。风格检查失败，或修改触及公式、量词、modal verb、数字、citation key、theorem label、引用角色或结论强度时，按科学修改处理并重新打开相应证据链。

对整节、全文或完整论文证明的读者稿，读取 renderer 的
`references/reader-attention-and-proof-layering.md`。先冻结本节要让读者理解的
问题、核心 insight、主结果与解释，再反向标记每段的功能和去向。只有推进这条
主线、提供承重定义或证明桥、给出理解或复现所必需的实施细节，或在规范位置
陈述实质限制的段落才留在正文；自包含的技术闭合移入附录，重复警告、流程残留
和没有明确后果的细节删除。不得用固定字数比例代替判断，但全文正文必须让读者
无需从实现细节中拼出问题、insight、主结果及其意义。局部段落编辑可就地执行；
材料性章节、全文或证明修改应记录轻量 attention map，并运行 renderer 的
`scripts/validate_reader_attention.py MAP --json`。结构通过只说明所记录的覆盖与
去向自洽，不证明段落重要性判断正确。

用户要求“去 AI 味”、humanize 或最终语言去模板化时，读取已安装
`humanizer/SKILL.md`，并同时执行
[academic-humanizer.md](academic-humanizer.md)。上游 Humanizer
负责识别公式化结构，本 profile 负责学术语域和证据边界。只在科学内容
锁定后处理指定 prose；不把去模板化变成口语化、同义词轮换或探测器规避，
也不改变术语、数学、量词、数字、引用和结论强度。若已使用
`econometrics-style-renderer`，Humanizer 必须在其结构、证明核验、读者稿和
防御性表达整理之后运行；Humanizer 提议的语义变化一律退回科学修改流程。
