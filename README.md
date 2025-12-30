# 工程规范文档结构化抽取智能体 (Engineering Specification Extraction Agent)

![Status](https://img.shields.io/badge/status-MVP-green)
![Version](https://img.shields.io/badge/version-2.3-blue)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

这是一个任务型、状态机驱动的**工程规范文档结构化抽取智能体**。它旨在从非结构化的工程文档（如PDF、Word、文本）中，自动化、高精度地抽取可执行的结构化约束，并输出为标准的JSON格式。

与通用聊天机器人不同，本Agent是一个为工程应用设计的、低容错、高可靠的抽取引擎，其核心是**确定性的多阶段处理流程**和**自我修复能力**。

## 核心特性

- **状态机驱动 (FSM-Driven):** Agent的行为由一个显式的有限状态机驱动，确保了流程的确定性、可追溯性和可控性。
- **多阶段闭环流程 (Multi-stage Loop):** 严格遵循`规划 → 执行 → 校验 → 修复`的闭环流程，保证了输出结果的质量。
- **自我修复能力 (Self-Repair):** 当LLM输出不完美或校验失败时，Agent能自动进入`REPAIR`状态，分析失败原因并尝试修复，而不是直接放弃或输出错误结果。
- **目标级规划 (Goal-level Planning):** 在抽取前进行智能规划，定义高级抽取目标（Goals），并关联相关文档片段，而非盲目处理整个文档。
- **严格Schema输出 (Strict Schema Compliance):** 所有输出都严格符合预定义的JSON Schema，确保了数据的一致性和下游系统的可用性。
- **完全可追溯 (Full Traceability):** 每一条抽取结果都包含指向原始文档位置的引用（`source_ref`）和详细的元数据，支持审计和验证。

## 系统架构

Agent的核心是一个8阶段的有限状态机（FSM），它确保了任务执行的每一步都是可控和可预测的。`VALIDATION` -> `REPAIR`的循环是其鲁棒性的关键。

![State Machine](docs/state_machine.png)

1.  **INIT:** 初始化Agent。
2.  **DOCUMENT_INGEST:** 读取并解析文档。
3.  **STRUCTURE_ANALYSIS:** 分析文档结构，切分逻辑块（Chunks）。
4.  **PLANNING:** 制定目标级的抽取计划。
5.  **EXTRACTION:** 调用LLM执行抽取任务。
6.  **VALIDATION:** 校验抽取结果的格式和内容。
7.  **REPAIR:** **（核心）**当校验失败时，自动尝试修复错误。
8.  **FINALIZE:** 整合所有通过校验的结果，生成最终输出。

更详细的架构设计，请参阅 [**技术白皮书 (TECHNICAL_WHITEPAPER.md)**](docs/TECHNICAL_WHITEPAPER.md)。

## 项目结构

```
spec_extraction_agent/
├── docs/                  # 详细文档
│   ├── TECHNICAL_WHITEPAPER.md
│   └── API_DOCUMENTATION.md
├── examples/              # 示例文档和数据
│   └── GB50016_2014_sample.txt
├── logs/                  # 运行日志
│   └── agent_mvp_final.log
├── src/                   # 核心源代码
│   └── agent.py
├── .gitignore
├── README.md              # 本文档
└── requirements.txt       # Python依赖
```

## 快速开始

### 1. 环境准备

- Python 3.9+
- Pip

### 2. 安装依赖

首先，克隆本仓库：
```bash
git clone <repository_url>
cd spec_extraction_agent
```

然后，安装所需的Python库：
```bash
pip install -r requirements.txt
```

### 3. 配置API Key

本Agent使用OpenAI兼容的API（如Gemini）进行LLM调用。请在环境变量中设置您的API密钥：

```bash
export OPENAI_API_KEY="your_api_key_here"
```

### 4. 运行示例

项目已包含一个基于《建筑设计防火规范》的示例文档。直接运行Agent即可开始处理：

```bash
python src/agent.py
```

运行结束后，您将在控制台看到最终的JSON输出，同时在`logs/`目录下生成一份详细的执行日志`agent_mvp_final.log`，其中记录了每一次状态转移和决策过程。

## 使用方法

要处理您自己的文档，只需修改`src/agent.py`文件末尾的`main`函数部分：

```python
if __name__ == "__main__":
    # 将"examples/GB50016_2014_sample.txt"替换为您的文档路径
    agent = ExtractionAgentFinal(document_path="path/to/your/document.txt")
    final_json_output = agent.run()
    
    # 打印或保存输出
    print(final_json_output)
```

## 输出格式

Agent的输出是一个包含多个约束对象的JSON数组。每个对象都严格遵循预定义的Schema。

**输出示例：**
```json
[
  {
    "id": "c7a1b2f8-3e4d-4f6a-8c1b-9d0a1b2c3d4e",
    "source_document": "examples/GB50016_2014_sample.txt",
    "source_ref": "7.1 防火墙",
    "applicable_object": "防火墙",
    "constraint_content": "耐火极限不应低于4.00h",
    "value": 4.0,
    "unit": "h",
    "operator": ">=",
    "pre_condition": null,
    "extraction_metadata": {
      "extraction_timestamp": "2025-12-30T10:30:25Z",
      "agent_version": "2.3-final",
      "llm_model_used": "gemini-2.5-flash",
      "confidence_score": 0.98
    }
  }
]
```

## 文档

- **[技术白皮书](docs/TECHNICAL_WHITEPAPER.md):** 深入了解系统架构、设计原则、核心能力和性能指标。
- **[API文档](docs/API_DOCUMENTATION.md):** 如果您希望将此Agent部署为服务，这里有完整的API接口定义。

## 贡献

欢迎各种形式的贡献！如果您有任何建议、发现bug或希望添加新功能，请随时提交Pull Request或创建Issue。

1.  Fork本仓库
2.  创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3.  提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4.  推送到分支 (`git push origin feature/AmazingFeature`)
5.  打开一个Pull Request

## 许可证

本项目采用 [MIT许可证](LICENSE)。
