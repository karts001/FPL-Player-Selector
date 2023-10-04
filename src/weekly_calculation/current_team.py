"""Get current team from FPL"""

from collections import namedtuple
from operator import attrgetter
import pandas as pd

import src.common.fpl_get_endpoint as fpl
import src.common.pandas_methods as pdm
import src.file_paths as fp
from src.model.fpl_team import FPLTeam
from src.common.team_conversion import position_mapper, int_to_string_map
from src.sql_app.database import engine, get_db
from src.sql_app.models import SuggestedAttackerTransfers, SuggestedCombinedTransfers, \
SuggestedDefenderTransfers, SuggestedGoalkeeperTransfers, SuggestedMidfielderTransfers

current_gameweek_m1 = fpl.get_current_gameweek() - 1
current_gameweek_data_endpoint = f"https://fantasy.premierleague.com/api/event/{current_gameweek_m1}/live/"

"""Create a dataframe which contains my team and their fpl weekly score"""

TransferData = namedtuple("TransferData", ["player_in", "chance_of_playing_this_round",
                            "element_type", "cost", "team", "rank",
                            "score_delta", "player_out", "fpl_weekly_score", "gameweek"])

SquadData = namedtuple("SquadData", ["fpl_team", "df_pop", "team_frequency"])


def combined_transfers() -> pd.DataFrame:
    """
    Get the best suggested transfer (based off FPL Weekly Score) for each position

    Returns:
        pd.DataFrame: Dataframe containing the best suggested transfer for each position. This dataframe is then displayed
        on a dashboard using Plotly Dash
    """
    if fpl.get_current_gameweek() == _get_gameweek_from_database():
        df = read_from_db()
    else:  
        print("recalculating values")     
        squad_data = _select_best_team_from_current_squad()
        goalkeeper = _top_x_players_for_a_position(squad_data.df_pop, 1, squad_data.fpl_team, squad_data.team_frequency, no_of_players_in_list=1)
        defender = _top_x_players_for_a_position(squad_data.df_pop, 2, squad_data.fpl_team, squad_data.team_frequency, no_of_players_in_list=1)
        midfielder = _top_x_players_for_a_position(squad_data.df_pop, 3, squad_data.fpl_team, squad_data.team_frequency, no_of_players_in_list=1)
        attacker = _top_x_players_for_a_position(squad_data.df_pop, 4, squad_data.fpl_team, squad_data.team_frequency, no_of_players_in_list=1)
        potential_transfers = [goalkeeper[0], defender[0], midfielder[0], attacker[0]]
        df = _make_dataframe_readable(potential_transfers)
        df.to_sql(name="suggested-combined-transfers", con=engine, if_exists="replace") 
    
    return df

def transfer_list(position: int, no_of_players_in_list: int) -> pd.DataFrame:
    """
    Create a dataframe containing the top {no_of_players_in_list} suggested transfers for a given position
    Args:
        position (int): Position to create the list for
        no_of_players_in_list (int): Number of suggested transfers to find

    Returns:
        pd.DataFrame: _description_
    """
    if position == 1:
        table = SuggestedGoalkeeperTransfers
        table_name = "suggested-goalkeeper-transfers"
    if position == 2:
        table = SuggestedDefenderTransfers
        table_name = "suggested-defender-transfers"  
    if position == 3:
        table = SuggestedMidfielderTransfers
        table_name = "suggested-midfielder-transfers"
    if position == 4:
        table = SuggestedAttackerTransfers
        table_name = "suggested-attacker-transfers"
        
    if fpl.get_current_gameweek() == _get_gameweek_from_database(table):
        print("getting from database")
        df = pd.read_sql(table_name, con=engine)
    else:
        print("recalculating values")
        squad_data = _select_best_team_from_current_squad()
        top_3_players = _top_x_players_for_a_position(squad_data.df_pop, position, squad_data.fpl_team, squad_data.team_frequency, no_of_players_in_list)
        df = _make_dataframe_readable(top_3_players)
        _update_database(df, position)
    
    return df

