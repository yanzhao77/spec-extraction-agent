> **语言(Language):** [**中文**](./DEPLOYMENT_GUIDE.md) | [**English**](./DEPLOYMENT_GUIDE_EN.md)

# 部署指南：工程规范抽取智能体 API

本指南将引导您如何在本地或云平台上部署和运行本智能体API服务。

---

## 1. 核心部署目标

本项目的核心是部署一个**RESTful API服务**。Gradio界面仅作为可选的调试工具，不应作为生产环境的入口。

---

## 2. 环境变量配置

在部署前，请准备好以下环境变量：

| 变量 | 说明 | 示例 |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | **必需。** 用于LLM调用的API密钥。 | `sk-xxxxxxxx` |
| `AGENT_API_KEY` | **必需。** 用于保护您的API服务的访问密钥。 | `a_secure_custom_key` |
| `RUN_GRADIO_UI` | **可选。** 设置为`true`以同时运行Gradio调试界面。 | `true` |

---

## 3. 本地部署 (使用Docker)

### 步骤 1: 克隆仓库

```bash
git clone https://github.com/yanzhao77/spec-extraction-agent.git
cd spec-extraction-agent
```

### 步骤 2: 构建Docker镜像

```bash
docker build -t spec-extraction-agent:latest .
```

### 步骤 3: 运行API服务

**仅运行API服务（推荐用于生产）：**

```bash
docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY="在此处填入您的LLM密钥" \
  -e AGENT_API_KEY="在此处填入您的服务密钥" \
  --name spec-agent-api \
  spec-extraction-agent:latest
```

**同时运行API服务和Gradio调试界面：**

```bash
docker run -d -p 8000:8000 -p 7860:7860 \
  -e OPENAI_API_KEY="在此处填入您的LLM密钥" \
  -e AGENT_API_KEY="在此处填入您的服务密钥" \
  -e RUN_GRADIO_UI=true \
  --name spec-agent-full \
  spec-extraction-agent:latest
```

### 步骤 4: 访问服务

- **API接口文档:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Gradio调试界面 (如已启动):** [http://localhost:7860](http://localhost:7860)

---

## 4. 部署到ModelScope / 通义千问

1. **Fork本项目** 到您自己的GitHub账户。
2. **在ModelScope上创建新空间**，并从您的GitHub仓库导入。
3. **在平台的“设置”或“环境变量”部分，添加以下密钥：**
   - `OPENAI_API_KEY`: 您的LLM密钥。
   - `AGENT_API_KEY`: 您自定义的服务访问密钥。
4. **（可选）** 如果您希望公开Gradio调试界面，请添加`RUN_GRADIO_UI`并设置为`true`。
5. **启动部署。** 平台将自动构建并启动服务。

部署成功后，平台会提供一个公开的URL，其`/docs`路径是您的API文档。

---

## 5. API调用示例

```bash
curl -X POST "http://your-deployed-url/v1/extract" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_agent_api_key" \
  -d 
    "document_path": "examples/GB50016_2014_sample.txt"
  }
```
