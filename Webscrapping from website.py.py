import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
import re

# Base URL for fetching state-wise party results
base_url = "https://results.eci.gov.in/PcResultGenJune2024/partywiseresult-{}.htm"

# State codes obtained from the dropdown menu
state_codes = [
    ("U01", "Andaman & Nicobar Islands"), ("S01", "Andhra Pradesh"), ("S02", "Arunachal Pradesh"),
    ("S03", "Assam"), ("S04", "Bihar"), ("U02", "Chandigarh"), ("S26", "Chhattisgarh"),
    ("U03", "Dadra & Nagar Haveli"), ("S05", "Goa"), ("S06", "Gujarat"),
    ("S07", "Haryana"), ("S08", "Himachal Pradesh"), ("U08", "Jammu and Kashmir"), ("S27", "Jharkhand"),
    ("S10", "Karnataka"), ("S11", "Kerala"), ("U09", "Ladakh"), ("U06", "Lakshadweep"), ("S12", "Madhya Pradesh"),
    ("S13", "Maharashtra"), ("S14", "Manipur"), ("S15", "Meghalaya"), ("S16", "Mizoram"), ("S17", "Nagaland"),
    ("U05", "NCT OF Delhi"), ("S18", "Odisha"), ("U07", "Puducherry"), ("S19", "Punjab"), ("S20", "Rajasthan"),
    ("S21", "Sikkim"), ("S22", "Tamil Nadu"), ("S29", "Telangana"), ("S23", "Tripura"), ("S24", "Uttar Pradesh"),
    ("S28", "Uttarakhand"), ("S25", "West Bengal")
]

# Function to fetch and process state-wise party results
def fetch_statewise_party_results(state_code, state_name):
    # Construct the URL for the given state code
    url = base_url.format(state_code)
    
    # Send a GET request to the state-specific URL
    response = requests.get(url)
    response.encoding = 'utf-8'

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the state name from the page title or other relevant element
        state_name = state_name  # State name from function argument

        # Initialize variables to track party-wise results for the state
        party_results = defaultdict(int)

        # Find the table containing party-wise results
        state_table = soup.find('table', {'class': 'table'})

        if state_table:
            # Extract the data rows
            rows = state_table.find_all('tr')

            for row in rows[1:]:  # Skip header row if necessary
                cols = row.find_all('td')
                if len(cols) >= 3:  # Adjust column indices based on actual structure
                    party = cols[0].text.strip()
                    seats = int(cols[1].text.strip())
                    vote_percent = float(cols[2].text.strip())
                    party_results[party] += seats

            # Find the party with maximum seats won in this state
            if party_results:
                max_party = max(party_results, key=party_results.get)
                print(f"In {state_name}, {max_party} won with {party_results[max_party]} seats.")

        else:
            print(f"Party-wise results table not found for {state_name}")
    else:
        print(f"Failed to retrieve the state page for {url}. Status code: {response.status_code}")

    return party_results, state_name

# Dictionary to store total wins per party across all states
total_wins = defaultdict(int)
state_wise_results = []

# Fetch and process party-wise results for each state code
for state_code, state_name in state_codes:
    state_party_results, state_name = fetch_statewise_party_results(state_code, state_name)
    state_wise_results.append({
        'State': state_name,
        'Party Results': state_party_results
    })
    for party, wins in state_party_results.items():
        total_wins[party] += wins

# Convert total wins dictionary to DataFrame
total_wins_df = pd.DataFrame(list(total_wins.items()), columns=['Party', 'Total Wins'])

# Sort DataFrame by Total Wins (highest to lowest)
total_wins_df = total_wins_df.sort_values(by='Total Wins', ascending=False)

# Export total wins DataFrame to Excel with adjusted sheet names
excel_file = "election_results_analysis.xlsx"
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    # Export total wins data
    total_wins_df.to_excel(writer, sheet_name='Total Wins', index=False)

    # Export state-wise results
    for state_result in state_wise_results:
        state_name = state_result['State']
        # Truncate state name if necessary to fit within Excel's limit of 31 characters
        truncated_state_name = re.sub(r'[^\w\s]', '', state_name)[:31]
        party_results = state_result['Party Results']
        state_results_df = pd.DataFrame(list(party_results.items()), columns=['Party', f'Wins in {truncated_state_name}'])
        state_results_df.to_excel(writer, sheet_name=f'State_{truncated_state_name}', index=False)

print(f"\nAnalysis data exported to {excel_file}")

# Print total wins DataFrame
print("\nTotal Wins DataFrame (sorted by Total Wins):")
print(total_wins_df)

# Display top parties and their wins in each state
for state_result in state_wise_results:
    state_name = state_result['State']
    party_results = state_result['Party Results']
    max_party = max(party_results, key=party_results.get)
    print(f"In {state_name}, {max_party} won with {party_results[max_party]} seats.")
