---
title: 工程规范抽取智能体 (MCP服务)
description: 一个从工程规范文档中抽取结构化约束的MCP服务。
app_file: mcp_server.py
app_port: 8000
sdk: fastapi
sdk_version: 0.104.1
---

# 工程规范文档结构化抽取 Agent (MCP服务)

> **语言(Language):** [**中文**](./README.md) | [**English**](./README_EN.md)

## 项目简介

本项目是一个基于FastAPI构建的MCP（Model Context Protocol）服务器，提供了一个强大的工程规范文档结构化抽取Agent。该Agent能够从PDF、Word或文本格式的工程规范文档中，提取可执行的结构化约束，并以JSON格式输出。

## 功能特性

- **结构化抽取**: 从文档中提取约束条件、技术参数、适用对象等信息。
- **多阶段处理**: 采用“规划 → 执行 → 校验 → 修复”的多阶段流程，确保结果的准确性。
- **自我修复**: 当抽取结果不符合Schema时，能够自动进行修复。
- **计费裁决**: 内置计费裁决器，明确区分可计费和不可计费的调用。
- **灵活的LLM配置**: 允许客户使用自己的LLM，也提供默认的智谱GLM-4.5-Flash模型。

## 依赖要求

- Python >= 3.11
- FastAPI
- Uvicorn
- OpenAI
- aiohttp

## 安装步骤

1.  克隆本仓库
2.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

## 启动服务

```bash
# 设置环境变量
export AGENT_API_KEY="your_secret_api_key"

# 启动服务
python mcp_server.py
```

## 魔搭社区部署说明

### 部署准备

1.  确保项目根目录包含以下文件：
    - `mcp_server.py` - 主服务文件
    - `pyproject.toml` - 项目配置文件
    - `README.md` - 项目说明文件

### 部署步骤

1.  在ModelScope创空间中，从本GitHub仓库导入项目。
2.  在环境变量中设置`AGENT_API_KEY`。
3.  ModelScope将自动识别`mcp_server.py`并启动服务。

### 服务配置

- **服务名称**: 工程规范文档结构化抽取Agent
- **通信方式**: HTTP
- **支持的工具**:
  - `extract_constraints_from_document`: 从文档中抽取结构化约束

### 使用示例

```bash
curl -X POST "http://your-modelscope-url/v1/extract" \
  -H "X-API-Key: your_agent_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "document_path": "examples/GB50016_2014_sample.txt"
  }'
```

## 注意事项

- **API密钥**: `AGENT_API_KEY`是用于访问本服务的密钥，必须在环境变量中设置。
- **LLM配置**: 默认使用智谱GLM-4.5-Flash模型。客户可以在请求体中提供`llm_base_url`, `llm_model_name`, `llm_api_key`来覆盖默认配置。
