import pytest
from statistics import mean

from src.weekly_calculation.get_matchday_odds import get_matchday_odds, TeamProbabilities

@pytest.fixture
def get_odds_dict():
    odds_dict = get_matchday_odds()
    return odds_dict

@pytest.fixture
def get_probabilities_for_spceific_team():
    team_name = "Liverpool"
    odds_dict = get_matchday_odds()
    
    return odds_dict[team_name]

def test_odds_dict_contains_20_keys(get_odds_dict):

    
    assert len(get_odds_dict) == 20
    
def test_odds_dict_contains_TeamProbabilities_object(team_odds):

    
    assert isinstance(team_odds, TeamProbabilities)
    
def test_average_probabilities_property_is_correctly_calculated(team_odds):
    list_of_probs = team_odds.probabilities
    average_probabilities = team_odds.average_probabilities
    
    assert mean(list_of_probs) == average_probabilities