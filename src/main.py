import requests
import pandas as pd
from tabulate import tabulate
from pprint import pprint

from model.fpl_team import FPLTeam

NUMBER_OF_PLAYERS_TO_SHORTLIST = 100
MINIMUM_NUMBER_OF_MINUTES_PLAYED = 1500
SQUAD_SIZE = 15
base_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
player_data_22_23_file = "..\src\data\players_raw_22_23.csv"


""" Get the team data and in a table, sort by Strength """

def get_player_data_from_csv_file():   
    df = read_csv_and_create_full_name_header()
    df = drop_players_who_dont_meet_playtime_requirements(df)
    df = drop_players_who_are_not_in_the_league_anymore(df)
    df = calculate_player_ROI_and_shortlist_best_players_based_on_ROI(df, NUMBER_OF_PLAYERS_TO_SHORTLIST)
    
    return df

def read_csv_and_create_full_name_header():
    df = pd.read_csv(player_data_22_23_file)
    df["Full Name"] = df["first_name"] + " " + df["second_name"]
    df = df.set_index("Full Name")
    
    return df
	
def drop_players_who_dont_meet_playtime_requirements(df: pd.DataFrame):
    df.drop(df[(df["minutes"] <= 1500) | (df["starts_per_90"] <= 1)].index, inplace=True)
    df["now_cost"] = df["now_cost"] / 10
    df["ROI"] = (df["points_per_game"].astype(float)) / df["now_cost"]
    df["FPL_metric"] = df["ROI"] * (df["total_points"])

    return df
 
def calculate_player_ROI_and_shortlist_best_players_based_on_ROI(df: pd.DataFrame, sample_size: int):
	df = df.sort_values(by=["points_per_game_rank"])
	top_x_players_based_on_ROI: pd.DataFrame = df[["total_points", "points_per_game_rank", "points_per_game", "now_cost", "minutes"
                                                , "starts_per_90", "element_type", "ROI", "team_code", "FPL_metric"]].head(sample_size)
	top_x_players_based_on_ROI = top_x_players_based_on_ROI.sort_values(by=["FPL_metric"], ascending=[False])
 
	return top_x_players_based_on_ROI

def drop_players_who_are_not_in_the_league_anymore(df):
    df = df.drop(["Ivan Toney"])
    
    return df   

def select_initial_squad(number_of_star_players: int):
    df = get_player_data_from_csv_file()
    df.to_csv("..\src\data\sort_by_FPL_metric.csv")
    fpl_team = FPLTeam(number_of_star_players)
    fpl_team.get_player_count()

    build_squad(df, fpl_team)
            
            
    with open("my_fpl_team.txt", "a", encoding="utf-8") as f:
        f.write(f"\nTeam with 4 star players: {fpl_team.team} \nThe remaining budget is: {fpl_team.budget}\n")

def build_squad(df, fpl_team):
    while fpl_team.player_count < SQUAD_SIZE - 1:
        for row in range(len(df)):
            row_data = df.iloc[row]
            player_name = df.index[row]
            player_cost = row_data["now_cost"]
            player_position = row_data["element_type"]
            player_team = row_data["team_code"]
            
            is_player_valid = fpl_team.validate_player(player_name, player_cost, player_team, player_position)
            
            if is_player_valid is True:
                fpl_team.add_player(player_cost, player_position, player_name, player_team)
            
   
def get_base_response_data():
	response = requests.get(base_url)
	data = response.json()
	
	return data

select_initial_squad(3)
