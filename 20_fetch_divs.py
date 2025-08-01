import requests
import json
import time
from datetime import datetime, timedelta
from tqdm import tqdm

BASE_URL = "https://commonsvotes-api.parliament.uk"
SEARCH_URL = f"{BASE_URL}/data/divisions.json/search"
DIVISION_DETAIL_URL = BASE_URL + "/data/division/{division_id}.json"  # single curly braces for .format()

def fetch_division_metadata(since_date: str, take: int = 25, max_divisions: int = 10000):
    divisions = []
    skip = 0

    print(f"Fetching division metadata since {since_date}...")

    while len(divisions) < max_divisions:
        params = {
            "skip": skip,
            "take": take,
            "fromDate": since_date
        }
        resp = requests.get(SEARCH_URL, params=params)
        if resp.status_code != 200:
            print(f"Error: {resp.status_code}")
            break

        batch = resp.json()
        if not batch:
            break

        divisions.extend(batch)
        skip += take
        print(f"Fetched {len(batch)} divisions... (total so far: {len(divisions)})")

        if len(batch) < take:
            break  # No more data

    return divisions

def fetch_division_details(divisions):
    count_with_votes = 0
    count_without_votes = 0
    detailed_data = []
    print(f"\nFetching detailed vote data for {len(divisions)} divisions...\n")
    for div in tqdm(divisions):
        division_id = div["DivisionId"]
        url = DIVISION_DETAIL_URL.format(division_id=division_id)
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("Ayes") or data.get("Noes"):
                    count_with_votes += 1
                    detailed_data.append(data)
                else:
                    count_without_votes += 1
                    print(f"Division {division_id} has no individual vote data")
                # Only append if there are actual votes recorded
                if data.get("Ayes") or data.get("Noes"):
                    detailed_data.append(data)
                else:
                    print(f"Division {division_id} has no individual vote data")
            else:
                print(f"Failed to fetch division {division_id} (status {resp.status_code})")
        except Exception as e:
            print(f"Error fetching division {division_id}: {e}")
        time.sleep(0.2)  # Avoid rate-limiting

    return detailed_data

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"\nSaved to {filename}")

if __name__ == "__main__":
    ten_years_ago = (datetime.utcnow() - timedelta(days=365*10)).strftime("%Y-%m-%d")

    divisions = fetch_division_metadata(since_date=ten_years_ago)
    save_json(divisions, "division_metadata_last_10_years.json")

    detailed = fetch_division_details(divisions)
    save_json(detailed, "division_votes_detailed_last_10_years.json")
