# 文献术语与作者定义术语

当任务涉及方法命名、贡献表述、定义新对象、全篇术语统一或语言润色时读取。本规则管理用词来源和含义；它不替代文献检索、主张核验或作者决定。

## 默认使用文献中的现有名称

先确定最近且已经核验原文的文献怎样称呼同一对象、性质、检验、估计量或假设。对象和条件实质相同时，沿用该名称及其通常范围，不通过换一个近义名称制造差异。不同文献名称不一致时，选择最接近本文对象和目标读者的标准用法，并记录其他名称及差别。

不得因为下列理由创造新词：让贡献显得更新、避免重复、形成品牌、让标题更醒目，或替代尚未完成的最近邻比较。Humanizer 也不得为词汇变化替换已定义术语。

## 何时可以使用作者定义术语

只有现有术语确实不能准确覆盖本文对象时，才考虑作者定义术语。进入稿件前必须同时具备：

- 现有术语及其来源定位；
- 现有术语不能覆盖的具体数学或实证差别；
- 新术语的一次明确形式定义；
- 与最近文献术语的对应关系和边界；
- 作者决定的项目内定位。

在这些条件闭合前，使用描述性文字或现有术语加限定语。不得把临时工作标签写入标题、摘要、贡献清单、定理名称或结论。

## 在项目状态中记录

受管项目在 `.paper/paper_state.yaml` 的 `canonical_terms` 中记录规范用词。文献术语示例：

```json
{
  "canonical": "conditional moment restriction",
  "forbidden_variants": ["conditional-moment certificate"],
  "provenance": {
    "kind": "literature",
    "citation_keys": ["AuthorYear"],
    "source_locator": "AuthorYear, Section 2"
  }
}
```

作者定义术语示例：

```json
{
  "canonical": "descriptive term",
  "forbidden_variants": [],
  "provenance": {
    "kind": "author-defined",
    "maps_to": ["nearest literature term"],
    "reason": "Exact object differs because ...",
    "decision_locator": ".paper/revisions.yaml#TERM-01"
  }
}
```

审计器检查这些来源字段和禁用变体。通过结构检查只说明记录完整，不证明所选术语真的是文献中的标准名称；高影响用词仍需重新打开来源并核对正文定位。

## 修改和验收

术语改变属于科学编辑，除非只是修正已记录的禁用变体。修改时检查标题、摘要、引言、定义、定理、算法、表图、附录和代码接口中的同一对象。验收至少确认：同一名称始终指同一对象；没有把相邻但不同的文献概念合并；作者定义术语具有必要性和清楚边界；贡献来自方法或结果本身，而不是名称的新颖感。
