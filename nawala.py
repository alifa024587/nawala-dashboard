import requests

URL = "https://www.nawala.asia/api/check"

def check_domain(domain):

    headers = {
        "Authorization": "Bearer AADMW1J3KW",
        "Content-Type": "application/json",
        "Origin": "https://www.nawala.asia",
        "Referer": "https://www.nawala.asia/",
        "User-Agent": "Mozilla/5.0"
    }

    payload = {
        "name": domain
    }

    response = requests.post(
        URL,
        json=payload,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()