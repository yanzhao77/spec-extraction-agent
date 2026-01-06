> **语言(Language):** [**中文**](./DEPLOYMENT_GUIDE.md) | [**English**](./DEPLOYMENT_GUIDE_EN.md)

# 部署指南：工程规范文档结构化抽取智能体

本指南将引导您如何在本地或云平台（如ModelScope、通义千问）上部署和运行本智能体。

---

## 1. 先决条件

在开始之前，请确保您已安装以下软件：

- **Docker:** 用于构建和运行容器化应用。 [安装Docker](https://docs.docker.com/get-docker/)
- **Git:** 用于克隆代码仓库。 [安装Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- **LLM API密钥:** 本智能体需要一个与OpenAI兼容的API密钥（例如，来自Gemini、通义千问等）。

---

## 2. 本地部署 (使用Docker)

这是在您自己的机器上运行和测试智能体的最快方法。

### 步骤 1: 克隆仓库

```bash
git clone https://github.com/yanzhao77/spec-extraction-agent.git
cd spec-extraction-agent
```

### 步骤 2: 构建Docker镜像

在项目根目录下，运行以下命令来构建Docker镜像。这将需要几分钟时间。

```bash
docker build -t spec-extraction-agent:latest .
```

### 步骤 3: 运行Docker容器

使用以下命令来启动容器。请确保将`"在此处填入您的API密钥"`替换为您真实的API密钥。

```bash
docker run -d -p 7860:7860 -p 8000:8000 \
  -e OPENAI_API_KEY="在此处填入您的API密钥" \
  --name spec-agent \
  spec-extraction-agent:latest
```

**命令解释:**
- `-d`: 在后台运行容器。
- `-p 7860:7860`: 将主机的7860端口映射到容器的7860端口 (Gradio UI)。
- `-p 8000:8000`: 将主机的8000端口映射到容器的8000端口 (FastAPI)。
- `-e OPENAI_API_KEY=...`: 将API密钥作为环境变量传递给容器。
- `--name spec-agent`: 为容器指定一个名称，方便管理。

### 步骤 4: 访问服务

容器成功运行后，您可以访问以下地址：

- **Gradio Web UI:** [http://localhost:7860](http://localhost:7860)
- **FastAPI接口文档:** [http://localhost:8000/docs](http://localhost:8000/docs)

要停止容器，请运行 `docker stop spec-agent`。
要查看日志，请运行 `docker logs spec-agent`。

---

## 3. 部署到ModelScope / 通义千问

ModelScope平台可以利用`configuration.json`和`Dockerfile`来自动部署和托管智能体。

### 步骤 1: 准备您的仓库

1. **Fork本项目:** 将本GitHub仓库Fork到您自己的账户下。
2. **（可选）修改代码:** 根据您的需求进行修改。

### 步骤 2: 在ModelScope上创建智能体

1. **登录ModelScope:** 访问 [ModelScope官网](https://modelscope.cn/) 并登录。
2. **进入“创空间”:** 找到并进入“创空间”或类似的开发者平台。
3. **创建新项目/智能体:** 选择“从GitHub仓库导入”或类似选项。
4. **填入仓库地址:** 填入您Fork后的GitHub仓库地址。

### 步骤 3: 配置部署

ModelScope平台将自动检测`configuration.json`和`Dockerfile`文件，并据此进行配置。

- **框架:** 平台会自动识别为`Docker`部署。
- **端口:** 平台会根据`Dockerfile`中的`EXPOSE`指令和`configuration.json`中的`ports`字段，自动配置端口映射。
- **环境变量:** 在平台的“设置”或“环境变量”部分，添加一个名为`OPENAI_API_KEY`的密钥，并填入您的API密钥值。

### 步骤 4: 启动部署

点击“部署”或“启动”按钮。平台将自动拉取您的代码，构建Docker镜像，并启动服务。

部署成功后，平台会提供一个公开的URL，您可以直接访问Gradio界面或调用API。

---

## 4. API使用示例

一旦部署成功，您就可以通过编程方式调用API。

```bash
# 假设您的服务部署在 https://your-agent-url.modelscope.cn

curl -X POST "https://your-agent-url.modelscope.cn/v1/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.txt"
```

**响应示例:**

```json
{
  "task_id": "some-unique-id",
  "filename": "document.txt",
  "content": {
    "validated_items": [...],
    "failed_items_count": 0
  }
}
```

---

## 5. 故障排查

- **500 错误 (API密钥问题):** 确保`OPENAI_API_KEY`环境变量已正确设置并且密钥有效。
- **容器无法启动:** 检查Docker日志 (`docker logs spec-agent`) 以获取详细错误信息。
- **连接超时:** 确保您的网络可以访问LLM API的服务地址。
