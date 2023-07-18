import requests
import pandas as pd
from os.path import dirname, join

from model.fpl_attack import FPLAttack
from model.fpl_midfield import FPLMidfield
from model.fpl_defense import FPLDefender
from model.fpl_goalkeeper import FPLGoalkeeper

NUMBER_OF_PLAYERS_TO_SHORTLIST = 150
MINIMUM_NUMBER_OF_MINUTES_PLAYED = 1500
SQUAD_SIZE = 15
BUDGET = 100

base_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
player_data_22_23_file = "players_raw_22_23.csv"

current_dir = dirname(__file__)
player_data_file_path = join(current_dir, "csv_files", player_data_22_23_file)

    
def select_initial_squad():
    """Generates the initial squad for the beginning of the season based off the previous season performance
    and current player cost. Writes the squad into a text file

    Args:
        number_of_star_players (int): The number of players in the squad >= £8.0m
    """
    list_of_df = get_player_data_from_csv_file()
    df_goalkeepers = list_of_df[0]
    df_defenders = list_of_df[1]
    df_midfielders = list_of_df[2]
    df_attackers = list_of_df[3]    

    build_squad(df_goalkeepers, df_defenders, df_midfielders, df_attackers)    
    
def build_squad(df_goalkeepers, df_defenders, df_midfielders, df_attackers):
    """Loop thorugh the dataset until the squad has been filled. Only adds the player if they are validated

    Args:response
        df (_type_): Pandas df_attackers which contains the filtered players
        fpl_team (_type_): FPLTeam object contains all of the validation and squad pre-requisites
    """
    
    fpl_attackers = FPLAttack(star_players=1, budget=BUDGET)
    attackers = select_players(df_attackers, fpl_attackers)
    
    fpl_midfielders = FPLMidfield(star_players=2, budget=fpl_attackers.budget)
    midfielders = select_players(df_midfielders, fpl_midfielders)
    
    fpl_defenders = FPLDefender(star_players=1, budget=fpl_midfielders.budget)
    defenders = select_players(df_defenders, fpl_defenders)
    
    fpl_goalkeepers = FPLGoalkeeper(budget=fpl_defenders.budget)
    goalkeepers = select_players(df_goalkeepers, fpl_goalkeepers)
    
    list_of_players = []
    list_of_players.extend([attackers, midfielders, defenders, goalkeepers])
    
    print(list_of_players)
    
    return list_of_players
    
def select_players(dataframe, fpl_class):
    
    for row in range(len(dataframe)):
        row_data = dataframe.iloc[row]
        player_name = dataframe.index[row]
        player_cost = row_data["now_cost"]
        player_team = row_data["team_code"]
        
        is_player_valid = fpl_class.validate_player(full_name=player_name, cost=player_cost,\
            team=player_team)
        
        if is_player_valid:
            fpl_class.add_player(cost=player_cost, full_name=player_name, team=player_team)
            
        if fpl_class.player_count >= fpl_class.min_no_of_players():
            break
                
    print(f"budget is {fpl_class.budget}")
    
    return fpl_class.players
                
def create_now_cost_series_from_api(df: pd.DataFrame) -> pd.Series:
    """Get player current cost from the FPL api

    Args:
        df_csv (pd.df_attackers): Pandas df_attackers generated from the csv file

    Returns:
        pd.Series: The current cost of FPL players taken from the FPL api
    """
    player_data = get_player_data_from_api()
    df_api = pd.DataFrame.from_dict(player_data)
    df_api = create_full_name_column_and_make_it_the_row_index(df_api)
    df_api = df_api.reindex(df.index)
    element_type_column = df_api["element_type"]
    now_cost_column = df_api["now_cost"] / 10
        
    return now_cost_column, element_type_column

def drop_and_replace_now_cost_column(now_cost_column: pd.Series, element_type_column: pd.Series, df: pd.DataFrame):
    """Drop the current now_cost column and replace with the series generated from the api

    Args:
        now_cost_column (pd.Series): Current player cost series
        df (pd.df_attackers): Pandas df_attackers with old now_cost column

    Returns:
        df (pd.df_attackers): New Pandas df_attackers which contains the new player now_cost
    """
    df.drop("now_cost", axis=1)
    df["now_cost"] = now_cost_column
    df.drop("element_type", axis=1)
    df["element_type"] = element_type_column
    
    return df

