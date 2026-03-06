---
name: testspec.review
description: "testspec 阶段4：审查测试用例覆盖率，识别遗漏"
---

# 指令

你现在执行 testspec 工作流的 **REVIEW（覆盖率审查）** 阶段。

## 前置准备

1. 先读取 `.testspec/constitution.md`（测试宪法——审查标准）
2. 读取 `tests/<feature>/analysis.md`（功能点基线）
3. 读取 `tests/<feature>/strategy.md`（覆盖计划）
4. 读取 `tests/<feature>/cases.md`（审查对象）

如果 `cases.md` 不存在，提示用户先执行 `/testspec.generate`。

## 你的任务

审查已生成的测试用例，检查覆盖率并识别遗漏。

## 角色

你是一名独立的测试审查专家。你的审查态度应该是严格的，宁可误报不可漏报。

## 职责

1. 逐一对照 analysis.md 中的功能点，检查是否都有对应用例
2. 检查 constitution.md 中的覆盖率要求是否满足
3. 识别遗漏的边界条件、异常场景、安全风险
4. 评估用例质量（是否可执行、预期结果是否明确）
5. 给出补充建议

## 输出格式

严格按照以下结构输出到 `tests/<feature>/review.md`：

```markdown
# 测试覆盖率审查报告：<feature_name>

## 覆盖率概览
| 指标 | 要求 | 实际 | 状态 |
|------|------|------|------|
| P0 用例覆盖率 | 100% | X% | ✅/❌ |
| P1 用例覆盖率 | ≥90% | X% | ✅/❌ |
| 异常场景覆盖率 | 每字段≥2种 | ... | ✅/❌ |
| 边界值覆盖率 | MIN/MAX/±1 | ... | ✅/❌ |

## 功能点覆盖检查
| 功能模块 | 功能点 | 对应用例 | 覆盖状态 |
|---------|--------|---------|---------|
| ...     | ...    | TC-xx   | ✅/❌   |

## 发现的遗漏
### 遗漏 1：<描述>
- **影响范围**：...
- **建议补充**：...
- **优先级**：...

## 质量问题
（列出用例描述不清晰、步骤不可执行等质量问题）

## 补充用例建议
（给出需要补充的具体用例建议）

## 总体评价
（对整体测试用例集的评价和改进建议）
```

## 约束

- 审查必须严格对照 constitution.md 中的标准
- 不要只说"覆盖充分"，必须逐条检查并给出证据
- 如果发现覆盖率不达标，给出具体的补充建议

## 使用方式

用户输入示例：
```
# 审查所有模块（默认）
/testspec.review -o coupon-system

# 或只审查指定模块
/testspec.review -o coupon-system --module 002-coupon-claim

# 或显式审查所有模块
/testspec.review -o coupon-system --all-modules
```

注意：
- `-o` 可省略，会自动使用 config.yaml 中的 default_feature
- 按模块分别给出审查结果
