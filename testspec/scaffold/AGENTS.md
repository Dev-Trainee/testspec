# AGENTS.md — testspec AI 协作指南

> 本文件指导 AI Agent 如何在 testspec 工作流中正确工作。
> 如果你是 AI 助手（Cursor / Copilot / Qoder / Claude 等），请严格遵循以下指令。

## 项目结构

```
.testspec/
├── constitution.md          # 测试宪法（必须遵守的规范）
├── config.yaml              # 项目配置
├── memory/                  # 知识库（历史用例、业务规则）
│   └── *.md
└── prompts/                 # Prompt 模板（自动注入）

.cursor/commands/            # Cursor 斜杠命令（仅 Cursor 使用）
├── testspec.analyze.md
├── testspec.list.md
├── testspec.strategy.md
├── testspec.generate.md
├── testspec.review.md
└── testspec.run.md

tests/
└── <feature-name>/          # 每个功能模块一个目录
    ├── analysis.md          # PRD 分析结果
    ├── strategy.md          # 测试策略
    ├── cases.md             # 测试用例
    └── review.md            # 覆盖率审查报告
```

## 可用命令

以下命令可在 AI 对话中直接使用（Cursor 中以斜杠触发，Qoder 中直接输入）：

| 命令 | 说明 |
|------|------|
| `testspec.analyze <prd> -o <name>` | 阶段1：分析 PRD，拆解功能模块，记录 default_feature |
| `testspec.list [-o <name>]` | 列出所有模块及进度状态 |
| `testspec.strategy [-o <name>] [--module <id>]` | 阶段2：制定测试策略（可指定模块） |
| `testspec.generate [-o <name>] [--module <id>]` | 阶段3：生成测试用例（可指定模块） |
| `testspec.review [-o <name>] [--module <id>]` | 阶段4：覆盖率审查（可指定模块） |
| `testspec.export [-o <name>]` | 导出测试用例到 Excel |
| `testspec.run <prd> -o <name>` | 一键执行完整流水线 |

参数说明：
- `-o <name>`: feature 名称，会创建 tests/<name>/ 目录。analyze 后会自动设为 default，后续命令可省略
- `--module <id>`: 指定模块 ID，如 `002-coupon-claim`。不指定则处理所有模块
- `--all-modules`: 显式指定处理所有模块（默认行为）

## 工作流状态机

testspec 遵循严格的线性工作流，每个阶段必须按顺序执行：

```
ANALYZE → STRATEGY → GENERATE → REVIEW → EXPORT
```

### 1. ANALYZE（需求分析）

**触发**：用户输入 `testspec.analyze <prd路径> -f <feature>`

**执行步骤**：
1. 读取 `.testspec/constitution.md`
2. 读取 `.testspec/memory/` 下所有 .md 文件（如果存在）
3. 读取用户指定的 PRD 文件
4. 分析 PRD，拆解为可测试的功能模块
5. 输出到 `tests/<feature>/analysis.md`

**输出格式**：
```markdown
# PRD 分析报告：<feature_name>

## 概述
（2-3 句话概括 PRD 核心目标）

## 功能模块拆解
### 模块 1：<名称>
- **描述**：...
- **涉及角色**：...
- **核心流程**：...
- **输入/输出**：...
- **业务规则**：...
- **依赖模块**：...

## 测试关注点汇总
| 序号 | 功能模块 | 关键测试点 | 复杂度 | 建议优先级 |
|------|---------|-----------|--------|-----------|

## 待确认事项
（PRD 中模糊或矛盾的问题）
```

**约束**：只做分析，不生成测试用例。

---

### 2. STRATEGY（测试策略）

**触发**：用户输入 `testspec.strategy -f <feature>`

**前置检查**：`tests/<feature>/analysis.md` 必须存在，否则提示先执行 analyze。

**执行步骤**：
1. 读取 `.testspec/constitution.md`
2. 读取 `tests/<feature>/analysis.md`
3. 读取 `.testspec/memory/` 下所有 .md 文件
4. 为每个模块制定测试策略
5. 输出到 `tests/<feature>/strategy.md`

**输出格式**：
```markdown
# 测试策略：<feature_name>

## 整体策略
（整体测试方法和重点）

## 模块测试策略
### 模块：<名称>
**优先级**：P0/P1/P2/P3
**预估用例数**：N 条

#### 测试维度
| 维度 | 覆盖范围 | 用例数 | 说明 |

#### 关键测试场景
1. **正向流程**：...
2. **异常场景**：...
3. **边界条件**：...

## 测试数据需求
## 风险点
```

**约束**：只做策略规划，不生成具体用例。

---

### 3. GENERATE（用例生成）

**触发**：用户输入 `testspec.generate -f <feature>`

**前置检查**：`tests/<feature>/strategy.md` 必须存在。

**执行步骤**：
1. 读取 `.testspec/constitution.md`
2. 读取 `tests/<feature>/strategy.md` 和 `analysis.md`
3. 读取 `.testspec/memory/` 下所有 .md 文件
4. 逐模块生成结构化测试用例
5. 输出到 `tests/<feature>/cases.md`

**用例格式**：
```markdown
### TC-<模块缩写>-<编号>: <用例标题>
- **所属模块**：<模块名称>
- **优先级**：P0 / P1 / P2 / P3
- **测试类型**：功能 / 边界 / 异常 / 安全 / 性能
- **前置条件**：
  1. ...
- **操作步骤**：
  1. ...
- **预期结果**：
  1. ...
- **测试数据**：...
```

**约束**：操作步骤必须可执行，预期结果必须可验证，禁止模糊描述。

---

### 4. REVIEW（覆盖率审查）

**触发**：用户输入 `testspec.review -f <feature>`

**前置检查**：`tests/<feature>/cases.md` 必须存在。

**执行步骤**：
1. 读取 `.testspec/constitution.md`（审查标准）
2. 读取 `tests/<feature>/analysis.md`（功能点基线）
3. 读取 `tests/<feature>/strategy.md`（覆盖计划）
4. 读取 `tests/<feature>/cases.md`（审查对象）
5. 逐条检查覆盖率，识别遗漏
6. 输出到 `tests/<feature>/review.md`

**输出格式**：
```markdown
# 测试覆盖率审查报告：<feature_name>

## 覆盖率概览
| 指标 | 要求 | 实际 | 状态 |

## 功能点覆盖检查
| 功能模块 | 功能点 | 对应用例 | 覆盖状态 |

## 发现的遗漏
## 质量问题
## 补充用例建议
## 总体评价
```

**约束**：审查态度严格，宁可误报不可漏报。

---

### 5. RUN（完整流水线）

**触发**：用户输入 `testspec.run <prd路径> -f <feature>`

**执行步骤**：按顺序执行 ANALYZE → STRATEGY → GENERATE → REVIEW，每个阶段完成后暂停，等待用户确认后继续。

---

## AI 行为准则

1. **始终先读取 constitution.md**，在生成任何内容之前
2. **每次只处理一个功能模块**，不要试图一次生成所有模块的用例
3. **在 memory/ 中检索相关历史用例**作为参考，避免重复和遗漏
4. **严格遵循当前阶段的输出格式**，不要跨阶段操作
5. **不确定时向用户确认**，而不是自行假设
6. **识别命令格式**：当用户输入 `testspec.xxx` 时，按照对应阶段的指令执行
