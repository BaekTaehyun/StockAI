import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000"
TEST_CODE = "005930"  # Samsung Electronics
LOGIN_USERNAME = "admin"  # Default username from app
LOGIN_PASSWORD = "admin"  # Default password from app

def login(session):
    """로그인하여 세션 획득"""
    print("Logging in...")
    login_url = f"{BASE_URL}/login"
    response = session.post(login_url, data={
        'username': LOGIN_USERNAME,
        'password': LOGIN_PASSWORD
    }, allow_redirects=False)  # Don't follow redirects to check response
    
    # Check if login was successful (should redirect to index page)
    if response.status_code == 302:  # Redirect means successful login
        print("[OK] Login successful")
        return True
    elif response.status_code == 200:
        # Login page returned, meaning credentials were wrong
        print(f"[FAIL] Login failed: Invalid credentials")
        print(f"Response preview: {response.text[:200]}")
        return False
    else:
        print(f"[FAIL] Login failed: {response.status_code}")
        return False

def test_sentiment_api():
    print(f"Testing Sentiment API for {TEST_CODE}...")
    
    # Create session for maintaining login state
    session = requests.Session()
    
    # Login first
    if not login(session):
        return False
    
    try:
        url = f"{BASE_URL}/api/analysis/sentiment/{TEST_CODE}"
        print(f"Requesting: {url}")
        
        response = session.get(url)
        
        if response.status_code != 200:
            print(f"[FAIL] Status Code: {response.status_code}")
            print(response.text)
            return False
            
        data = response.json()
        
        if not data.get('success'):
            print(f"[FAIL] API Success False: {data.get('message')}")
            return False
            
        result_data = data.get('data', {})
        print(f"[DEBUG] Response Data Keys: {list(result_data.keys())}")
        
        if 'price_strategy' in result_data:
            print("[PASS] 'price_strategy' found in response.")
            print(f"Strategy: {result_data['price_strategy']}")
            return True
        else:
            print("[FAIL] 'price_strategy' NOT found in response.")
            return False
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    if test_sentiment_api():
        sys.exit(0)
    else:
        sys.exit(1)
