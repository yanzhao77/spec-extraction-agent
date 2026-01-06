'''
一个完整的Python客户端示例，用于演示如何接收和处理Agent API的SSE流式响应。
'''

import requests
import json
import os

# --- 配置 ---
# 您的Agent API服务器地址
API_BASE_URL = os.getenv("AGENT_API_URL", "http://127.0.0.1:8000")
# 您的Agent API访问密钥
AGENT_API_KEY = os.getenv("AGENT_API_KEY", "your_agent_api_key")

# 要处理的文档
DOCUMENT_TO_PROCESS = "examples/GB50016_2014_sample.txt"
USER_ID = "client_user_001"


def process_sse_stream():
    """
    连接到Agent API的SSE端点，并处理流式响应。
    """
    endpoint = f"{API_BASE_URL}/v1/extract"
    headers = {
        "X-API-Key": AGENT_API_KEY,
        "Accept": "text/event-stream"
    }
    payload = {
        "document_path": DOCUMENT_TO_PROCESS,
        "user_id": USER_ID
    }

    print(f"▶️  连接到SSE端点: {endpoint}")
    print(f"▶️  请求参数: {payload}")
    print("-" * 40)

    try:
        with requests.post(endpoint, headers=headers, json=payload, stream=True, timeout=120) as response:
            response.raise_for_status()  # 确保请求成功

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("event:"):
                        event_type = decoded_line.split(":", 1)[1].strip()
                    elif decoded_line.startswith("data:"):
                        data_str = decoded_line.split(":", 1)[1].strip()
                        data = json.loads(data_str)

                        # --- 事件处理 ---
                        if event_type == "status_update":
                            handle_status_update(data)
                        elif event_type == "final_result":
                            handle_final_result(data)
                            break  # 任务完成，退出循环
                        elif event_type == "error":
                            handle_error(data)
                            break # 任务失败，退出循环

    except requests.exceptions.RequestException as e:
        print(f"\n❌ 连接错误: {e}")
    except KeyboardInterrupt:
        print("\n⏹️  客户端已停止。")

def handle_status_update(data):
    """处理状态更新事件"""
    task_id = data.get("task_id")
    status = data.get("status")
    print(f"⏳ [状态更新] 任务 {task_id[:8]}...: {status}")

def handle_final_result(data):
    """处理最终结果事件"""
    task_id = data.get("task_id")
    print(f"\n✅ [任务完成] 任务 {task_id[:8]}... 已完成！")
    print("-" * 40)

    # --- 核心：解析计费信息 ---
    billing_info = data.get("billing", {})
    is_billable = billing_info.get("billable")
    reason = billing_info.get("reason")

    if is_billable:
        print(f"💰 [计费事件] 本次调用可计费")
    else:
        print(f"🆓 [不计费事件] 本次调用不计费")
    
    print(f"   - 原因: {reason}")
    print(f"   - 计费单元: {billing_info.get('unit')}")
    print("-" * 40)

    # --- 核心：解析最终结果 ---
    result = data.get("result", {})
    validated_items = result.get("validated_items", [])
    failed_count = result.get("failed_items_count", 0)

    print(f"📊 [最终结果] 成功校验 {len(validated_items)} 条约束，失败 {failed_count} 条。")
    
    if validated_items:
        print("\n--- 抽取结果示例 (前2条) ---")
        for item in validated_items[:2]:
            print(json.dumps(item, indent=2, ensure_ascii=False))
        if len(validated_items) > 2:
            print("...")

def handle_error(data):
    """处理错误事件"""
    task_id = data.get("task_id")
    error_message = data.get("error_message")
    print(f"\n❌ [任务失败] 任务 {task_id[:8]}... 发生错误: {error_message}")

    # --- 核心：解析计费信息（失败场景） ---
    billing_info = data.get("billing", {})
    is_billable = billing_info.get("billable")
    reason = billing_info.get("reason")

    if not is_billable:
        print(f"🆓 [不计费事件] 本次调用不计费，原因: {reason}")


if __name__ == "__main__":
    process_sse_stream()
