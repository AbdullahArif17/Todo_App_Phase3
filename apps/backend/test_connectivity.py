import requests

def test_backend_connectivity():
    try:
        # Test basic connectivity
        response = requests.get('http://127.0.0.1:8000/')
        print(f"Basic connectivity test: {response.status_code}")

        # Test health endpoint
        response = requests.get('http://127.0.0.1:8000/health')
        print(f"Health endpoint: {response.status_code}, {response.json()}")

        # Test auth endpoints
        response = requests.get('http://127.0.0.1:8000/api/v1/auth')
        print(f"Auth endpoint: {response.status_code}")

        # Test login with demo user
        login_data = {
            "email": "demo@example.com",
            "password": "demo123"
        }
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/auth/login',
            json=login_data
        )
        print(f"Login test: {response.status_code}")
        if response.status_code == 200:
            print("Login successful! Response:", response.json())
        else:
            print("Login failed. Response:", response.text)

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Backend server may not be running.")
    except Exception as e:
        print(f"❌ Error during connectivity test: {e}")

if __name__ == "__main__":
    test_backend_connectivity()