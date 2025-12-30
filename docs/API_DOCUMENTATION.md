# 工程规范文档结构化抽取Agent API文档

**版本:** 2.2  
**基础URL:** `https://api.example.com/v1`  
**认证:** API Key (Header: `Authorization: Bearer YOUR_API_KEY`)

---

## 1. API概览

该API提供了对工程规范文档进行结构化抽取的能力。所有请求和响应都使用JSON格式。

### 1.1 基本信息

| 属性 | 值 |
| :--- | :--- |
| **协议** | HTTPS |
| **格式** | JSON |
| **认证** | Bearer Token |
| **速率限制** | 100 请求/分钟 |
| **超时** | 60秒 |

### 1.2 错误处理

所有错误响应都遵循以下格式：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "additional_context"
    }
  }
}
```

**常见错误码：**

| 错误码 | HTTP状态 | 说明 |
| :--- | :--- | :--- |
| `INVALID_REQUEST` | 400 | 请求格式错误 |
| `UNAUTHORIZED` | 401 | 认证失败 |
| `FORBIDDEN` | 403 | 无权限访问 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `RATE_LIMIT_EXCEEDED` | 429 | 超过速率限制 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `SERVICE_UNAVAILABLE` | 503 | 服务暂时不可用 |

---

## 2. 端点定义

### 2.1 提交抽取任务

**端点:** `POST /tasks`

**描述:** 提交一个新的文档抽取任务。

**请求头:**
```
Content-Type: multipart/form-data
Authorization: Bearer YOUR_API_KEY
```

**请求体:**

| 字段 | 类型 | 必需 | 说明 |
| :--- | :--- | :--- | :--- |
| `document` | File | ✓ | 工程规范文档（PDF、Word或文本） |
| `schema` | JSON | ✗ | 自定义输出Schema（JSON格式）。如不提供，使用默认Schema |
| `extraction_goals` | JSON | ✗ | 自定义抽取目标列表。如不提供，自动检测 |
| `max_retries` | Integer | ✗ | 最大重试次数（默认：2） |
| `timeout` | Integer | ✗ | 任务超时时间（秒，默认：60） |

**请求示例:**

```bash
curl -X POST https://api.example.com/v1/tasks \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "document=@GB50016_2014.pdf" \
  -F "schema=@schema.json" \
  -F "max_retries=3"
```

**响应 (201 Created):**

```json
{
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "created_at": "2025-12-30T10:30:25Z",
  "document_name": "GB50016_2014.pdf",
  "estimated_completion_time": "2025-12-30T10:31:25Z"
}
```

**错误响应 (400 Bad Request):**

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Document file is required",
    "details": {
      "missing_field": "document"
    }
  }
}
```

---

### 2.2 查询任务状态

**端点:** `GET /tasks/{task_id}`

**描述:** 查询任务的当前状态和进度。

**路径参数:**

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `task_id` | String | 任务ID |

**请求示例:**

```bash
curl -X GET https://api.example.com/v1/tasks/task_550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**响应 (200 OK) - 处理中:**

```json
{
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "status": "EXTRACTION",
  "progress": {
    "current_stage": "EXTRACTION",
    "stage_progress": "3/5",
    "overall_progress": 60
  },
  "created_at": "2025-12-30T10:30:25Z",
  "updated_at": "2025-12-30T10:30:45Z"
}
```

**响应 (200 OK) - 已完成:**

```json
{
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "status": "COMPLETED",
  "progress": {
    "current_stage": "FINALIZE",
    "overall_progress": 100
  },
  "created_at": "2025-12-30T10:30:25Z",
  "completed_at": "2025-12-30T10:31:25Z",
  "results": {
    "total_constraints": 23,
    "validated_constraints": 23,
    "failed_constraints": 0,
    "confidence_score": 0.95
  },
  "result_url": "https://api.example.com/v1/results/task_550e8400-e29b-41d4-a716-446655440000"
}
```

**响应 (200 OK) - 失败:**

```json
{
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "status": "FAILED",
  "error": {
    "code": "EXTRACTION_FAILED",
    "message": "Failed to extract constraints from document",
    "details": {
      "stage": "EXTRACTION",
      "reason": "LLM API timeout"
    }
  },
  "created_at": "2025-12-30T10:30:25Z",
  "failed_at": "2025-12-30T10:31:25Z"
}
```

**状态值:**

| 状态 | 说明 |
| :--- | :--- |
| `PENDING` | 任务已提交，等待处理 |
| `DOCUMENT_INGEST` | 正在读取文档 |
| `STRUCTURE_ANALYSIS` | 正在分析文档结构 |
| `PLANNING` | 正在制定抽取计划 |
| `EXTRACTION` | 正在执行抽取 |
| `VALIDATION` | 正在校验结果 |
| `REPAIR` | 正在修复失败条目 |
| `FINALIZE` | 正在生成最终输出 |
| `COMPLETED` | 任务已完成 |
| `FAILED` | 任务失败 |

---

### 2.3 获取抽取结果

**端点:** `GET /results/{task_id}`

**描述:** 获取任务的最终抽取结果。

**路径参数:**

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `task_id` | String | 任务ID |

**查询参数:**

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `format` | String | `json` | 输出格式：`json`, `csv`, `xlsx` |
| `include_metadata` | Boolean | `true` | 是否包含提取元数据 |

**请求示例:**

```bash
# 获取JSON格式结果
curl -X GET https://api.example.com/v1/results/task_550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_API_KEY"

