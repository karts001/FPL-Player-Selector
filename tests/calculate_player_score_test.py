import pandas as pd
import pytest
from unittest.mock import patch

from src.weekly_calculation.player_weekly_score import _add_gameweek_odds_as_new_column_of_the_dataframe, _calcualte_fpl_weekly_score_and_add_to_data_frame
from src.weekly_calculation.get_matchday_odds import TeamProbabilities


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
            "status": ["i"],
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
        assert "Probabilities" in df.columns
        assert "Average Probability" in df.columns
        assert "One Match Probability" in df.columns
    
def test_players_who_are_injured_or_suspended_have_an_fpl_score_of_zero(basic_dataframe):
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
    

