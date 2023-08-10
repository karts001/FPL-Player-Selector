import requests

base_url = "https://fantasy.premierleague.com/api/bootstrap-static/"

def get_player_data_from_api() -> list[dict]:
    """Get player data from the fpl api

    Returns:
        list[dict]: list of players and their fpl data
    """
    response = requests.get(base_url)
    response = response.json()
    player_data = response["elements"]
    
    return player_data
