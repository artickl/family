#!/usr/bin/env python3

import datetime
import os
from pathlib import Path
import requests

def load_env_file(path):
    values = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key.strip()] = value
    return values


config = load_env_file(Path(__file__).with_name(".env.history"))
BASE_URL = os.getenv("BASE_URL", config.get("BASE_URL"))
USERNAME = os.getenv("USERNAME", config.get("USERNAME"))
PASSWORD = os.getenv("PASSWORD", config.get("PASSWORD"))

missing_variables = [
    name
    for name, value in (
        ("BASE_URL", BASE_URL),
        ("USERNAME", USERNAME),
        ("PASSWORD", PASSWORD),
    )
    if not value
]
if missing_variables:
    raise RuntimeError(
        f"Missing required configuration: {', '.join(missing_variables)}"
    )

BASE_URL = BASE_URL.rstrip("/") + "/api"

# 1. Authenticate & Fetch Bearer Token
token_url = f"{BASE_URL}/token/"
auth_response = requests.post(token_url, json={"username": USERNAME, "password": PASSWORD})
auth_response.raise_for_status()
print(f"Authentication successful. ({auth_response.status_code})")
access_token = auth_response.json().get("access_token")

# Set up authorization headers
headers = {"Authorization": f"Bearer {access_token}"}

# 2. Define the timeframe (Last 7 days)
one_week_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)

# 3. Retrieve Transactions
# Note: You may need to paginate if you make massive amounts of edits per week
# after in unix format 
transactions_url = f"{BASE_URL}/transactions/history/?after={int(one_week_ago.timestamp())}"
response = requests.get(transactions_url, headers=headers)
response.raise_for_status()
all_transactions = response.json()

print(f"Retrieved {len(all_transactions)} transactions.")

# 5. Format for your Blog / Email
print(f"Found {len(all_transactions)} transactions in the last week:\n")
for tx in all_transactions:
    user = tx.get("user", "Unknown User")
    date_str = tx.get("timestamp")
    if date_str is not None:
        date_str = datetime.datetime.fromtimestamp(date_str, datetime.timezone.utc).date()
    print(f"[{date_str}] User '{user}' made a change:")
    print(f"description: {tx.get('description', 'No description')}")
    
    # Each transaction contains a list of specific object edits (add, update, delete)
    print(f"Transaction details: {tx}")
    for change in tx.get("changes", []):
        print(f"Change details: {change}")
        obj_type = change.get("object_type") # e.g., 'person', 'family', 'event'
        action = change.get("action")       # e.g., 'add', 'update', 'delete'
        print(f"  - {action}: {obj_type}")