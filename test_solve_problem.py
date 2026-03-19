import requests
import json

def test_solve_problem():
    url = "http://localhost:5001/api/solve-problem"
    headers = {
        'Content-Type': 'application/json'
    }
    
    # 测试文字输入
    text_data = {
        "type": "text",
        "content": "求解方程：2x + 3 = 7"
    }
    
    print("Testing text input...")
    try:
        response = requests.post(url, headers=headers, json=text_data)
        print(f"Status code: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success')}")
        if result.get('data'):
            print(f"Recognized text: {result['data'].get('recognizedText')}")
            print(f"Parse result: {result['data'].get('parseResult')}")
            print(f"Solution: {result['data'].get('solution')}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    test_solve_problem()
