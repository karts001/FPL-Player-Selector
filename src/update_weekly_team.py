import requests
from dotenv import load_dotenv
import os
from collections import namedtuple

load_dotenv()
PL_ODDS_API_KEY = os.getenv("PL_ODDS_API_KEY")
sport = "soccer_epl"
region = "uk"
odds_list = []
team_probability = namedtuple("team_probability", ["name", "win_probability"])

def get_matchday_odds() -> list[team_probability]:
    """Get match day odds from odds-api

    Returns:
        list[team_probability]: list of odds for each match in the gameweek
    """
    premier_league_odds_api = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={PL_ODDS_API_KEY}&regions={region}"
    response = requests.get(premier_league_odds_api).json()

    for fixture in response:
        match_outcome = get_match_outcomes(fixture)
        odds_list = add_probabilities_to_list(match_outcome)
        
    return odds_list

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

def add_probabilities_to_list(match_outcome: dict) -> list[team_probability]:
    """Create a list containing all of the probabilities of each game in the game week

    Args:
        match_outcome (dict): Dictionary containing the probabilities of the gameweek

    Returns:
        list[team_probability]: List containing the probabilities of each match in the gameweek
    """
    home_team = team_probability(match_outcome[0]["name"], convert_h2h_odds_to_probabilities(match_outcome[0]["price"]))
    away_team = team_probability(match_outcome[1]["name"], convert_h2h_odds_to_probabilities(match_outcome[1]["price"]))
    odds_list.append((home_team, away_team))
    
    return odds_list
