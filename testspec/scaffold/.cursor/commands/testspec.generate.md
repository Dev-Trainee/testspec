---
name: testspec.generate
description: "testspec 阶段3：根据策略生成结构化测试用例"
---

# 指令

你现在执行 testspec 工作流的 **GENERATE（用例生成）** 阶段。

## 前置准备

1. 先读取 `.testspec/constitution.md`（测试宪法）
2. 读取 `tests/<feature>/strategy.md`（上一阶段产物）
3. 读取 `tests/<feature>/analysis.md`（供参考）
4. 读取 `.testspec/memory/` 目录下的知识库文件（如果存在）

如果 `strategy.md` 不存在，提示用户先执行 `/testspec.strategy`。

## 你的任务

按照测试策略逐模块生成结构化的测试用例。

## 角色

你是一名资深测试工程师。

## 职责

1. 严格按照测试策略中定义的维度和范围生成用例
2. 每条用例必须完整、可执行、可验证
3. 确保覆盖所有策略中规划的场景
4. 参考历史用例（如有），保持一致性并避免遗漏

## 输出格式

严格按照以下结构输出到 `tests/<feature>/cases.md`：

```markdown
# 测试用例：<feature_name>

## <模块名称>

### TC-<模块缩写>-<编号>: <用例标题>
- **所属模块**：<模块名称>
- **优先级**：P0 / P1 / P2 / P3
- **测试类型**：功能 / 边界 / 异常 / 安全 / 性能
- **前置条件**：
  1. （列出执行该用例需要的前置状态）
- **操作步骤**：
  1. （具体可执行的操作动作）
  2. ...
- **预期结果**：
  1. （可验证的明确断言）
  2. ...
- **测试数据**：（需要的具体测试数据，如有）
```

## 约束

- 操作步骤必须是具体可执行的动作，不允许模糊描述
- 预期结果必须是可验证的断言，不允许"系统正常"这样的表述
- 每个功能模块的正向流程必须有至少 1 条 P0 用例
- 异常场景必须说明具体的异常输入或操作
- **用例编号格式**：TC-{模块编号}-{用例序号}，如 TC-001-001、TC-002-003

## 使用方式

用户输入示例：
```
# 生成所有模块的用例（默认）
/testspec.generate -o coupon-system

# 或只生成指定模块的用例
/testspec.generate -o coupon-system --module 002-coupon-claim

# 或显式生成所有模块
/testspec.generate -o coupon-system --all-modules
```

注意：
- `-o` 可省略，会自动使用 config.yaml 中的 default_feature
- 模块标题格式：`## 001-module-name`（带编号）
- 用例编号格式：`TC-001-001`（模块编号-序号）
