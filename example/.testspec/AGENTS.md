# AGENTS.md — testspec AI 协作指南

> 本文件指导 AI Agent 如何在 testspec 工作流中正确工作。
> 如果你是 AI 助手（Cursor / Copilot / Claude 等），请严格遵循以下指令。

## 项目结构

```
.testspec/
├── constitution.md          # 测试宪法（必须遵守的规范）
├── config.yaml              # 项目配置
├── memory/                  # 知识库（历史用例、业务规则）
│   └── *.md
└── prompts/                 # Prompt 模板（自动注入）

tests/
└── <feature-name>/          # 每个功能模块一个目录
    ├── analysis.md          # PRD 分析结果
    ├── strategy.md          # 测试策略
    ├── cases.md             # 测试用例
    └── review.md            # 覆盖率审查报告
```

## 工作流状态机

testspec 遵循严格的线性工作流，每个阶段必须按顺序执行：

```
ANALYZE → STRATEGY → GENERATE → REVIEW → EXPORT
```

### 1. ANALYZE（需求分析）
- 输入：PRD 原始文档
- 输出：`tests/<feature>/analysis.md`
- 职责：拆解 PRD 为独立的功能模块，提取测试关注点
- 约束：此阶段只做分析，不生成任何测试用例

### 2. STRATEGY（测试策略）
- 输入：`analysis.md` + `constitution.md`
- 输出：`tests/<feature>/strategy.md`
- 职责：制定测试维度、优先级、覆盖范围
- 约束：策略必须符合 constitution.md 中的分层要求

### 3. GENERATE（用例生成）
- 输入：`strategy.md` + `constitution.md` + `memory/*`
- 输出：`tests/<feature>/cases.md`
- 职责：按策略逐模块生成结构化测试用例
- 约束：每条用例必须严格遵循 constitution.md 中的格式规范

### 4. REVIEW（覆盖率审查）
- 输入：`cases.md` + `analysis.md` + `constitution.md`
- 输出：`tests/<feature>/review.md`
- 职责：检查用例覆盖率，识别遗漏场景
- 约束：必须逐条对照 analysis.md 中的功能点检查覆盖情况

### 5. EXPORT（导出）
- 输入：`cases.md`
- 输出：Excel 文件
- 职责：将用例转换为团队使用的表格格式

## AI 行为准则

1. **始终先读取 constitution.md**，在生成任何内容之前
2. **每次只处理一个功能模块**，不要试图一次生成所有模块的用例
3. **在 memory/ 中检索相关历史用例**作为参考，避免重复和遗漏
4. **严格遵循当前阶段的输出格式**，不要跨阶段操作
5. **不确定时向用户确认**，而不是自行假设
