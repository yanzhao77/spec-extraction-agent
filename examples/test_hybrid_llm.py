"""
测试混合LLM调用模式：验证默认LLM和客户指定LLM都能正常工作。
"""

import requests
import json

# --- 配置 ---
API_BASE_URL = "http://127.0.0.1:8000"
AGENT_API_KEY = "your_agent_api_key"  # 如果设置了AGENT_API_KEY环境变量，请替换此处
DOCUMENT_PATH = "examples/GB50016_2014_sample.txt"

def test_default_llm():
    """
    测试场景1：不指定LLM配置，使用默认的智谱GLM-4.5-Flash。
    """
    print("\n" + "="*60)
    print("测试场景1: 使用默认LLM (智谱 GLM-4.5-Flash)")
    print("="*60)
    
    headers = {
        "X-API-Key": AGENT_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "document_path": DOCUMENT_PATH,
        "user_id": "test_user_default"
    }
    
    print(f"请求参数: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(f"{API_BASE_URL}/v1/extract", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        print(f"\n响应状态: {result['status']}")
        print(f"计费信息: {json.dumps(result['billing'], indent=2, ensure_ascii=False)}")
        
        if result['status'] == 'completed' and result['result']:
            validated_count = len(result['result'].get('validated_items', []))
            print(f"抽取结果: 成功校验 {validated_count} 条约束")
        
        print("\n✅ 测试场景1 通过！")
        return result
    
    except Exception as e:
        print(f"\n❌ 测试场景1 失败: {e}")
        return None

def test_custom_llm():
    """
    测试场景2：客户指定自己的LLM配置。
    """
    print("\n" + "="*60)
    print("测试场景2: 使用客户指定的LLM")
    print("="*60)
    
    headers = {
        "X-API-Key": AGENT_API_KEY,
        "Content-Type": "application/json"
    }
    
    # 示例：使用另一个智谱模型
    payload = {
        "document_path": DOCUMENT_PATH,
        "user_id": "test_user_custom",
        "llm_base_url": "https://open.bigmodel.cn/api/paas/v4",
        "llm_model_name": "glm-4-flash",
        "llm_api_key": "2cb6d2e323ed4f3badc136090daa0ccb.87GF3FfJmNUuQcSd"
    }
    
    print(f"请求参数: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(f"{API_BASE_URL}/v1/extract", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        print(f"\n响应状态: {result['status']}")
        print(f"计费信息: {json.dumps(result['billing'], indent=2, ensure_ascii=False)}")
        
        if result['status'] == 'completed' and result['result']:
            validated_count = len(result['result'].get('validated_items', []))
            print(f"抽取结果: 成功校验 {validated_count} 条约束")
        
        print("\n✅ 测试场景2 通过！")
        return result
    
    except Exception as e:
        print(f"\n❌ 测试场景2 失败: {e}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("混合LLM调用模式测试")
    print("="*60)
    
    # 测试默认LLM
    result1 = test_default_llm()
    
    # 测试客户指定LLM
    result2 = test_custom_llm()
    
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    if result1 and result2:
        print("✅ 所有测试通过！混合LLM调用模式工作正常。")
    else:
        print("❌ 部分测试失败，请检查日志。")
