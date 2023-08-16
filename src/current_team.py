"""Get current team from FPL"""

import common.fpl_get_endpoint as fpl
import common.pandas_methods as pdm
import common.team_conversion as tc
import file_paths as fp
import requests

current_gameweek = fpl.get_current_gameweek()
get_current_team_data = f"https://fantasy.premierleague.com/api/event/{current_gameweek}/live/"

current_team = fpl.get_current_fpl_team()
remaining_balance = fpl.get_remaining_balance()

"""Create a dataframe which contains my team and their fpl weekly score"""

# List of player's element number   
list_of_player_element = [current_team[index]["element"] for index in range(len(current_team))]

# Find the associated player data from player_weekly_score.csv
file_path = fp.get_player_weekly_score_csv_path()
df_player_score = pdm.convert_data_to_dataframe(file_path)
df_player_score = df_player_score.set_index("Full Name")
req_data = df_player_score.loc[:, ["FPL Weekly Score", "rank"]]

player_data = fpl.get_player_data_from_api()
response = requests.get(get_current_team_data).json()

# Data of each player in squad in a list
squad_data = [response["elements"][element - 1] for element in list_of_player_element]

# Clean the data and put it in a pandas dataframe
df = pdm.convert_squad_data_into_a_dataframe(squad_data)
df["Full Name"] = df["id"].map(tc.squad_element_map)
df = df.set_index("Full Name")

df = pdm.concatenate_dataframes(df, req_data)
df = df.head(15)
df = pdm.convert_column_to_int(df, "rank")
df.sort_values(by=["rank"], ascending=True, inplace=True)

print(df)
