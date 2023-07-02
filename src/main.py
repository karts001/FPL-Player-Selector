import requests
import pandas as pd
from tabulate import tabulate
from pprint import pprint

from model.fpl_team import FPLTeam

NUMBER_OF_PLAYERS_TO_SHORTLIST = 100
MINIMUM_NUMBER_OF_MINUTES_PLAYED = 1500
SQUAD_SIZE = 15
base_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
player_data_22_23_file = ".\src\data\players_raw_22_23.csv"

    
def select_initial_squad(number_of_star_players: int):
    """Generates the initial squad for the beginning of the season based off the previous season performance
    and current player cost. Writes the squad into a text file

    Args:
        number_of_star_players (int): The number of players in the squad >= £8.0m
    """
    df = get_player_data_from_csv_file()    
    df.to_csv(".\src\data\sort_by_FPL_metric.csv")
    fpl_team = FPLTeam(number_of_star_players)
    fpl_team.get_player_count()

    build_squad(df, fpl_team)    
    with open("my_fpl_team.txt", "a", encoding="utf-8") as f:
        f.write(f"\nTeam with 4 star players: {fpl_team.team} \nThe remaining budget is: {fpl_team.budget}\n")
    
def build_squad(df, fpl_team):
    """Loop thorugh the dataset until the squad has been filled. Only adds the player if they are validated

    Args:
        df (_type_): Pandas DataFrame which contains the filtered players
        fpl_team (_type_): FPLTeam object contains all of the validation and squad pre-requisites
    """
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
                
def create_now_cost_series_from_api(df_csv: pd.DataFrame):
    """Get player current cost from the FPL api

    Args:
        df_csv (pd.DataFrame): Pandas DataFrame generated from the csv file

    Returns:
        pd.Series: The current cost of FPL players taken from the FPL api
    """
    response = requests.get(base_url)
    response = response.json()
    player_data = response["elements"]
    df_api = pd.DataFrame.from_dict(player_data)
    now_cost_column = df_api["now_cost"] / 10
        
    return now_cost_column

def drop_and_replace_now_cost_column(now_cost_column: pd.Series, df: pd.DataFrame):
    """Drop the current now_cost column and replace with the series generated from the api

    Args:
        now_cost_column (pd.Series): Current player cost series
        df (pd.DataFrame): Pandas dataframe with old now_cost column

    Returns:
        df (pd.DataFrame): New Pandas DataFrame which contains the new player now_cost
    """
    df.drop(["now_cost"])
    df["now_cost"] = now_cost_column
    
    return df

def get_player_data_from_csv_file():   
    df = read_csv_create_full_name_header_and_add_player_price_data_from_api()
    df = drop_players_who_dont_meet_playtime_requirements(df)
    df = drop_players_who_are_not_in_the_league_anymore(df)
    df = calculate_player_ROI_and_shortlist_best_players_based_on_ROI(df, NUMBER_OF_PLAYERS_TO_SHORTLIST)
    
    return df

def create_full_name_column_and_make_it_the_row_index(df: pd.DataFrame):
    """Create a full name column and make it the row headers

    Args:
        df (pd.DataFrame): The pandas dataframe to update

    Returns:
      df (pd.DataFrame) : Updated pandas dataframe
    """
    df["Full Name"] = df["first_name"] + " " + df["second_name"]
    df = df.set_index("Full Name")
    
    return df

def read_csv_create_full_name_header_and_add_player_price_data_from_api():
    """Read the csv file as a DataFrame and add the player 

    Returns:
        df (pd.DataFrame) : Updated pandas dataframe
    """
    df = pd.read_csv(player_data_22_23_file)
    now_cost_column = create_now_cost_series_from_api(df)
    df = drop_and_replace_now_cost_column(now_cost_column, df)
    df = create_full_name_column_and_make_it_the_row_index(df)
    
    return df
	
def drop_players_who_dont_meet_playtime_requirements(df: pd.DataFrame):
    """Drop players from DataFrame who haven'tplayed enough mintues in the last season

    Args:
        df (pd.DataFrame): The DataFrame to be updated

    Returns:
        df (pd.DataFrame) : Updated pandas dataframe
    """
    df.drop(df[(df["minutes"] <= 1500) | (df["starts_per_90"] <= 1)].index, inplace=True)
    df["ROI"] = (df["points_per_game"].astype(float)) / df["now_cost"]
    df["FPL_metric"] = df["ROI"] * (df["total_points"])

    return df
 
def calculate_player_ROI_and_shortlist_best_players_based_on_ROI(df: pd.DataFrame, sample_size: int):
    """Calculate player ROI and create a new DataFrame with the top sample_size number of players

    Args:
        df (pd.DataFrame): DataFrame to be updated
        sample_size (int): Number of players to shortlist

    Returns:
        df (pd.DataFrame) : Updated pandas dataframe
    """
    df = df.sort_values(by=["points_per_game_rank"])
    top_x_players_based_on_ROI: pd.DataFrame = df[["total_points", "points_per_game_rank", "points_per_game", "now_cost", "minutes"
                                                , "starts_per_90", "element_type", "ROI", "team_code", "FPL_metric"]].head(sample_size)
    top_x_players_based_on_ROI = top_x_players_based_on_ROI.sort_values(by=["FPL_metric"], ascending=[False])
 
    return top_x_players_based_on_ROI

def drop_players_who_are_not_in_the_league_anymore(df):
    """Method for dropping specific players

    Args:
        df (_type_): DataFrame to be updated

    Returns:
        df (pd.DataFrame) : Updated pandas dataframe
    """
    df = df.drop(["Ivan Toney"])
    return df            
   
def get_base_response_data():
	response = requests.get(base_url)
	data = response.json()
	
	return data

select_initial_squad(3)
