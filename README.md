# testspec

基于规格（Spec-Driven）的测试用例生成工具。将 PRD 文档转化为结构化、可追踪、高质量的测试用例。

[![GitHub](https://img.shields.io/badge/GitHub-Dev--Trainee/testspec-blue)](https://github.com/Dev-Trainee/testspec)
[![Gitee](https://img.shields.io/badge/Gitee-Dev--Trainee/testspec-red)](https://gitee.com/Dev-Trainee/testspec)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 特性

- **四阶段流水线** — ANALYZE → STRATEGY → GENERATE → REVIEW，每一步都可审查
- **模块化设计** — 大型 PRD 按功能模块拆分，支持逐个或批量处理
- **宪法驱动** — 通过 `constitution.md` 定义团队测试规范，AI 严格执行
- **智能默认** — 一次配置，后续命令自动记住上下文
- **IDE 集成** — 支持 Cursor 斜杠命令和 Qoder 结构化提示词
- **Excel 导出** — 一键导出带优先级颜色标注的测试用例表格

---

## 快速开始

### 安装

```bash
# 从 GitHub 安装
git clone https://github.com/Dev-Trainee/testspec.git
cd testspec && pip install -e .

# 或从 Gitee 安装
git clone https://gitee.com/Dev-Trainee/testspec.git
cd testspec && pip install -e .
```

### 初始化项目

```bash
cd your-project
testspec init
```

这会创建 `.testspec/` 配置目录，包含：
- `constitution.md` — 团队测试规范
- `config.yaml` — LLM 和输出配置
- `memory/` — 可放入历史用例作参考

### 配置 LLM

编辑 `.testspec/config.yaml`：

```yaml
llm:
  provider: openai
  model: gpt-4o
  api_key_env: OPENAI_API_KEY
  temperature: 0.3
```

设置环境变量：
```bash
export OPENAI_API_KEY=your_api_key
```

### 运行完整流程

```bash
# 第 1 步：分析 PRD，拆出功能模块
testspec analyze docs/prd.md -o feature-name

# 查看模块清单
testspec list

# 第 2 步：制定测试策略
testspec strategy --all-modules

# 第 3 步：生成测试用例
testspec generate --all-modules

# 第 4 步：检查覆盖率
testspec review --all-modules

# 导出 Excel
testspec export
```

---

## 命令参考

| 命令 | 说明 |
|------|------|
| `testspec init` | 初始化项目配置 |
| `testspec analyze <prd> -o <name>` | 分析 PRD，拆解功能模块 |
| `testspec list` | 列出所有模块及进度 |
| `testspec strategy [--module <id>]` | 制定测试策略 |
| `testspec generate [--module <id>]` | 生成测试用例 |
| `testspec review [--module <id>]` | 审查覆盖率 |
| `testspec export` | 导出 Excel |
| `testspec run <prd> -o <name>` | 一键执行完整流水线 |
| `testspec --version` | 查看版本 |

---

## IDE 集成

### Cursor

运行 `testspec init` 后会自动生成 `.cursor/commands/` 目录。在 Cursor Agent 中输入 `/` 即可看到 testspec 系列命令：
- `/testspec.analyze` — 分析 PRD
- `/testspec.strategy` — 制定策略
- `/testspec.generate` — 生成用例
- `/testspec.review` — 审查覆盖率

### Qoder

运行 `testspec init` 后会生成 `AGENTS.md`。在 Qoder Agent 对话中引用该文件，即可使用工作流命令。

---

## 项目结构

```
.testspec/
├── constitution.md          # 团队测试规范（必须遵守）
├── config.yaml              # 项目配置
├── memory/                  # 历史用例参考
└── prompts/                 # Prompt 模板

tests/
└── <feature-name>/          # 测试产物输出目录
    ├── analysis.md          # PRD 分析结果
    ├── strategy.md          # 测试策略
    ├── cases.md             # 测试用例
    └── cases.xlsx           # Excel 导出
```

---

## 测试规范（Constitution）

在 `.testspec/constitution.md` 中定义团队标准：

```markdown
# 格式规范
- 用例编号格式: TC-{模块编号}-{三位序号}
- 每条用例必须包含: 前置条件、步骤、期望结果

# 覆盖率要求
- P0 功能: 正向 + 至少 2 个反向场景
- 涉及金额的模块必须包含精度边界测试

# 质量标准
- 期望结果必须可验证，避免模糊描述
- 测试数据使用具体值，不使用占位符
```

---

## 支持的 LLM

- OpenAI (GPT-4, GPT-4o)
- Claude (Anthropic)
- DeepSeek
- 任何 OpenAI 兼容接口的模型

---

## 示例

查看 `example/` 目录下的优惠券系统完整示例：
- `prd-coupon.md` — 示例 PRD
- `tests/coupon-system/` — 生成的分析、策略、用例

---

## 贡献

欢迎提交 Issue 和 PR！

---

## License

MIT License
