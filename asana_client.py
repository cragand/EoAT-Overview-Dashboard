"""Thin wrapper for authenticated Asana API calls."""
import requests
from auth import get_token

BASE_URL = "https://app.asana.com/api/1.0"


def api_get(endpoint, params=None):
    """Make an authenticated GET request to the Asana API."""
    token = get_token()
    if not token:
        raise RuntimeError("Not authenticated. Run: python auth.py")
    resp = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
    )
    resp.raise_for_status()
    return resp.json().get("data", resp.json())
