> **语言(Language):** [**中文**](./README.md) | [**English**](./README_EN.md)

> **注意:** 本项目是一个任务型、FSM驱动的智能体的MVP实现，专为高可靠性的结构化数据抽取而设计。其核心价值在于架构模式，而不仅仅是抽取性能。

# 工程规范文档结构化抽取智能体

![状态](https://img.shields.io/badge/status-MVP-green)
![版本](https://img.shields.io/badge/version-2.3-blue)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![许可](https://img.shields.io/badge/license-MIT-lightgrey)

这是一个**任务型、状态机驱动的智能体**，用于从工程文档中进行结构化数据抽取。它专为高可靠性、可审计和自动化的工作流而设计，例如从建筑规范、机械规格或合规文件中抽取可执行的约束条件。

与通用聊天机器人不同，本智能体作为一个确定性的引擎运行，优先考虑准确性和可追溯性，而非对话能力。

## ✨ 核心特性

- **🤖 自我修复机制 (Self-Repair):** 自动检测、分析并尝试修复失败的抽取结果（例如，格式错误的JSON、缺少必填字段）。这是其工程级可靠性的核心。
- **📄 严格的JSON Schema输出:** 所有输出都经过预定义JSON Schema的严格校验，确保数据一致性和下游系统的直接可用性。
- **🔍 完全可追溯与可审计:** 每一条抽取的数据都链接回其在文档中的原始来源 (`source_ref`)，并且整个过程（包括状态转换和修复尝试）都被详细地记录下来。
- **🎯 任务导向与非对话式:** 作为一个纯粹的抽取引擎而非聊天机器人构建。它遵循一个确定性的、状态驱动的流程（`规划 -> 执行 -> 校验 -> 修复`）来实现其目标。

---

## 🚀 快速开始：体验自我修复流程

我们提供了一个简单的示例，让您可以轻松地看到智能体的核心——自我修复机制的实际运作。该示例被设计为在第一次尝试时失败，然后进行自我修复。

### 1. 环境设置

```bash
# 克隆仓库
git clone https://github.com/yanzhao77/spec-extraction-agent.git
cd spec-extraction-agent

# 安装依赖
pip install -r requirements.txt

# 设置您的API密钥 (使用与OpenAI兼容的API，如Gemini)
export OPENAI_API_KEY="在此处填入您的API密钥"
```

### 2. 一键运行示例

运行示例脚本。它将处理一个样本工程文档，故意触发一个校验失败，并演示自我修复循环。

```bash
python examples/run_example.py
```

### 3. 预期输出

您将在控制台中看到详细的日志，展示智能体的完整处理流程。最重要的部分是 **校验 -> 修复 -> 再次校验** 的循环：

```log
# ... (初始抽取日志)

[2025-12-30 10:30:24,440] INFO: 状态转换: EXTRACTION -> VALIDATION
[2025-12-30 10:30:24,440] WARNING: 来自'...'的结果JSON解析/校验失败。错误: LLM输出不是一个JSON数组。
[2025-12-30 10:30:24,440] WARNING: 来自'...'的条目Schema校验失败。错误: [\"数字类型的'value'需要一个'unit'\"]
[2025-12-30 10:30:24,440] INFO: 5个条目校验失败。进入REPAIR状态。

# --- 自我修复循环开始 --- #
[2025-12-30 10:30:24,440] INFO: 状态转换: VALIDATION -> REPAIR
[2025-12-30 10:30:24,440] INFO: 尝试修复来自'...'的条目 (第1次尝试)
[2025-12-30 10:30:27,851] INFO: HTTP请求: POST https://api.manus.im/api/llm-proxy/v1/chat/completions \"HTTP/1.1 200 OK\"

# --- 修复成功，重新校验 --- #
[2025-12-30 10:30:30,727] INFO: 状态转换: REPAIR -> VALIDATION
[2025-12-30 10:30:30,728] INFO: 所有条目校验成功。
[2025-12-30 10:30:30,728] INFO: 状态转换: VALIDATION -> FINALIZE

# ... (生成最终输出)

✅ 抽取完成: 21条约束被成功抽取和校验。
```

---

## 部署到ModelScope创空间

本项目已适配ModelScope创空间，可实现一键部署。

### README.md YAML头配置

为了让ModelScope正确识别，请确保您的`README.md`文件包含以下YAML头信息：

```yaml
---
title: 工程规范抽取智能体API
description: 一个用于从工程规范文档中抽取结构化约束的、可按次收费的Agent API服务。
app_file: app.py
app_port: 7860
sdk: fastapi
sdk_version: 0.104.1
---
```

### 环境变量

在ModelScope创空间的"设置"页面，配置以下环境变量：

- `OPENAI_API_KEY`: 您的LLM API密钥。
- `AGENT_API_KEY`: 您为API服务设置的访问密钥。

### 部署步骤

1. 登录ModelScope并进入"创空间"。
2. 点击"新建创空间"，选择"从GitHub仓库导入"。
3. 填入本仓库地址：`https://github.com/yanzhao77/spec-extraction-agent`
4. 在"设置"中配置好环境变量。
5. ModelScope将自动拉取代码并根据配置启动服务。
6. 部署成功后，您将获得一个公网访问地址，即可通过API调用该地址调用您的Agent服务。

---

## 📂 项目结构


```
spec-extraction-agent/
├── docs/                  # 详细文档
│   ├── TECHNICAL_WHITEPAPER.md  # 系统架构、设计原则和性能
│   └── API_DOCUMENTATION.md     # 将智能体部署为服务时使用的REST API接口
├── examples/              # 示例文档和运行脚本
│   ├── GB50016_2014_sample.txt  # 样本工程规范文档
│   └── run_example.py           # 一键运行示例的脚本
├── src/                   # 核心源代码
│   └── agent.py               # 主要的FSM驱动的智能体逻辑
├── .github/               # GitHub相关文件 (CI, issue模板)
├── logs/                  # 默认情况下，日志文件存储在此处
├── README.md              # 本文件
└── requirements.txt       # Python依赖
```

## ⚙️ 系统架构

智能体的行为由一个8阶段的有限状态机（FSM）控制，这确保了过程的确定性和可审计性。`VALIDATION` -> `REPAIR`的循环是其鲁棒性的关键。

![状态机](docs/state_machine.png)

要深入了解架构、设计原则和性能指标，请参阅[**技术白皮书**](docs/TECHNICAL_WHITEPAPER.md)。

## 🤝 贡献

欢迎任何形式的贡献！无论是bug报告、功能请求还是代码改进，请随时创建Issue或提交Pull Request。更多细节请参阅我们的[**贡献指南**](CONTRIBUTING.md)。

## 📄 许可证

本项目采用[MIT许可证](LICENSE)。
许可证](LICENSE)。
