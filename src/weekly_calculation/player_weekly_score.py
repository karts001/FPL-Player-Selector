"""Calculate a custom metric to rank players per game week

This metric will use their historical Return on Investment, Fixture Difficulty and their current form

"""

import numpy as np
import pandas as pd
from os.path import dirname, join

from common.team_conversion import string_to_int_map
from common.fpl_get_endpoint import get_player_data_from_api
import common.pandas_methods as pdm
import file_paths as fp
from get_matchday_odds import get_matchday_odds


def create_separate_columns_from_team_probability_class(team_probability):
    attribute_dict = {
        "Probabilities": team_probability.probabilities,
        "Average Probability": team_probability.average_probabilities
    }
    return attribute_dict


# Get data from csv file
full_path = fp.get_filtered_players_csv_path()

# Convert csv file to correct format
df = pd.read_csv(full_path)
df = pdm.create_full_name_column_and_make_it_the_row_index(df)
df_fpl_and_roi = df.filter(["FPL_Metric", "ROI"])

# Get data from fpl endpoint
player_data = get_player_data_from_api()
df_fpl = pdm.convert_api_response_to_pandas_dataframe(player_data)
df_fpl = pdm.create_full_name_column_and_make_it_the_row_index(df_fpl)
df_fpl = pdm.filter_columns(df_fpl)

# Concatenate the two dataframes
df_fpl_and_roi = df_fpl_and_roi.reindex(df_fpl.index)
df_fpl = pd.concat([df_fpl, df_fpl_and_roi], axis=1)
df_fpl["FPL_Metric"] = df_fpl["FPL_Metric"].replace(np.nan, 0)
df_fpl["ROI"] = df_fpl["ROI"].replace(np.nan, 0)

# Create new columns to display a weekly score
dict_of_gameweek_odds = get_matchday_odds()
translated_dict = {string_to_int_map.get(k, k): v for k, v in dict_of_gameweek_odds.items()}
df_fpl["TeamProbability"] = df_fpl["team"].map(translated_dict)
df_fpl = df_fpl[df_fpl["TeamProbability"].notna()]
new_columns_df = df_fpl['TeamProbability'].apply(create_separate_columns_from_team_probability_class).apply(pd.Series)
df_fpl = pd.concat([df_fpl, new_columns_df], axis=1)
df_fpl["One Match Probability"] = df_fpl.Probabilities.apply(lambda x: x[0])
df_fpl = pdm.convert_column_to_float(df_fpl, "form")
df_fpl = pdm.convert_column_to_float(df_fpl, "ict_index")
df_fpl["FPL Weekly Score"] = ((0.1 * df_fpl["form"]) + (2 * df_fpl["One Match Probability"]) + (1.5 * df_fpl["Average Probability"]) + (0.1 * df_fpl["ict_index"]) + (0.01 * df_fpl["FPL_Metric"]))

try:
    df_fpl.drop(df[(df["chance_of_playing_next_round"]) <= 50.0].index, inplace=True)
except KeyError:
    pass

df_fpl["chance_of_playing_next_round"] = df_fpl["chance_of_playing_next_round"].fillna(100.0)
df_fpl["chance_of_playing_this_round"] = df_fpl["chance_of_playing_this_round"].fillna(100.0)
df_fpl.sort_values(by="FPL Weekly Score", ascending=False, inplace=True)
df_fpl["rank"] = np.arange(df_fpl.shape[0]) + 1

df_fpl.to_csv("src/player_weekly_score.csv")