# 获取CSV格式结果
curl -X GET "https://api.example.com/v1/results/task_550e8400-e29b-41d4-a716-446655440000?format=csv" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**响应 (200 OK):**

```json
{
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "document_name": "GB50016_2014.pdf",
  "extraction_summary": {
    "total_constraints": 23,
    "by_goal": {
      "goal_firewall": 8,
      "goal_distance": 5,
      "goal_materials": 10
    }
  },
  "constraints": [
    {
      "id": "c7a1b2f8-3e4d-4f6a-8c1b-9d0a1b2c3d4e",
      "source_document": "GB50016_2014.pdf",
      "source_ref": "Section 7.1.1, Page 45",
      "applicable_object": "防火墙",
      "constraint_content": "耐火极限",
      "value": 4.0,
      "unit": "h",
      "operator": ">=",
      "pre_condition": null,
      "extraction_metadata": {
        "extraction_timestamp": "2025-12-30T10:30:25Z",
        "agent_version": "2.2",
        "llm_model_used": "gemini-2.5-flash",
        "confidence_score": 0.95
      }
    },
    ...
  ]
}
```

**错误响应 (404 Not Found):**

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found",
    "details": {
      "task_id": "task_550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

---

### 2.4 列出任务历史

**端点:** `GET /tasks`

**描述:** 列出当前用户的所有任务。

**查询参数:**

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `status` | String | - | 按状态筛选（如：`COMPLETED`, `FAILED`） |
| `limit` | Integer | 20 | 返回结果数量 |
| `offset` | Integer | 0 | 分页偏移 |
| `sort_by` | String | `created_at` | 排序字段 |
| `sort_order` | String | `desc` | 排序顺序（`asc` 或 `desc`） |

**请求示例:**

```bash
curl -X GET "https://api.example.com/v1/tasks?status=COMPLETED&limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**响应 (200 OK):**

```json
{
  "tasks": [
    {
      "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
      "status": "COMPLETED",
      "document_name": "GB50016_2014.pdf",
      "created_at": "2025-12-30T10:30:25Z",
      "completed_at": "2025-12-30T10:31:25Z",
      "results": {
        "total_constraints": 23,
        "confidence_score": 0.95
      }
    },
    ...
  ],
  "pagination": {
    "total": 42,
    "limit": 10,
    "offset": 0,
    "pages": 5
  }
}
```

---

### 2.5 获取Schema定义

**端点:** `GET /schemas`

**描述:** 获取支持的Schema列表和默认Schema。

**请求示例:**

```bash
curl -X GET https://api.example.com/v1/schemas \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**响应 (200 OK):**

```json
{
  "default_schema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Engineering Specification Constraint",
    "type": "object",
    "properties": {
      "applicable_object": {"type": "string"},
      "constraint_content": {"type": "string"},
      "value": {"type": ["number", "string", "null"]},
      "unit": {"type": ["string", "null"]},
      "operator": {"type": "string"},
      "pre_condition": {"type": ["string", "null"]},
      "source_ref": {"type": "string"}
    },
    "required": ["source_ref", "applicable_object", "constraint_content"]
  },
  "available_schemas": [
    {
      "id": "schema_building",
      "name": "Building Specification Schema",
      "description": "For building and construction standards"
    },
    {
      "id": "schema_mechanical",
      "name": "Mechanical Specification Schema",
      "description": "For mechanical engineering standards"
    }
  ]
}
```

---

### 2.6 取消任务

**端点:** `DELETE /tasks/{task_id}`

**描述:** 取消正在进行的任务。

**路径参数:**

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `task_id` | String | 任务ID |

**请求示例:**

```bash
curl -X DELETE https://api.example.com/v1/tasks/task_550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**响应 (200 OK):**

```json
{
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "status": "CANCELLED",
  "cancelled_at": "2025-12-30T10:31:00Z"
}
```

---

## 3. 使用示例

### 3.1 Python客户端

```python
import requests
import json

class ExtractionAgentClient:
    def __init__(self, api_key, base_url="https://api.example.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def submit_task(self, document_path, schema=None):
        """提交抽取任务"""
        with open(document_path, 'rb') as f:
            files = {'document': f}
            data = {}
            if schema:
                data['schema'] = json.dumps(schema)
            
            response = requests.post(
                f"{self.base_url}/tasks",
                headers=self.headers,
                files=files,
                data=data
            )
        
        return response.json()
    
    def get_task_status(self, task_id):
        """查询任务状态"""
        response = requests.get(
            f"{self.base_url}/tasks/{task_id}",
            headers=self.headers
        )
        return response.json()
    
    def get_results(self, task_id, format='json'):
        """获取抽取结果"""
        response = requests.get(
            f"{self.base_url}/results/{task_id}?format={format}",
            headers=self.headers
        )
        return response.json()
    
    def wait_for_completion(self, task_id, timeout=300):
        """等待任务完成"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_task_status(task_id)
            
            if status['status'] == 'COMPLETED':
                return self.get_results(task_id)
            elif status['status'] == 'FAILED':
                raise Exception(f"Task failed: {status['error']}")
            
            time.sleep(2)
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")

# 使用示例
client = ExtractionAgentClient(api_key="your_api_key")

# 提交任务
task = client.submit_task("GB50016_2014.pdf")
print(f"Task ID: {task['task_id']}")

# 等待完成并获取结果
results = client.wait_for_completion(task['task_id'])
print(f"Extracted {len(results['constraints'])} constraints")

# 处理结果
for constraint in results['constraints']:
    print(f"{constraint['applicable_object']}: {constraint['constraint_content']}")
```

### 3.2 cURL示例

```bash
#!/bin/bash

API_KEY="your_api_key"
BASE_URL="https://api.example.com/v1"

# 1. 提交任务
echo "Submitting task..."
RESPONSE=$(curl -s -X POST "$BASE_URL/tasks" \
  -H "Authorization: Bearer $API_KEY" \
  -F "document=@GB50016_2014.pdf")

TASK_ID=$(echo $RESPONSE | jq -r '.task_id')
echo "Task ID: $TASK_ID"

# 2. 轮询任务状态
echo "Waiting for task completion..."
while true; do
  STATUS=$(curl -s -X GET "$BASE_URL/tasks/$TASK_ID" \
    -H "Authorization: Bearer $API_KEY" | jq -r '.status')
  
  echo "Status: $STATUS"
  
  if [ "$STATUS" == "COMPLETED" ]; then
    break
  elif [ "$STATUS" == "FAILED" ]; then
    echo "Task failed!"
    exit 1
  fi
  
  sleep 2
done

# 3. 获取结果
echo "Fetching results..."
curl -s -X GET "$BASE_URL/results/$TASK_ID" \
  -H "Authorization: Bearer $API_KEY" | jq '.'
```

---

## 4. 认证

所有API请求都需要在请求头中提供API Key：

```
Authorization: Bearer YOUR_API_KEY
```

**获取API Key:**

1. 登录到 https://console.example.com
2. 进入 "API Keys" 部分
3. 点击 "Create New Key"
4. 复制生成的Key

**安全建议:**

- 不要在代码中硬编码API Key，使用环境变量
- 定期轮换API Key
- 为不同的应用使用不同的API Key
- 监控API Key的使用情况

---

## 5. 示例调用

以下是一个使用`curl`调用API的示例，用于从一个PDF文档中抽取约束。

```bash
curl -X POST http://localhost:8000/v1/extract \
  -H "Content-Type: multipart/form-data" \
  -F "document=@/path/to/your/GB50016_2014_sample.pdf" \
  -F "schema=@/path/to/your/schema.json"
```

### 响应示例

```json
{
  "status": "success",
  "message": "Extraction completed successfully.",
  "data": {
    "validated_items": [
      {
        "id": "c7a1b2f8-3e4d-4f6a-8c1b-9d0a1b2c3d4e",
        "source_document": "GB50016_2014_sample.pdf",
        "source_ref": "Section 7.1.1, Page 45",
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
    ],
    "failed_items_count": 0
  }
}
```

## 6. 速率限制

API实施以下速率限制：

| 限制类型 | 值 |
| :--- | :--- |
| **请求/分钟** | 100 |
| **请求/小时** | 5000 |
| **并发任务** | 10 |

当超过限制时，API返回 `429 Too Many Requests` 响应。

**响应头包含限制信息:**

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1735553425
```

---

## 6. 最佳实践

1. **使用异步处理:** 对于大文件，使用异步API，而不是同步等待
2. **实现重试逻辑:** 在网络错误时实现指数退避重试
3. **缓存结果:** 避免重复提交相同的文档
4. **监控配额:** 定期检查API使用情况
5. **错误处理:** 实现完善的错误处理和日志记录

---

## 7. 支持与反馈

- **文档:** https://docs.example.com
- **状态页:** https://status.example.com
- **支持邮箱:** support@example.com
- **问题报告:** https://github.com/example/agent/issues

---

**API版本:** 2.2  
**最后更新:** 2025年12月30日
