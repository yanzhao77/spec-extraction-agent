# SSE (Server-Sent Events) 流式响应示例

为了支持MCP的`streamable`特性，API服务器需要能够以SSE格式流式返回Agent的执行状态。以下是一个示例实现，展示了如何在FastAPI中返回SSE响应。

## 1. 修改FastAPI端点

您需要修改`/v1/extract`端点以返回`StreamingResponse`。

```python
# src/api_server.py

from fastapi.responses import StreamingResponse
import asyncio

async def stream_agent_execution(document_path: str, user_id: str):
    """
    一个异步生成器，用于流式返回Agent的执行状态。
    """
    task_id = f"task_{uuid.uuid4()}"
    
    # 1. 初始状态
    yield f"event: status_update\ndata: {json.dumps({\'task_id\': task_id, \'status\': \'INIT\'})}\n\n"
    await asyncio.sleep(0.1)

    try:
        # 模拟Agent执行的不同阶段
        agent = ExtractionAgentFinal(document_path=document_path)
        
        # 模拟规划阶段
        yield f"event: status_update\ndata: {json.dumps({\'task_id\': task_id, \'status\': \'PLANNING\'})}\n\n"
        await asyncio.sleep(1)

        # 模拟抽取阶段
        yield f"event: status_update\ndata: {json.dumps({\'task_id\': task_id, \'status\': \'EXTRACTION\'})}\n\n"
        await asyncio.sleep(2)

        # 最终结果
        final_json_output = agent.run()
        agent_result = json.loads(final_json_output)
        billing_info = decide_billing({
            "status": agent_result.get("status", "completed"),
            "validated_count": len(agent_result.get("validated_items", [])),
        })

        final_response = {
            "task_id": task_id,
            "user_id": user_id,
            "document_path": document_path,
            "status": "completed",
            "billing": billing_info,
            "result": agent_result
        }
        yield f"event: final_result\ndata: {json.dumps(final_response)}\n\n"

    except Exception as e:
        error_response = {
            "task_id": task_id,
            "user_id": user_id,
            "document_path": document_path,
            "status": "failed",
            "billing": decide_billing({"status": "AGENT_EXECUTION_FAILURE"}),
            "error_message": str(e)
        }
        yield f"event: error\ndata: {json.dumps(error_response)}\n\n"

@app.post("/v1/extract")
async def extract_from_document(request: ExtractionRequest, api_key: Optional[str] = Depends(get_api_key)):
    return StreamingResponse(
        stream_agent_execution(request.document_path, request.user_id),
        media_type="text/event-stream"
    )
```

## 2. SSE事件格式

- **`event: status_update`**: 用于发送Agent执行过程中的状态更新。
- **`event: final_result`**: 用于在任务成功完成时发送最终的完整结果。
- **`event: error`**: 用于在任务失败时发送错误信息。

## 3. 客户端如何处理

支持SSE的客户端（如MCP客户端）可以监听这些事件，并实时更新UI或处理结果。

```javascript
const eventSource = new EventSource("http://your-api-url/v1/extract");

eventSource.addEventListener("status_update", (event) => {
  const data = JSON.parse(event.data);
  console.log("Status Update:", data.status);
});

eventSource.addEventListener("final_result", (event) => {
  const data = JSON.parse(event.data);
  console.log("Final Result:", data);
  eventSource.close();
});

eventSource.addEventListener("error", (event) => {
  const data = JSON.parse(event.data);
  console.error("Error:", data.error_message);
  eventSource.close();
});
```

