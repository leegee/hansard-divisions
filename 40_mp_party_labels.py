import json
from collections import defaultdict

with open('division_votes_detailed_last_10_years.json', 'r', encoding='utf-8') as f:
    divisions = json.load(f)

mp_party = dict()
party_colours = dict()

for division in divisions:
    for side in ['Ayes', 'Noes']:
        for mp in division.get(side, []):
            mp_id = mp['MemberId']
            if mp_id not in mp_party:
                mp_party[mp_id] = {
                    'Name': mp['Name'],
                    'Party': mp['Party'],
                    'PartyAbbreviation': mp['PartyAbbreviation'],
                    'PartyColour': mp['PartyColour'],
                }

    # Tellers may be included later if desired

# Now map party abbreviation to colour
for mp_data in mp_party.values():
    abbr = mp_data['PartyAbbreviation']
    colour = mp_data['PartyColour']
    if abbr and colour and abbr not in party_colours:
        party_colours[abbr] = colour

# Save results
with open('mp_party.json', 'w', encoding='utf-8') as f:
    json.dump(mp_party, f, indent=2)

with open('party_colours.json', 'w', encoding='utf-8') as f:
    json.dump(party_colours, f, indent=2)
