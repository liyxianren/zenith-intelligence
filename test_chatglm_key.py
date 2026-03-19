import os

import requests
import json

def test_chatglm_key(api_key):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # 尝试使用不同的模型
    models = ["glm-4.7-flashx", "glm-4.6", "glm-4.5", "glm-4"]
    
    for model in models:
        print(f"\nTesting with model: {model}")
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "你好"}],
            "max_tokens": 10,
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            if response.status_code == 200:
                print("API key is valid!")
                return True
            else:
                print("API key is invalid!")
        except Exception as e:
            print(f"Error: {e}")
    
    return False

if __name__ == "__main__":
    api_key = os.getenv("CHATGLM_API_KEY")
    if not api_key:
        raise RuntimeError("请先设置 CHATGLM_API_KEY 环境变量")
    test_chatglm_key(api_key)
