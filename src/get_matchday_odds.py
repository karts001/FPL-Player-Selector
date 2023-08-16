import requests
from dotenv import load_dotenv
import os
from collections import namedtuple
import pandas as pd

from common.team_conversion import string_to_int_map

load_dotenv()
PL_ODDS_API_KEY = os.getenv("PL_ODDS_API_KEY")
sport = "soccer_epl"
region = "uk"
odds_dict = {}

class TeamProbabilities:
    def __init__(self, team_name):
        self.team_name = team_name
        self.probabilities = []
        self.average_probabilities = 0
        
    def calculate_average_probabilities(self):
        if len(self.probabilities) != 0:
            average = sum(self.probabilities) / len(self.probabilities)
            return average



def get_matchday_odds() -> dict:
    """Get match day odds from odds-api

    Returns:
        list[team_probability]: list of odds for each match in the gameweek
    """
    premier_league_odds_api = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={PL_ODDS_API_KEY}&regions={region}"
    response = requests.get(premier_league_odds_api).json()

    for fixture in response:
        match_outcome = get_match_outcomes(fixture)
        odds_dict = add_probabilities_to_dict(match_outcome)
        
    return odds_dict

def convert_h2h_odds_to_probabilities(h2h_odds: float) -> float:
    """Convert head to head odds into probabilities

    Args:
        h2h_odds (float): H2H odds from betting site

    Returns:
        float: Odds converted to probabilities
    """
    converted_odds = 1 / h2h_odds
    return converted_odds

def get_match_outcomes(fixture: dict) -> list[dict]:
    """Get william hill odds for each match in the game week

    Args:
        fixture (dict): Dictionary for each match in the gameweek

    Returns:
        list[dict]: List of dictionaries containing each teams win probability
    """
    william_hill_odds = fixture.get("bookmakers")[1]
    william_hill_market = william_hill_odds.get("markets")[0]
    match_outcome = william_hill_market.get("outcomes")
    
    return match_outcome

def add_probabilities_to_dict(match_outcome: dict) -> dict:
    """Create a list containing all of the probabilities of each game in the game week

    Args:
        match_outcome (dict): Dictionary containing the probabilities of the gameweek

    Returns:
        odds_dict (dict): List containing the probabilities of each match in the gameweek
    """

    home_team_name = match_outcome[0]["name"]
    away_team_name = match_outcome[1]["name"]
    home_probability = round(convert_h2h_odds_to_probabilities(match_outcome[0]["price"]), 3)
    away_probability = round(convert_h2h_odds_to_probabilities(match_outcome[1]["price"]), 3)
    
    home_team = TeamProbabilities(home_team_name)
    away_team = TeamProbabilities(away_team_name)
    
    if odds_dict.get(home_team_name, None) == None:
        
        home_team.team_name = home_team_name
        home_team.probabilities.append(home_probability)
        odds_dict.update({
        home_team_name: home_team
        })    
    else:
        odds_dict.get(home_team_name).probabilities.append(home_probability)
    
    if odds_dict.get(away_team_name, None) == None:
        
        away_team.probabilities.append(away_probability)
        away_team.team_name = away_team_name
        odds_dict.update({
        away_team_name: away_team
        })
        
    else:
        odds_dict.get(away_team_name).probabilities.append(away_probability)

    odds_dict.get(home_team_name).average_probabilities = odds_dict.get(home_team_name).calculate_average_probabilities()
    odds_dict.get(away_team_name).average_probabilities = odds_dict.get(away_team_name).calculate_average_probabilities()
    return odds_dict

def get_probability_average(list_of_win_probabilities: list) -> int:
    average_probability = sum(list_of_win_probabilities)/len(list_of_win_probabilities)
    
    return average_probability
