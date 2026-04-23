"""OAuth helper: prints auth URL, accepts callback URL, saves token."""
import json
import os
import urllib.parse
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("ASANA_CLIENT_ID")
CLIENT_SECRET = os.getenv("ASANA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ASANA_REDIRECT_URI")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".token.json")

AUTH_URL = "https://app.asana.com/-/oauth_authorize"
TOKEN_URL = "https://app.asana.com/-/oauth_token"


def get_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def exchange_code(code):
    resp = requests.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    })
    resp.raise_for_status()
    token_data = resp.json()
    token_data["obtained_at"] = datetime.now(timezone.utc).isoformat()
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    return token_data


def refresh_token():
    with open(TOKEN_FILE) as f:
        token_data = json.load(f)
    resp = requests.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": token_data["refresh_token"],
    })
    resp.raise_for_status()
    new_data = resp.json()
    new_data["obtained_at"] = datetime.now(timezone.utc).isoformat()
    # Preserve refresh_token if not returned
    if "refresh_token" not in new_data:
        new_data["refresh_token"] = token_data["refresh_token"]
    with open(TOKEN_FILE, "w") as f:
        json.dump(new_data, f, indent=2)
    return new_data


def get_token():
    """Return a valid access token, refreshing if needed."""
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE) as f:
        token_data = json.load(f)
    # Asana tokens expire in 1 hour; refresh proactively at 50 min
    obtained = datetime.fromisoformat(token_data["obtained_at"])
    age = (datetime.now(timezone.utc) - obtained).total_seconds()
    if age > 3000:
        token_data = refresh_token()
    return token_data["access_token"]


if __name__ == "__main__":
    print("\n1) Open this URL in your browser:\n")
    print(f"   {get_auth_url()}\n")
    print("2) Log in and click 'Allow'")
    print("3) Your browser will redirect to a URL that fails to load — that's OK")
    print("4) Copy the FULL URL from your browser's address bar and paste it here:\n")
    callback_url = input("Paste URL here: ").strip()
    parsed = urllib.parse.urlparse(callback_url)
    code = urllib.parse.parse_qs(parsed.query).get("code", [None])[0]
    if not code:
        print("Error: Could not find 'code' parameter in URL.")
        raise SystemExit(1)
    token_data = exchange_code(code)
    print(f"\nAuthenticated as: {token_data.get('data', {}).get('name', 'unknown')}")
    print(f"Token saved to {TOKEN_FILE}")
