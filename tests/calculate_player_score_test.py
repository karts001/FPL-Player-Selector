import pandas as pd
import pytest
from unittest.mock import patch

from src.weekly_calculation.player_weekly_score import _add_gameweek_odds_as_new_column_of_the_dataframe, _calcualte_fpl_weekly_score_and_add_to_data_frame
from src.weekly_calculation.get_matchday_odds import TeamProbabilities

@pytest.fixture
def mock_full_dataframe():
    df = pd.DataFrame(
        {
            "element_type": [1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4],
            "team": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
            "form": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
            "ict_index": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
            "now_cost": [1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4],
            "ict_index_rank": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
            "chance_of_playing_next_round": [0.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0],
            "chance_of_playing_this_round": [0.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0,100.0],
            "Full Name": list("abcdefghijklmnopqrst")
        }
    )
    df.set_index("Full Name", inplace=True)
    
    return df

@pytest.fixture
def basic_dataframe():
    df = pd.DataFrame(
        {
            "element_type": [1],
            "team": [1],
            "form": [1],
            "ict_index": [1],
            "now_cost": [1],
            "ict_index_rank": [1],
            "chance_of_playing_next_round": [0.0],
            "chance_of_playing_this_round": [0.0],
            "Full Name": list("a")
        }
    )
    df.set_index("Full Name", inplace=True)
    return df
    
def test_that_gameweek_odds_column_is_added_to_the_dataframe(basic_dataframe):
    with patch("src.weekly_calculation.player_weekly_score.get_matchday_odds") as mock_gameweek_odds:
        mock_team_probability = TeamProbabilities("Arsenal")
        mock_team_probability.probabilities = [0.5]
        mock_team_probability.average_probabilities = 0.5
        mock_gameweek_odds.return_value = {
            "Arsenal": mock_team_probability
        }
        df = _add_gameweek_odds_as_new_column_of_the_dataframe(basic_dataframe)

        assert "TeamProbability" in df.columns
        assert "Probability" in df.columns
        assert "Average Probability" in df.columns
    
def test_players_who_have_0_percent_chance_of_playing_in_the_next_round_have_a_0_fpl_weekly_score(basic_dataframe):
    with patch("src.weekly_calculation.player_weekly_score.get_matchday_odds") as mock_gameweek_odds:
        mock_team_probability = TeamProbabilities("Arsenal")
        mock_team_probability.probabilities = [0.5]
        mock_team_probability.average_probabilities = 0.5
        mock_gameweek_odds.return_value = {
            "Arsenal": mock_team_probability
        }
        df = _add_gameweek_odds_as_new_column_of_the_dataframe(basic_dataframe)
        df = _calcualte_fpl_weekly_score_and_add_to_data_frame(df)
    
        assert df.loc["a"].fpl_weekly_score == 0
    

