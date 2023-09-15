import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(override=True)
base_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
manager_id = "5701404"
manager_base_url = f"https://fantasy.premierleague.com/api/entry/{manager_id}"
my_team_endpoint = f"https://fantasy.premierleague.com/api/my-team/{manager_id}/"


password = os.getenv("FPL_PASSWORD")
login = os.getenv("FPL_LOGIN")
cookie = os.getenv("FPL_SESSION_COOKIE")

string = f"""pl_profile={cookie}"""

headers = {
        "cookie": string
    }

def sort_base_response_by_id():
    response = get_player_data_from_api()
    response = sorted(response, key=lambda k: k.get("id", 0))
    
    return response

def _get_base_response():
    
    response = requests.get(base_url)
    response = response.json()
    
    return response

def get_manager_response():
    response = requests.get(manager_base_url)
    response = response.json()
    return response

def _get_my_team():    
    response = requests.get(my_team_endpoint, headers=headers)
    response = response.json()
    
    return response

def get_player_data_from_api() -> list[dict]:
    """Get player data from the fpl api

    Returns:
        list[dict]: list of players and their fpl data
    """
    response = _get_base_response()
    player_data = response["elements"]
    
    return player_data

def get_current_fpl_team() -> list:
    """Get current FPL team from endpoint

    Returns:
        picks list: list of 15 elements whih are in the current FPL team
    """
    
    response = _get_my_team()
    picks = response["picks"]
    
    return picks

def get_remaining_free_transfer() -> int:
    """Get remaining free transfers in current gameweek

    Returns:
        int: number of free transfers in gameweek
    """

    response = _get_my_team()
    transfers = response.get("transfers")
    limit = transfers.get("limit")
    
    return limit    

def get_remaining_balance() -> int:
    """Get remaining fpl team balance

    Returns:
        balance int: amount of money left in £m
    """
    
    response = _get_my_team()
    transfers = response["transfers"]
    balance = transfers.get("bank")
    
    return balance / 10

def get_current_gameweek():
    response = _get_base_response()
    events = response["events"]
    # check if current date is before deadline
    # if it is break out of loop and take the gameweek
    today = _get_today()
    iso_date = today.isoformat()
    
    for gameweek_data in events:
        deadline = gameweek_data["deadline_time"]
        if iso_date > deadline:
           continue
        else:
            current_gameweek = gameweek_data["id"]
            return current_gameweek
        
def _get_today():
    return datetime.now()
