import requests
import time
import random

BASE_URL = "http://localhost:8000"

def test_feature(name, func):
    print(f"Testing {name}...")
    try:
        func()
        print(f"  {name} PASSED")
    except Exception as e:
        print(f"  {name} FAILED: {e}")

def verify_all():
    # Use a unique phone number for registration test
    test_phone = f"99999{random.randint(10000, 99999)}"
    
    # 1. Registration
    def registration():
        resp = requests.post(f"{BASE_URL}/register", json={
            "name": "Test User",
            "phone": test_phone,
            "password": "testpassword",
            "email": "test@example.com",
            "country": "India"
        })
        assert resp.json()["status"] == "success"

    # 2. Login
    def login():
        resp = requests.post(f"{BASE_URL}/login", json={
            "phone": test_phone,
            "password": "testpassword"
        })
        assert resp.json()["status"] == "success"

    # 3. Send Message
    def send_message():
        resp = requests.post(f"{BASE_URL}/sendMessage", json={
            "sender": test_phone,
            "receiver": "1234567890",
            "message": "Hello from Supabase test!",
            "timestamp": int(time.time() * 1000)
        })
        assert resp.json()["status"] == "success"

    # 4. Create Group
    def create_group():
        resp = requests.post(f"{BASE_URL}/group/create", json={
            "groupId": f"group_{random.randint(100, 999)}",
            "name": "Test Group",
            "createdBy": test_phone,
            "timestamp": int(time.time() * 1000)
        })
        assert resp.json()["status"] == "success"

    # 5. Create Status
    def create_status():
        resp = requests.post(f"{BASE_URL}/status/create", json={
            "userId": test_phone,
            "caption": "Feeling Supa!",
            "timestamp": int(time.time() * 1000)
        })
        assert resp.json()["status"] == "success"

    # Run tests
    test_feature("Registration", registration)
    test_feature("Login", login)
    test_feature("Send Message", send_message)
    test_feature("Create Group", create_group)
    test_feature("Create Status", create_status)

if __name__ == "__main__":
    # Note: Server must be running for this to work
    print("Starting verification (Server must be running on localhost:8000)...")
    try:
        verify_all()
    except Exception as e:
        print(f"Verification stopped: {e}")
