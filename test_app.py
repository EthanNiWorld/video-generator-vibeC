import requests

# 测试登录页面
print("Testing login page...")
try:
    response = requests.get('http://127.0.0.1:5002/login')
    print(f"Status code: {response.status_code}")
    print(f"Response length: {len(response.text)} characters")
    print(f"First 500 characters of response: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {e}")

# 测试首页
print("\nTesting home page...")
try:
    response = requests.get('http://127.0.0.1:5002/')
    print(f"Status code: {response.status_code}")
    print(f"Response length: {len(response.text)} characters")
    print(f"First 500 characters of response: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {e}")
