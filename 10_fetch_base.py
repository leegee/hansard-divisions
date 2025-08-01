# Voting history from Hansard
# https://commonsvotes-api.parliament.uk/swagger/ui/index#/Divisions

import requests
import time
import json

BASE_URL = "https://commonsvotes-api.parliament.uk/data/divisions.json/search"
TAKE = 25

def fetch_all_divisions():
    skip = 0
    all_divisions = []
    while True:
        params = {"skip": skip, "take": TAKE}
        resp = requests.get(BASE_URL, params=params)
        if resp.status_code != 200:
            print(f"Error fetching divisions at skip={skip}: {resp.status_code}")
            break
        divisions = resp.json()
        if not divisions:
            break
        all_divisions.extend(divisions)
        print(f"Fetched {len(divisions)} divisions starting at {skip}")
        skip += TAKE
        time.sleep(0.2)  # be polite to the API
    return all_divisions

if __name__ == "__main__":
    divisions = fetch_all_divisions()
    with open("uk_parliament_divisions.json", "w", encoding="utf-8") as f:
        json.dump(divisions, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(divisions)} divisions.")
