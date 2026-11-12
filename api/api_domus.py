import requests 

r = requests.post(
    "http://10.215.39.118:8001/auth/login",
    json={
        "username": "regional_norte",
        "password": "mtE49UjFHJ850CZ3Bb5F"
    }
)

print(r.status_code)
print(r.text)


headers = {
    "x-access-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwdWJsaWNfaWQiOiI3ODJmMDk4NS1mZDBhLTQyZGMtYjMyNy00MWNkMWQ0YzY4OTMiLCJleHAiOjE3OTQ0Mzc5OTd9.oiJ-9v4Jn-zsytBk6jKCwswoQ7C_x4UXamS-0ljqN68"
}

r = requests.get(
    "http://10.215.39.118:8001/query/calamidade-details",
    headers=headers,
    params={
        "page": 0,
        "limit": 1000,
        "mode": "tickets",
        "detail_type": "sites_fora"
    }
)

print(r.json())