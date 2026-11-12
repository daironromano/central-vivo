import os
import requests
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("DOMUS_BASE_URL", "http://10.215.39.118:8001")
username = os.getenv("DOMUS_USERNAME", "regional_norte")
password = os.getenv("DOMUS_PASSWORD", "")

r = requests.post(
    f"{base_url}/auth/login",
    json={
        "username": username,
        "password": password,
    },
)

print(r.status_code)
print(r.text)

token = os.getenv("DOMUS_API_TOKEN", "")
headers = {
    "x-access-token": token,
}

r = requests.get(
    f"{base_url}/query/calamidade-details",
    headers=headers,
    params={
        "page": 0,
        "limit": 1000,
        "mode": "tickets",
        "detail_type": "sites_fora",
    },
)

print(r.json())