def read_from_db():
    print("getting from database")
    df = pd.read_sql("suggested-combined-transfers", con=engine)
    
    return df

def _get_gameweek_from_database(table=SuggestedCombinedTransfers) -> int:
    """
    Get the gameweek currently held in the database
    Args:
        table (BaseTransfers, optional): The database to look for the gameweek
        Defaults to SuggestedCombinedTransfers.

    Returns:
        int: Gamweek held in the selected database
    """
    try:
        db = next(get_db())
        gameweek = db.query(table).first().gameweek
    
    except AttributeError:
        gameweek = 0
    return gameweek

def _select_best_team_from_current_squad() -> SquadData:
    """
    Select the best (valid) combination of 11 players from the current squad
    Returns:
        SquadData: fpl_team contains the current squad players and associated gameweek data.
                   req_data contains the same gameweek data for the rest of the players
                   team_frequency tracks the number of players from a certain team  
    """
    list_of_player_ids = _create_a_list_of_squad_ids()
    req_data = _trim_df_columns(True)
    squad_data = _get_squad_player_data(list_of_player_ids)
    player_population_data = something()
    df_pop = _convert_squad_data_list_into_df(player_population_data, req_data)
    df_squad = _convert_squad_data_list_into_df(squad_data, req_data).head(15)
    df_squad.sort_values(by=["fpl_rank"], ascending=True, inplace=True)
    team_frequency = _count_number_of_players_from_same_team(df_squad)
    fpl_team = _select_and_validate_team_from_squad(df_squad)
    
    squad_data = SquadData(fpl_team, df_pop, team_frequency)
    
    return squad_data

# List of player's element number
def _create_a_list_of_squad_ids() -> list: 
    """
    Create a list of the squad ids of the current fpl squad
    Returns:
        list: list of squad ids of the current fpl squad
    """
    list_of_player_element = [fpl.get_current_fpl_team()[index]["element"] for index in range(15)]
    return list_of_player_element

# Find the associated player data from player_weekly_score.csv
def _trim_df_columns(include_coptr_col: bool) -> pd.DataFrame:
    """
    Create a dataframe from the csv file for all the "elements" in fpl but also trim down the columns and reformat the
    dataframe
    Returns:
        pd.DataFrame: _description_
    """
    file_path = fp.get_player_weekly_score_csv_path()
    df_player_score = pdm.convert_data_to_dataframe(file_path)
    df_player_score = df_player_score.set_index("Full Name")
    df_player_score.rename(columns={"rank": "fpl_rank"}, inplace=True)

    if include_coptr_col:
        req_data = df_player_score.loc[:, ["fpl_weekly_score", "fpl_rank"]]
    else:
        req_data = df_player_score.loc[:, ["fpl_weekly_score", "fpl_rank"]]
    
    return req_data

# Get fpl stats for players in squad
def _get_squad_player_data(list_of_player_ids: list) -> list:
    """
    Get data for each player in squad from the fpl api
    Args:
        list_of_player_ids list: list of player ids in current squad

    Returns:
        list: list of player data of players in current squad
    """
    players_in_id_order = fpl.sort_base_response_by_id()
    squad_data = [players_in_id_order[element - 1] for element in list_of_player_ids]
    
    return squad_data

def something() -> list:
    """
    Get data for each player in squad from the fpl api
    Args:
        list_of_player_ids list: list of player ids in current squad

    Returns:
        list: list of player data of players in current squad
    """
    players_in_id_order = fpl.sort_base_response_by_id()
    
    return players_in_id_order