def get_player_data_from_csv_file():   
    df = read_csv_create_full_name_header_and_add_player_price_data_from_api()
    df = drop_players_who_dont_meet_playtime_requirements(df)
    df = drop_players_who_are_not_in_the_league_anymore(df)
    df.dropna(subset=["now_cost"], inplace=True)
    list_of_df = calculate_player_ROI_and_shortlist_best_players_based_on_ROI(df, NUMBER_OF_PLAYERS_TO_SHORTLIST)
    
    return list_of_df

def create_full_name_column_and_make_it_the_row_index(df: pd.DataFrame):
    """Create a full name column and make it the row headers

    Args:
        df (pd.df_attackers): The pandas df_attackers to update

    Returns:
      df (pd.df_attackers) : Updated pandas df_attackers
    """
    df["Full Name"] = df["first_name"] + " " + df["second_name"]
    df = df.set_index("Full Name")
    
    return df

def read_csv_create_full_name_header_and_add_player_price_data_from_api():
    """Read the csv file as a df_attackers and add the player 

    Returns:
        df (pd.df_attackers) : Updated pandas df_attackers
    """
    df = pd.read_csv(player_data_file_path)
    df = create_full_name_column_and_make_it_the_row_index(df)
    now_cost_column, element_type_column = create_now_cost_series_from_api(df)
    df = drop_and_replace_now_cost_column(now_cost_column, element_type_column, df)

    return df
	
def drop_players_who_dont_meet_playtime_requirements(df: pd.DataFrame):
    """Drop players from df_attackers who haven'tplayed enough mintues in the last season

    Args:
        df (pd.df_attackers): The df_attackers to be updated

    Returns:
        df (pd.df_attackers) : Updated pandas df_attackers
    """
    df.drop(df[(df["minutes"] <= 1500) | (df["starts_per_90"] <= 1)].index, inplace=True)
    df["ROI"] = (df["points_per_game"].astype(float)) / df["now_cost"]
    df["FPL_Metric"] = df["ROI"] * (df["total_points"])

    return df
 
def calculate_player_ROI_and_shortlist_best_players_based_on_ROI(df: pd.DataFrame, sample_size: int):
    """Calculate player ROI and create a new df_attackers with the top sample_size number of players

    Args:
        df (pd.df_attackers): df_attackers to be updated
        sample_size (int): Number of players to shortlist

    Returns:
        df (pd.df_attackers) : Updated pandas df_attackers
    """
    df_goalkeepers = split_data_by_position(1, df)
    df_defenders = split_data_by_position(2, df)
    df_midfielders = split_data_by_position(3, df)
    df_attackers = split_data_by_position(4, df)
    
    df_list  = []
    df_list.extend([df_goalkeepers, df_defenders, df_midfielders, df_attackers])

    return df_list

def split_data_by_position(position, df):
    df_position_specific = df.drop(df[(df["element_type"] != position)].index)
    # df_columns_filtered = df_position_specific[["total_points", "points_per_game", "now_cost",
    #                                          "starts_per_90", "element_type", "team_code", "FPL_Metric"]]
    df_columns_filtered = df_position_specific.filter(["total_points", "points_per_game", "now_cost", "starts_per_90", "element_type", "team_code", "FPL_Metric"], axis=1)
    df_columns_filtered.sort_values(by=["FPL_Metric"], inplace=True, ascending=False)
    
    return df_columns_filtered

def drop_players_who_are_not_in_the_league_anymore(df):
    """Method for dropping specific players

    Args:
        df (pd.df_attackers): df_attackers to be updated

    Returns:
        df (pd.df_attackers) : Updated pandas df_attackers
    """
    df = df.drop(["Ivan Toney"])
    df = df.drop(["Granit Xhaka"])
    
    return df

def get_player_data_from_api() -> list[dict]:
    """Get player data from the fpl api

    Returns:
        list[dict]: list of players and their fpl data
    """
    response = requests.get(base_url)
    response = response.json()
    player_data = response["elements"]
    
    return player_data