---
name: testspec.run
description: "testspec 一键执行完整流水线：分析 → 策略 → 生成 → 审查"
---

# 指令

你现在执行 testspec 的 **完整工作流**，依次完成所有阶段：

```
ANALYZE → STRATEGY → GENERATE → REVIEW
```

## 前置准备

1. 先读取 `.testspec/constitution.md`（测试宪法）
2. 读取 `.testspec/memory/` 目录下的所有知识库文件（如果存在）
3. 读取用户指定的 PRD 文档

## 执行流程

请严格按照以下顺序执行，每个阶段完成后再进入下一个阶段：

### 阶段 1：ANALYZE
- 分析 PRD，拆解功能模块
- 输出到 `tests/<feature>/analysis.md`
- 完成后告知用户分析结果摘要，确认后继续

### 阶段 2：STRATEGY
- 基于 analysis.md 制定测试策略
- 输出到 `tests/<feature>/strategy.md`
- 完成后告知用户策略摘要，确认后继续

### 阶段 3：GENERATE
- 基于 strategy.md 生成测试用例
- 输出到 `tests/<feature>/cases.md`
- 完成后告知用户用例数量和分布

### 阶段 4：REVIEW
- 审查 cases.md 的覆盖率
- 输出到 `tests/<feature>/review.md`
- 完成后告知用户审查结论

## 各阶段的详细格式要求

请参考项目中的 `AGENTS.md` 文件，其中定义了每个阶段的输入、输出和格式规范。

## 约束

- 每个阶段必须按顺序执行，不可跳过
- 每个阶段的输出必须遵守 constitution.md 中的规范
- 每个阶段完成后暂停，等用户确认后再继续下一阶段
- feature 名称由用户指定

## 使用方式

用户输入示例：
```
/testspec.run docs/prd-coupon.md -o coupon-system
```

其中：
- 第一个参数为 PRD 文件路径
- `-o` 后面为 feature 名称
- 会自动执行：analyze → strategy --all-modules → generate --all-modules → review --all-modules
