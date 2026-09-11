import requests
import time

BASE = "http://127.0.0.1:8000"

print("--- Testing /health ---")
t0 = time.time()
r = requests.get(f"{BASE}/health")
elapsed = round((time.time() - t0) * 1000, 2)
print(f"Status: {r.status_code}, Time: {elapsed}ms")
print("Response:", r.json())
assert r.status_code == 200
assert r.json().get("status") == "ok"
assert r.json().get("service") == "krishna-portfolio-api"

print("\n--- Testing /keepalive ---")
t0 = time.time()
r = requests.get(f"{BASE}/keepalive")
elapsed = round((time.time() - t0) * 1000, 2)
print(f"Status: {r.status_code}, Time: {elapsed}ms")
print("Response:", r.json())
assert r.status_code == 200
assert r.json().get("status") == "ok"

print("\n--- Testing /ready ---")
r = requests.get(f"{BASE}/ready")
print(f"Status: {r.status_code}, Response:", r.json())
assert r.status_code == 200

print("\n--- Testing /api/status ---")
r = requests.get(f"{BASE}/api/status")
print(f"Status: {r.status_code}, Response:", r.json())
assert r.status_code == 200

print("\n--- Testing /api/github/profile ---")
r = requests.get(f"{BASE}/api/github/profile")
print(f"Status: {r.status_code}, Response:", r.json())
assert r.status_code == 200
assert r.json().get("success") is True

print("\n--- Testing /api/github/repositories ---")
r = requests.get(f"{BASE}/api/github/repositories")
data = r.json()
print(f"Status: {r.status_code}, Repos count: {data.get('count')}")
assert r.status_code == 200

print("\n--- Testing /api/github/activity ---")
r = requests.get(f"{BASE}/api/github/activity")
data = r.json()
print(f"Status: {r.status_code}, Activity count: {data.get('count')}")
assert r.status_code == 200

print("\n--- Testing /api/github/contributions?year=2026 ---")
r = requests.get(f"{BASE}/api/github/contributions?year=2026")
data = r.json()
print(f"Status: {r.status_code}, Total: {data.get('totalContributions')}")
assert r.status_code == 200
assert data.get("totalContributions") >= 74900

print("\n--- Testing /api/github/commits ---")
r = requests.get(f"{BASE}/api/github/commits")
data = r.json()
print(f"Status: {r.status_code}, Commits count: {data.get('count')}")
assert r.status_code == 200

print("\n--- Testing /api/chat ---")
# 1. Greeting
r = requests.post(f"{BASE}/api/chat", json={"message": "hello"})
print("Greeting reply:", r.json().get("reply"))
assert r.status_code == 200

# 2. Portfolio question
r = requests.post(f"{BASE}/api/chat", json={"message": "What projects has Krishna built?"})
safe_reply = r.json().get("reply")[:150].encode("ascii", "ignore").decode("ascii")
print("Projects reply:", safe_reply + "...")
assert r.status_code == 200

# 3. Skills question
r = requests.post(f"{BASE}/api/chat", json={"message": "What are your skills?"})
safe_skills = r.json().get("reply")[:150].encode("ascii", "ignore").decode("ascii")
print("Skills reply:", safe_skills + "...")
assert r.status_code == 200

print("\n--- Testing Security Headers ---")
r = requests.get(f"{BASE}/health")
headers = r.headers
print("X-Content-Type-Options:", headers.get("X-Content-Type-Options"))
print("X-Frame-Options:", headers.get("X-Frame-Options"))
print("X-XSS-Protection:", headers.get("X-XSS-Protection"))
assert headers.get("X-Content-Type-Options") == "nosniff"

print("\nALL ENDPOINTS VERIFIED AND PASSING!")
