import json
from collections import defaultdict
import pandas as pd

# Load division data
with open("division_votes_detailed_last_10_years.json", "r", encoding="utf-8") as f:
    divisions = json.load(f)

print(f"Total divisions loaded: {len(divisions)}")

# Deduplicate divisions by DivisionId
seen_division_ids = set()
unique_divisions = []
for div in divisions:
    division_id = div.get("DivisionId")
    if division_id not in seen_division_ids:
        seen_division_ids.add(division_id)
        unique_divisions.append(div)
    else:
        print(f"Duplicate division skipped: {division_id}")

print(f"Unique divisions after deduplication: {len(unique_divisions)}")

# Counters for debugging
count_divisions_with_votes = 0
total_ayes = 0
total_noes = 0
total_novotes = 0

# Map: MP -> { division_id: vote (+1/-1/0) }
vote_map = defaultdict(dict)

for division in unique_divisions:
    division_id = division.get("DivisionId")
    title = division.get("Title", "<no title>")

    ayes = division.get("Ayes", [])
    noes = division.get("Noes", [])
    novotes = division.get("NoVoteRecorded", [])

    if ayes or noes:
        count_divisions_with_votes += 1
        total_ayes += len(ayes)
        total_noes += len(noes)
        total_novotes += len(novotes)
        print(f"Division {division_id} '{title}' has votes: Ayes={len(ayes)}, Noes={len(noes)}, NoVoteRecorded={len(novotes)}")

        # Add votes to vote_map
        for mp in ayes:
            vote_map[mp["MemberId"]][division_id] = 1
        for mp in noes:
            vote_map[mp["MemberId"]][division_id] = -1
        for mp in novotes:
            vote_map[mp["MemberId"]][division_id] = 0
    else:
        print(f"Division {division_id} '{title}' has NO individual vote data")

print(f"Divisions with recorded individual votes: {count_divisions_with_votes}")
print(f"Total individual votes collected: Ayes={total_ayes}, Noes={total_noes}, NoVoteRecorded={total_novotes}")
print(f"Total MPs with voting records: {len(vote_map)}")

# Convert vote_map to DataFrame
df = pd.DataFrame.from_dict(vote_map, orient="index").fillna(0)

print(f"Data shape (MPs x Divisions): {df.shape}")

# Optional: print a small sample to see data layout
print("Sample data (first 5 MPs and first 5 divisions):")
print(df.iloc[:5, :5])

# Save the DataFrame in Parquet format (most efficient and compressed)
df.to_parquet("mp_vote_map.parquet", compression="snappy")
print("\nSaved DataFrame as mp_vote_map.parquet")

# df.to_csv("mp_vote_map.csv")
# print("Saved DataFrame as mp_vote_map.csv")
