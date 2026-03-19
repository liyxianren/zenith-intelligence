import requests

def test_model_health():
    url = "http://localhost:5001/api/model/health"
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        try:
            print(f"JSON response: {response.json()}")
        except Exception as e:
            print(f"Not JSON response: {e}")
    except Exception as e:
        print(f"Error: {e}")

def test_api_health():
    url = "http://localhost:5001/api/health"
    try:
        response = requests.get(url)
        print(f"Health check status code: {response.status_code}")
        print(f"Health check response: {response.json()}")
    except Exception as e:
        print(f"Health check error: {e}")

if __name__ == "__main__":
    test_api_health()
    test_model_health()
