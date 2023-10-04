"""Calculate a custom metric to rank players per game week

This metric will use their historical Return on Investment, Fixture Difficulty and their current form

"""

import numpy as np
import pandas as pd

from src.common.team_conversion import string_to_int_map
from src.common.fpl_get_endpoint import get_player_data_from_api
import src.common.pandas_methods as pdm
from src.weekly_calculation.get_matchday_odds import get_matchday_odds


def calculate_player_score():
    df_fpl_api = _get_data_from_fpl_api()
    df_probabilities = _add_gameweek_odds_as_new_column_of_the_dataframe(df_fpl_api)
    df_weekly_score = _calcualte_fpl_weekly_score_and_add_to_data_frame(df_probabilities)
    _sort_data_frame_by_fpl_weekly_score_and_save_to_a_csv_file(df_weekly_score)
    

def _create_separate_columns_from_team_probability_class(team_probability):
    attribute_dict = {
        "Probabilities": team_probability.probabilities,
        "Average Probability": team_probability.average_probabilities
    }
    return attribute_dict

def _get_data_from_fpl_api():
    # Get data from fpl endpoint
    player_data = get_player_data_from_api()
    df_fpl = pdm.convert_api_response_to_pandas_dataframe(player_data)
    df_fpl = pdm.create_full_name_column_and_make_it_the_row_index(df_fpl)
    df_fpl = pdm.filter_columns(df_fpl)
    
    return df_fpl

def _add_gameweek_odds_as_new_column_of_the_dataframe(df_fpl):
    # Create new columns to display a weekly score
    dict_of_gameweek_odds = get_matchday_odds()
    translated_dict = {string_to_int_map.get(k, k): v for k, v in dict_of_gameweek_odds.items()}
    df_fpl["TeamProbability"] = df_fpl["team"].map(translated_dict)
    df_fpl = df_fpl[df_fpl["TeamProbability"].notna()]
    new_columns_df = df_fpl['TeamProbability'].apply(_create_separate_columns_from_team_probability_class).apply(pd.Series)
    df_fpl = pd.concat([df_fpl, new_columns_df], axis=1)
    df_fpl["One Match Probability"] = df_fpl.Probabilities.apply(lambda x: x[0])
    df_fpl = pdm.convert_column_to_float(df_fpl, "form")
    df_fpl = pdm.convert_column_to_float(df_fpl, "ict_index")
    df_fpl["chance_of_playing_next_round"] = df_fpl["chance_of_playing_next_round"].fillna(100.0)
    df_fpl["chance_of_playing_this_round"] = df_fpl["chance_of_playing_this_round"].fillna(100.0)
    
    return df_fpl

def _calcualte_fpl_weekly_score_and_add_to_data_frame(df_fpl):
    df_fpl["fpl_weekly_score"] = ((0.1 * df_fpl["form"]) + (2 * df_fpl["One Match Probability"]) + (1.5 * df_fpl["Average Probability"])
                                  + (0.1 * df_fpl["ict_index"]) + ((df_fpl["chance_of_playing_this_round"]/100) -1) )
    df_fpl.drop(df_fpl[df_fpl["fpl_weekly_score"] < 0].index, inplace=True)
    df_fpl["fpl_weekly_score"] = df_fpl["fpl_weekly_score"].round(2)
    df_fpl.loc[df_fpl["status"] == "i", ["fpl_weekly_score", "chance_of_playing_this_round"]] = 0.0
    df_fpl.loc[df_fpl["status"] == "s", ["fpl_weekly_score", "chance_of_playing_this_round"]] = 0.0

    return df_fpl

def _sort_data_frame_by_fpl_weekly_score_and_save_to_a_csv_file(df_fpl):
    df_fpl.sort_values(by="fpl_weekly_score", ascending=False, inplace=True)
    df_fpl["rank"] = np.arange(df_fpl.shape[0]) + 1
    df_fpl.to_csv("../player_weekly_score.csv")
