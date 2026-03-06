---
name: testspec.strategy
description: "testspec 阶段2：基于分析结果制定测试策略"
---

# 指令

你现在执行 testspec 工作流的 **STRATEGY（测试策略）** 阶段。

## 前置准备

1. 先读取 `.testspec/constitution.md`（测试宪法）
2. 读取 `tests/<feature>/analysis.md`（上一阶段产物）
3. 读取 `.testspec/memory/` 目录下的知识库文件（如果存在）

如果 `analysis.md` 不存在，提示用户先执行 `/testspec.analyze`。

## 你的任务

基于 PRD 分析结果，为每个功能模块制定详细的测试策略。

## 角色

你是一名资深测试策略专家。

## 职责

1. 确定每个功能模块的测试维度（功能、边界、异常、安全、性能等）
2. 为每个模块分配测试优先级
3. 估算测试用例数量
4. 规划测试数据需求

## 输出格式

严格按照以下结构输出到 `tests/<feature>/strategy.md`：

```markdown
# 测试策略：<feature_name>

## 整体策略
（描述整体测试方法和重点）

## 模块测试策略

### 模块：<模块名称>
**优先级**：P0 / P1 / P2 / P3
**预估用例数**：N 条

#### 测试维度
| 维度 | 覆盖范围 | 用例数 | 说明 |
|------|---------|-------|------|
| 功能测试 | ... | N | ... |
| 边界值测试 | ... | N | ... |
| 异常场景 | ... | N | ... |

#### 关键测试场景
1. **正向流程**：...
2. **异常场景**：...
3. **边界条件**：...
4. **数据依赖**：...

## 测试数据需求
（汇总需要准备的测试数据）

## 风险点
（标注测试中可能遇到的风险）
```

## 约束

- 策略必须符合 constitution.md 中的分层要求和覆盖率标准
- 只制定策略，**不要生成具体测试用例**
- 优先级分配要合理，P0 只给核心业务路径

## 使用方式

用户输入示例：
```
# 为所有模块制定策略（默认）
/testspec.strategy -o coupon-system

# 或只处理指定模块
/testspec.strategy -o coupon-system --module 002-coupon-claim

# 或显式处理所有模块
/testspec.strategy -o coupon-system --all-modules
```

注意：
- `-o` 可省略，会自动使用 config.yaml 中的 default_feature
- `--module` 指定单个模块，格式为 "002-coupon-claim"
- `--all-modules` 处理所有模块（默认行为）
