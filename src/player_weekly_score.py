"""Calculate a custom metric to rank players per game week

This metric will use their historical Return on Investment, Fixture Difficulty and their current form

"""

import numpy as np
import pandas as pd
from os.path import dirname, join

from build_initial_squad import get_player_data_from_csv_file

from common.team_conversion import string_to_int_map

from common.fpl_get_endpoint import get_player_data_from_api
import common.pandas_methods as pdm 
from get_matchday_odds import get_matchday_odds


def custom_function(team_probability):
    attribute_dict = {
        "Probabilities": team_probability.probabilities,
        "Average Probability": team_probability.average_probability
    }
    return attribute_dict

filtered_players_file = "filtered_players.csv"
current_dir = dirname(__file__)
full_path = join(current_dir, "csv_files", filtered_players_file)

# df = get_player_data_from_csv_file(file_path=full_path)
# df_roi = df.sort_values(by="ROI", ascending=False)
# df_fpl = df.sort_values(by="FPL_Metric", ascending=False)

df = pd.read_csv(full_path)
df = pdm.create_full_name_column_and_make_it_the_row_index(df)
df_fpl_and_roi = df.filter(["FPL_Metric", "ROI"])

player_data = get_player_data_from_api()
df_fpl = pdm.convert_api_response_to_pandas_dataframe(player_data)
df_fpl = pdm.create_full_name_column_and_make_it_the_row_index(df_fpl)
df_fpl = pdm.filter_columns(df_fpl)


df_fpl_and_roi = df_fpl_and_roi.reindex(df_fpl.index)
df_fpl = pd.concat([df_fpl, df_fpl_and_roi], axis=1)
df_fpl["FPL_Metric"] = df_fpl["FPL_Metric"].replace(np.nan, 0)
df_fpl["ROI"] = df_fpl["ROI"].replace(np.nan, 0)


dict_of_gameweek_odds = get_matchday_odds()
translated_dict = {string_to_int_map.get(k, k): v for k, v in dict_of_gameweek_odds.items()}
df_fpl["TeamProbability"] = df_fpl["team"].map(translated_dict)
df_fpl = df_fpl[df_fpl["TeamProbability"].notna()]
new_columns_df = df_fpl['TeamProbability'].apply(custom_function).apply(pd.Series)
df_fpl = pd.concat([df_fpl, new_columns_df], axis=1)
df_fpl["One Match Probability"] = df_fpl.Probabilities.apply(lambda x: x[0])
df_fpl["form"] = df_fpl["form"].astype(float)
df_fpl["FPL Weekly Score"] = (df_fpl["form"] + (2 * df_fpl["One Match Probability"]) + (1.5 * df_fpl["Average Probability"])) * df_fpl["FPL_Metric"]
df_fpl.sort_values(by="FPL Weekly Score", ascending=False, inplace=True)



print(df_fpl)
