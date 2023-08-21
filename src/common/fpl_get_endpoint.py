import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()



base_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
manager_id = "5701404"
manager_base_url = f"https://fantasy.premierleague.com/api/entry/{manager_id}"
my_team_endpoint = f"https://fantasy.premierleague.com/api/my-team/{manager_id}/"


password = os.getenv("FPL_PASSWORD")
login = os.getenv("FPL_LOGIN")
cookie = os.getenv("FPL_SESSION_COOKIE")

string = """pl_profile=eyJzIjogIld6SXNNemt3TVRneU9UaGQ6MXFVTjRYOldHRG9sM2hxTGowNkVGb1ZuSkdQYl9TVmduem5VZ1lfQ2IwVkY0VE1TNzgiLCAidSI6IHsiaWQiOiAzOTAxODI5OCwgImZuIjogIlNoaXZhIiwgImxuIjogIkthcnRoaWtleWFuIiwgImZjIjogMTR9fQ=="""

headers = {
        "cookie": string
    }

def get_base_response():
    
    response = requests.get(base_url)
    response = response.json()
    
    return response

def get_manager_response():
    response = requests.get(manager_base_url)
    response = response.json()
    return response

def get_my_team():
    # session = authenticate_login()
    # headers = {
    #     "cookie": string
    # }
    
    response = requests.get(my_team_endpoint, headers=headers)
    response = response.json()
    
    return response

def get_player_data_from_api() -> list[dict]:
    """Get player data from the fpl api

    Returns:
        list[dict]: list of players and their fpl data
    """
    response = get_base_response()
    player_data = response["elements"]
    
    return player_data

def get_current_gameweek() -> int:
    """Get the current gameweek from the response object

    Returns:
        int gameweek: The current gameweek
    """
    response = get_manager_response()
    gameweek = response["started_event"]
    
    return gameweek

def get_current_fpl_team() -> list:
    """Get current FPL team from endpoint

    Returns:
        picks list: list of 15 elements whih are in the current FPL team
    """
    
    response = get_my_team()
    picks = response["picks"]
    
    return picks

def get_remaining_free_transfer() -> int:
    """Get remaining free transfers in current gameweek

    Returns:
        int: number of free transfers in gameweek
    """

    response = get_my_team()
    transfers = response.get("transfers")
    limit = transfers.get("limit")
    
    return limit    

def get_remaining_balance() -> int:
    """Get remaining fpl team balance

    Returns:
        balance int: amount of money left in £m
    """
    
    response = get_my_team()
    transfers = response["transfers"]
    balance = transfers.get("bank")
    
    return balance / 10
