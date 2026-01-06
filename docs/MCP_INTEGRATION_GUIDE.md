# MCP (Model Context Protocol) 集成指南

本文档说明了如何将工程规范抽取智能体API作为MCP服务，集成到支持MCP的客户端（如通义千问、Claude Desktop等）中。

---

## 1. 核心配置文件

您需要以下两个核心配置文件来定义MCP服务：

1.  **`mcp_server_config.json`**: 定义服务器信息和协议。
2.  **`mcp_tool_spec.json`**: 定义Agent提供的工具（即API端点）。

---

## 2. 在MCP客户端中配置

以通义千问为例，您可以在其“插件中心”或“开发者设置”中添加自定义工具。

1.  **选择“添加自定义工具”**

2.  **选择“通过URL导入”或“手动配置”**

3.  **填入配置信息**

    - **服务器配置URL**: 提供`mcp_server_config.json`文件的托管地址。
    - **工具定义URL**: 提供`mcp_tool_spec.json`文件的托管地址。

    或者，将两个文件的内容直接粘贴到手动配置的表单中。

4.  **设置认证信息**

    在认证部分，填入您的`AGENT_API_KEY`。

    - **认证类型**: API Key
    - **Header名称**: `X-API-Key`
    - **API Key值**: `your_agent_api_key`

5.  **保存并启用**

    保存后，您的Agent API就会作为通义千问的一个可用工具出现在工具列表中。

---

## 3. 如何调用

在支持MCP的客户端中，您可以像调用任何其他工具一样调用您的Agent。

**示例对话：**

> **用户:** "请使用工程规范抽取工具，帮我分析一下这份文档：`https://example.com/spec.pdf`"

MCP客户端会自动识别出您意图调用`extract_constraints_from_document`工具，并自动填充参数：

```json
{
  "tool_name": "extract_constraints_from_document",
  "parameters": {
    "document_path": "https://example.com/spec.pdf",
    "user_id": "qwen_user_123"  // 由客户端自动生成
  }
}
```

客户端将此请求发送到您的API服务器，并以流式方式接收和显示结果。

---

## 4. 流式响应 (SSE)

由于我们在`mcp_tool_spec.json`中将`streamable`设置为`true`，MCP客户端会期望服务器以Server-Sent Events (SSE)格式返回响应。

客户端会实时展示Agent的执行状态（如`PLANNING`, `EXTRACTION`），并在收到`final_result`事件后显示最终结果。

这为用户提供了更好的交互体验，因为他们不必等待整个任务完成后才能看到反馈。

---

## 5. 计费

- **计费事件**: 只有当客户端收到`final_result`事件，并且其中的`billing.billable`为`true`时，才应记录一次计费事件。
- **失败不计费**: 如果收到`error`事件，或者`final_result`中的`billing.billable`为`false`，则不计费。