# Clean the data and put it in a pandas dataframe
def _convert_squad_data_list_into_df(squad_data: list, req_data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the squad_data dataframe and concatenate with the req_data dataframe
    Args:
        squad_data (pd.DataFrame): Dataframe containing squad data
        req_data (pd.DataFrame): Dataframe containing data on all players in fpl

    Returns:
        pd.DataFrame: Concatenated dataframe
    """
    
    df = pdm.convert_squad_data_into_a_dataframe(squad_data)
    df = pdm.create_full_name_column_and_make_it_the_row_index(df)
    df.drop(["first_name", "second_name"], axis=1, inplace=True)
    df = pdm.concatenate_dataframes(df, req_data)
    df["now_cost"] = df["now_cost"] / 10
        
    return df

def _count_number_of_players_from_same_team(df) -> pd.Series:
    team_frequency = df["team"].value_counts()
    team_frequency.loc
    
    return team_frequency
    
def _select_and_validate_team_from_squad(df):
    fpl_team = FPLTeam()
    PlayerData = namedtuple("PlayerData", ["id", "fpl_rank", "name", "element_type", "score", "cost", "team", "chance_of_playing_this_round"])
    goalkeepers = df.loc[df["element_type"] == 1]
    defenders = df.loc[df["element_type"] == 2]
    midfielders = df.loc[df["element_type"] == 3]
    attackers = df.loc[df["element_type"] == 4]
    
    fpl_team, df_trimmed_1 = _select_best_player_in_position(goalkeepers, PlayerData, fpl_team)
    fpl_team, df_trimmed_2 = _select_top_3_defenders(defenders, PlayerData, fpl_team)
    fpl_team, df_trimmed_3 = _select_best_player_in_position(attackers, PlayerData, fpl_team)
    
    remaining_players = pd.concat([df_trimmed_1, df_trimmed_2, df_trimmed_3, midfielders])
    remaining_players.sort_values(by=["fpl_weekly_score"], ascending=False, inplace=True)
    
    top_6_from_remaining = remaining_players.head(6)
    bottom_4_from_remaining = remaining_players.tail(4)
    
    for row in top_6_from_remaining.iterrows():
        _add_player_data_to_fpl_team_class(fpl_team, PlayerData, row, "team")
        
    for row in bottom_4_from_remaining.iterrows():
        _add_player_data_to_fpl_team_class(fpl_team, PlayerData, row, "bench")
    
    return fpl_team
    
def _move_player_to_team(PlayerData, row, fpl_team):

    player_data = PlayerData(id=row.id, fpl_rank=row.fpl_rank, name=row.name, element_type=row.element_type,
                            score=row.fpl_weekly_score, cost=row.now_cost, team=row.team, 
                            chance_of_playing_this_round=row.chance_of_playing_this_round)
    fpl_team.team.append(player_data)
    

def _select_best_player_in_position(df, PlayerData, fpl_team):
    row = df.iloc[0]
    _move_player_to_team(PlayerData, row, fpl_team)
    df_trimmed = df.drop(df.index[0])
    
    return fpl_team, df_trimmed
    
def _select_top_3_defenders(df, PlayerData, fpl_team):
    row = df.iloc[0]
    _move_player_to_team(PlayerData, row, fpl_team)
    row = df.iloc[1]
    _move_player_to_team(PlayerData, row, fpl_team)
    row = df.iloc[2]
    _move_player_to_team(PlayerData, row, fpl_team)
    
    df_trimmed = df.drop(df.index[[0,1,2]])
    
    return fpl_team, df_trimmed
    
def _add_player_data_to_fpl_team_class(fpl_team, PlayerData, row, team_or_bench):
    player_data = PlayerData(id=row[1].id, fpl_rank=row[1].fpl_rank, name=row[0], element_type=row[1].element_type,
                            score=row[1].fpl_weekly_score, cost=row[1].now_cost, team=row[1].team,
                            chance_of_playing_this_round=row[1].chance_of_playing_this_round)
    
    if team_or_bench == "team":
        fpl_team.team.append(player_data)
    else:
        fpl_team.bench.append(player_data)
        
def _make_dataframe_readable(potential_transfers):
    df = pd.DataFrame(potential_transfers)
    df["team"] = df["team"].map(int_to_string_map)
    df["element_type"] = df["element_type"].map(position_mapper)    
    return df

def _create_list_of_players_per_position(fpl_team, position):
    position_list = [player for player in fpl_team.team if player.element_type == position]
    position_list.extend(player for player in fpl_team.bench if player.element_type == position)
    position_list.sort(key=attrgetter("fpl_rank"))
    
    return position_list

def _get_desired_data_from_data_frame(row):
    DataFrameData = namedtuple("DataFrameData", ["name", "position",
                                                             "chance_of_playing", "cost",
                                                             "team", "fpl_rank",
                                                             "score"])
    
    name = row[0]
    position = row[1].element_type
    chance_of_playing = row[1].chance_of_playing_this_round
    cost = row[1].now_cost
    team = row[1].team
    fpl_rank = row[1].fpl_rank
    score = round(row[1].fpl_weekly_score, 3)
    
    data = DataFrameData(name, position, chance_of_playing, cost, team, fpl_rank, score)
    
    return data

def _update_database(df, position):
    #TODO: save to a database instead (postgres)
    if position == 1:
        df.to_sql(name="suggested-goalkeeper-transfers", con=engine, if_exists="replace")
    if position == 2:
        df.to_sql(name="suggested-defender-transfers", con=engine, if_exists="replace")
    if position == 3:
        df.to_sql(name="suggested-midfielder-transfers", con=engine, if_exists="replace")
    if position == 4:
        df.to_sql(name="suggested-attacker-transfers", con=engine, if_exists="replace")

def _top_x_players_for_a_position(req_data, position, fpl_team, team_frequency, no_of_players_in_list):
    #TODO: Calculate expected team scores with suggested players and add another column to dashboard with team score
    # use deepcopy etc.
    top_x_transfers_per_position = []
    position_data = req_data.loc[req_data["element_type"] == position]
    position_data.sort_values(by="fpl_weekly_score", ascending=False, inplace=True)
    for row in position_data.iterrows():
        data = _get_desired_data_from_data_frame(row)
        position_list = _create_list_of_players_per_position(fpl_team, position)
        if len(top_x_transfers_per_position) == no_of_players_in_list:
                return top_x_transfers_per_position
        number_of_players_from_specific_team = team_frequency.get(row[1].team, 0)
        if number_of_players_from_specific_team == 3:
            #TODO: There will be cases where we want to replace this player with a player from their team.
            # 3 players from team already
            continue
        
        if _player_already_in_team(position_list, data):
            continue
        
        balance = fpl.get_remaining_balance()        
        if (position_list[-1].cost + balance) > row[1].now_cost:
            data.name
            score_delta = round(row[1].fpl_weekly_score - position_list[-1].score, 3)
            # if score_delta > 0:
            transfer_data = TransferData(data.name, data.chance_of_playing,
                                            data.position, data.cost, data.team, data.fpl_rank,
                                            score_delta, position_list[-1].name, data.score, fpl.get_current_gameweek())
             
            top_x_transfers_per_position.append(transfer_data)

def _player_already_in_team(position_list, data):
    for player in position_list:
        if player.name == data.name:
            return True
        else:
            continue
    return False

def get_current_team():
    list_of_player_ids = _create_a_list_of_squad_ids()
    req_data = _trim_df_columns(False)
    df = convert_api_data_to_data_frame(list_of_player_ids, req_data)
    df = df.head(15)
    df.sort_values(by=["fpl_rank"], ascending=True, inplace=True)
    df["chance_of_playing_this_round"] = df["chance_of_playing_this_round"].fillna(df["chance_of_playing_next_round"])
    df["chance_of_playing_this_round"] = df["chance_of_playing_this_round"].fillna(100.0)
    df["Full Name"] = df.index
    df["element_type"] = df["element_type"].map(position_mapper)
    df.loc[df["status"] == "i", ["fpl_weekly_score", "chance_of_playing_this_round"]] = 0.0
    df.loc[df["status"] == "s", ["fpl_weekly_score", "chance_of_playing_this_round"]] = 0.0
    
    return df

def convert_api_data_to_data_frame(list_of_player_ids: list, req_data: pd.DataFrame):
    squad_data = _get_squad_player_data(list_of_player_ids)
    df = _convert_squad_data_list_into_df(squad_data, req_data)  
    
    return df
