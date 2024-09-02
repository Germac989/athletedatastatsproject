import requests
import pandas as pd

# API key for API-SPORTS Football API
API_KEY = 'apikey'

# Define the base URL
BASE_URL = "https://v3.football.api-sports.io"

# Set up headers required for the API requests
headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}


def fetch_data(endpoint, params=None):
    """Fetch data from the API endpoint and print debugging information."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        print(f"API Request URL: {response.url}")
        print(f"API Response Status Code: {response.status_code}")
        print(f"Full API Response: {data}")
        return data
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


def fetch_leagues():
    """Fetch available leagues to verify league ID."""
    data = fetch_data('leagues')
    if data:
        print("Available Leagues:")
        for league in data.get('response', []):
            print(f"ID: {league.get('league', {}).get('id')}, Name: {league.get('league', {}).get('name')}")
    else:
        print("Failed to fetch leagues.")


def process_player_statistics(data):
    """Process player statistics data."""
    if not data:
        print("No data to process.")
        return pd.DataFrame()  # Return an empty DataFrame if no data

    players = data.get('response', [])
    if not players:
        print("No player data found in the response.")
        return pd.DataFrame()  # Return an empty DataFrame if no data found

    player_data = []
    for player in players:
        player_info = player.get('statistics', [{}])[0]

        # Debug: Print the player_info for inspection
        print(f"Processing player info: {player_info}")

        # Safely handle numeric values
        passes_attempted = player_info.get('passes', {}).get('attempted', 0)
        passes_completed = player_info.get('passes', {}).get('total', 0)
        try:
            incomplete_passes = int(passes_attempted) - int(passes_completed)
        except (ValueError, TypeError):
            incomplete_passes = 'N/A'

        player_stats = {
            'Player Name': player.get('player', {}).get('name', 'N/A'),
            'Team': player.get('team', {}).get('name', 'N/A'),
            'Goals': player_info.get('goals', {}).get('total', 'N/A'),
            'Assists': player_info.get('goals', {}).get('assists', 'N/A'),
            'Minutes Played': player_info.get('minutes', {}).get('total', 'N/A'),
            'Completed Passes': player_info.get('passes', {}).get('total', 'N/A'),
            'Incomplete Passes': incomplete_passes,
            'Tackles': player_info.get('tackles', {}).get('total', 'N/A'),
            'Interceptions': player_info.get('interceptions', {}).get('total', 'N/A'),
            'Dribbles': player_info.get('dribbles', {}).get('total', 'N/A'),
            'Shots': player_info.get('shots', {}).get('total', 'N/A'),
            'Saves': player_info.get('goalkeeper', {}).get('saves', 'N/A') if player.get('goalkeeper') else 'N/A',
            'Clean Sheets': player_info.get('goalkeeper', {}).get('clean_sheets', 'N/A') if player.get('goalkeeper') else 'N/A'
        }
        player_data.append(player_stats)

    print(f"Processed {len(player_data)} player records.")
    return pd.DataFrame(player_data)


def fetch_all_players(season, league):
    """Fetch all player statistics across multiple pages."""
    page = 1
    all_players = []
    while True:
        params = {'season': season, 'league': league, 'page': page}
        data = fetch_data('players', params=params)

        if not data or not data.get('response'):
            print(f"No more data at page {page}.")
            break

        # Append the data from the current page
        players = data.get('response', [])
        if not players:
            print(f"No player data found on page {page}.")
            break

        all_players.extend(players)
        print(f"Fetched page {page} with {len(players)} results.")

        # Check if there are more pages
        paging = data.get('paging', {})
        current_page = paging.get('current', 0)
        total_pages = paging.get('total', 0)
        if current_page >= total_pages:
            break

        page += 1

    return all_players


# Fetch and print available leagues
fetch_leagues()

# Define parameters
season = 2020
league = 39

# Fetch all player data
players_data = fetch_all_players(season, league)
print(f"Total players fetched: {len(players_data)}")

# Convert the data to a DataFrame
df = process_player_statistics({'response': players_data})

# Debug: Check if DataFrame is empty
if df.empty:
    print("DataFrame is empty. No data to export.")
else:
    # Export the DataFrame to a CSV file
    output_file = 'player_performance_stats.csv'
    df.to_csv(output_file, index=False)
    print(f"Player performance stats have been exported to {output_file}")
