# API Documentation

This document provides detailed information about the Engineering Specification Extraction Agent API.

## Base URL

`http://your-api-server-address`

## Authentication

The API uses an API key for authentication. The key must be provided in the `X-API-Key` header of every request.

- **Header Name**: `X-API-Key`
- **Value**: Your assigned API key for this service.

## Endpoint: `/v1/extract`

This is the primary and only endpoint to run a single, billable Agent execution on a document.

- **Method**: `POST`
- **Summary**: Run a Billable Extraction Task

### Request Body

```json
{
  "document_path": "string (required)",
  "user_id": "string (optional, default: default_user)",
  "llm_base_url": "string (optional)",
  "llm_model_name": "string (optional)",
  "llm_api_key": "string (optional)"
}
```

**Fields:**

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `document_path` | string | **Yes** | The absolute path to the document file on the server where the agent is running. |
| `user_id` | string | No | A unique identifier for the user or client making the request. Used for logging and billing attribution. |
| `llm_base_url` | string | No | **Advanced**: Override the default LLM base URL. |
| `llm_model_name` | string | No | **Advanced**: Override the default LLM model name. |
| `llm_api_key` | string | No | **Advanced**: Override the default LLM API key. |

### LLM Configuration Logic

The Agent provides a flexible model for LLM configuration:

1.  **Customer-Provided LLM (Advanced)**: If you provide values for `llm_base_url`, `llm_model_name`, and `llm_api_key`, the Agent will use your specified LLM for the extraction task. This allows you to use your own models or accounts.

2.  **Default System LLM**: If the `llm_*` fields are **not** provided, the Agent will automatically use the built-in default configuration:
    -   **Provider**: Zhipu AI (智谱)
    -   **Model**: `glm-4-flash`
    -   **Base URL**: `https://open.bigmodel.cn/api/paas/v4`

### Responses

The API always returns a `200 OK` status code, but the `status` and `billing` fields in the response body indicate the outcome of the task.

#### Success Response

This indicates the Agent completed its task successfully.

```json
{
  "task_id": "task_abc123...",
  "user_id": "user_123",
  "document_path": "examples/GB50016_2014_sample.txt",
  "status": "completed",
  "billing": {
    "billable": true,
    "reason": "SUCCESSFUL_EXTRACTION",
    "unit": "per_call"
  },
  "result": {
    "status": "completed",
    "validated_items": [...],
    "failed_items_count": 0
  }
}
```

#### Failure Response

This indicates the Agent encountered an error and could not complete the task.

```json
{
  "task_id": "task_xyz789...",
  "user_id": "user_456",
  "document_path": "examples/non_billable_cases/empty_document.txt",
  "status": "failed",
  "billing": {
    "billable": false,
    "reason": "AGENT_EXECUTION_FAILURE",
    "unit": "per_call"
  },
  "result": null,
  "error_message": "Document not found or is empty."
}
```

### Authentication Error

If the `X-API-Key` is missing or invalid, the server will respond with a `401 Unauthorized` error.

## Other Endpoints

### Health Check

- **Endpoint**: `GET /health`
- **Description**: A simple endpoint to check if the API server is running.
- **Response**:
  ```json
  {
    "status": "ok"
  }
  ```
