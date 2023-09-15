"""Get current team from FPL"""

import requests
from collections import namedtuple
from operator import attrgetter
import pandas as pd

import src.common.fpl_get_endpoint as fpl
import src.common.pandas_methods as pdm
import src.common.team_conversion as tc
import src.file_paths as fp
from src.model.fpl_team import FPLTeam
from src.common.team_conversion import position_mapper, int_to_string_map
from src.sql_app.database import engine, get_db
from src.sql_app.models import SuggestedAttackerTransfers, SuggestedCombinedTransfers, \
SuggestedDefenderTransfers, SuggestedGoalkeeperTransfers, SuggestedMidfielderTransfers

      
def get_gameweek_from_database(table=SuggestedCombinedTransfers):
    db = next(get_db())
    gameweek = db.query(table).first().gameweek
    
    return gameweek
    

current_gameweek = fpl.get_current_gameweek()
current_gameweek_data_endpoint = f"https://fantasy.premierleague.com/api/event/{current_gameweek-1}/live/"

"""Create a dataframe which contains my team and their fpl weekly score"""

TransferData = namedtuple("TransferData", ["player_in", "chance_of_playing_next_round",
                            "element_type", "cost", "team", "rank",
                            "score_delta", "player_out", "fpl_weekly_score", "gameweek"])

SquadData = namedtuple("SquadData", ["fpl_team", "req_data", "team_frequency"])

def combined_transfers():
    if current_gameweek == get_gameweek_from_database():
        print("getting from database")
        df = pd.read_sql("suggested-combined-transfers", con=engine)
    else:  
        print("recalculating values")     
        squad_data = select_best_team_from_current_squad()
        goalkeeper = top_x_players_for_a_position(squad_data.req_data, 1, squad_data.fpl_team, squad_data.team_frequency, no_of_players_in_list=1)
        defender = top_x_players_for_a_position(squad_data.req_data, 2, squad_data.fpl_team, squad_data.team_frequency, no_of_players_in_list=1)
        midfielder = top_x_players_for_a_position(squad_data.req_data, 3, squad_data.fpl_team, squad_data.team_frequency, no_of_players_in_list=1)
        attacker = top_x_players_for_a_position(squad_data.req_data, 4, squad_data.fpl_team, squad_data.team_frequency, no_of_players_in_list=1)
        potential_transfers = [goalkeeper[0], defender[0], midfielder[0], attacker[0]]
        df = make_dataframe_readable(potential_transfers)
        df.to_sql(name="suggested-combined-transfers", con=engine, if_exists="replace") 
    
    return df

def select_best_team_from_current_squad():
    list_of_player_ids = create_a_list_of_squad_ids()
    req_data = trim_df_columns()
    squad_data = get_squad_player_data(list_of_player_ids)
    df = convert_squad_data_list_into_df(squad_data, req_data)
    team_frequency = count_number_of_players_from_same_team(df)
    fpl_team = select_and_validate_team_from_squad(df)
    
    squad_data = SquadData(fpl_team, req_data, team_frequency)
    
    return squad_data

# List of player's element number
def create_a_list_of_squad_ids(): 
    list_of_player_element = [fpl.get_current_fpl_team()[index]["element"] for index in range(15)]
    return list_of_player_element

# Find the associated player data from player_weekly_score.csv
def trim_df_columns():
    file_path = fp.get_player_weekly_score_csv_path()
    df_player_score = pdm.convert_data_to_dataframe(file_path)
    df_player_score = df_player_score.set_index("Full Name")
    req_data = df_player_score.loc[:, ["fpl_weekly_score", "rank", "element_type", "chance_of_playing_this_round", "now_cost", "team"]]
    
    return req_data

def get_squad_player_data(list_of_player_ids):

    # player_data = fpl.get_player_data_from_api()
    response = requests.get(current_gameweek_data_endpoint).json()
    squad_data = [response["elements"][element - 1] for element in list_of_player_ids]
    
    return squad_data

# Clean the data and put it in a pandas dataframe
def convert_squad_data_list_into_df(squad_data, req_data):
    
    df = pdm.convert_squad_data_into_a_dataframe(squad_data)
    df["Full Name"] = df["id"].map(tc.squad_element_map)
    df = df.set_index("Full Name")

    df = pdm.concatenate_dataframes(df, req_data)
    df = df.head(15)
    df = pdm.convert_column_to_int(df, "rank")
    df.sort_values(by=["rank"], ascending=True, inplace=True)
    
    return df

def count_number_of_players_from_same_team(df):
    team_frequency = df["team"].value_counts()
    team_frequency.loc
    
    return team_frequency

def check_if_position_is_on_limit(fpl_team, position):
    
    if position == 1 and fpl_team.goalkeepers == 1:
        return True
    if position == 2 and fpl_team.defenders == 3:
        return True
    if position == 3 and fpl_team.attackers == 1:
        return True
    
def select_and_validate_team_from_squad(df):
    fpl_team = FPLTeam()
    PlayerData = namedtuple("PlayerData", ["id", "rank", "name", "element_type", "score", "cost", "team"])
    goalkeepers = df.loc[df["element_type"] == 1]
    defenders = df.loc[df["element_type"] == 2]
    midfielders = df.loc[df["element_type"] == 3]
    attackers = df.loc[df["element_type"] == 4]
    
    fpl_team, df_trimmed_1 = select_best_player_in_position(goalkeepers, PlayerData, fpl_team)
    fpl_team, df_trimmed_2 = select_top_3_defenders(defenders, PlayerData, fpl_team)
    fpl_team, df_trimmed_3 = select_best_player_in_position(attackers, PlayerData, fpl_team)
    
    remaining_players = pd.concat([df_trimmed_1, df_trimmed_2, df_trimmed_3, midfielders])
    remaining_players.sort_values(by=["fpl_weekly_score"], ascending=False, inplace=True)
    
    top_6_from_remaining = remaining_players.head(6)
    bottom_4_from_remaining = remaining_players.tail(4)
    
    for row in top_6_from_remaining.iterrows():
        add_player_data_to_fpl_team_class(fpl_team, PlayerData, row, "team")
        
    for row in bottom_4_from_remaining.iterrows():
        add_player_data_to_fpl_team_class(fpl_team, PlayerData, row, "bench")
    
    return fpl_team
    
def move_player_to_team(PlayerData, row, fpl_team):

    player_data = PlayerData(id=row.id, rank=row[26], name=row.name, element_type=row.element_type,
                            score=row.fpl_weekly_score, cost=row.now_cost, team=row.team)
    fpl_team.team.append(player_data)
    

def select_best_player_in_position(df, PlayerData, fpl_team):
    row = df.iloc[0]
    move_player_to_team(PlayerData, row, fpl_team)
    df_trimmed = df.drop(df.index[0])
    
    return fpl_team, df_trimmed
    
def select_top_3_defenders(df, PlayerData, fpl_team):
    row = df.iloc[0]
    move_player_to_team(PlayerData, row, fpl_team)
    row = df.iloc[1]
    move_player_to_team(PlayerData, row, fpl_team)
    row = df.iloc[2]
    move_player_to_team(PlayerData, row, fpl_team)
    
    df_trimmed = df.drop(df.index[[0,1,2]])
    
    return fpl_team, df_trimmed
    
def add_player_data_to_fpl_team_class(fpl_team, PlayerData, row, team_or_bench):
    player_data = PlayerData(id=row[1].id, rank=row[1][26], name=row[0], element_type=row[1].element_type,
                            score=row[1].fpl_weekly_score, cost=row[1].now_cost, team=row[1].team)
    
    if team_or_bench == "team":
        fpl_team.team.append(player_data)
    else:
        fpl_team.bench.append(player_data)
        
def make_dataframe_readable(potential_transfers):
    df = pd.DataFrame(potential_transfers)
    df["team"] = df["team"].map(int_to_string_map)
    df["element_type"] = df["element_type"].map(position_mapper)    
    return df

def create_list_of_players_per_position(fpl_team, position):
    position_list = [player for player in fpl_team.team if player.element_type == position]
    position_list.extend(player for player in fpl_team.bench if player.element_type == position)
    position_list.sort(key=attrgetter("rank"))
    
    return position_list

def get_desired_data_from_data_frame(row):
    DataFrameData = namedtuple("DataFrameData", ["name", "position",
                                                             "chance_of_playing", "cost",
                                                             "team", "rank",
                                                             "score"])
    
    name = row[0]
    position = row[1].element_type
    chance_of_playing = row[1].chance_of_playing_this_round
    cost = row[1].now_cost
    team = row[1].team
    rank = row[1][1]
    score = round(row[1].fpl_weekly_score, 3)
    
    data = DataFrameData(name, position, chance_of_playing, cost, team, rank, score)
    
    return data

def transfer_list(position, no_of_players_in_list):
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
        
    if current_gameweek == get_gameweek_from_database(table):
        print("getting from database")
        df = pd.read_sql(table_name, con=engine)
    else:
        print("recalculating values")
        squad_data = select_best_team_from_current_squad()
        top_3_players = top_x_players_for_a_position(squad_data.req_data, position, squad_data.fpl_team, squad_data.team_frequency, no_of_players_in_list)
        df = make_dataframe_readable(top_3_players)
        save_to_corresponding_file(df, position)
    
    return df

def save_to_corresponding_file(df, position):
    #TODO: save to a database instead (postgres)
    if position == 1:
        # df.to_csv("src/csv_files/goalkeeper_transfers.csv")
        df.to_sql(name="suggested-goalkeeper-transfers", con=engine, if_exists="replace")
    if position == 2:
        # df.to_csv("src/csv_files/defender_transfers.csv")
        df.to_sql(name="suggested-defender-transfers", con=engine, if_exists="replace")
    if position == 3:
        # df.to_csv("src/csv_files/midfielder_transfers.csv")
        df.to_sql(name="suggested-midfielder-transfers", con=engine, if_exists="replace")
    if position == 4:
        # df.to_csv("src/csv_files/attacker_transfers.csv")
        df.to_sql(name="suggested-attacker-transfers", con=engine, if_exists="replace")

def top_x_players_for_a_position(req_data, position, fpl_team, team_frequency, no_of_players_in_list):
    #TODO: Calculate expected team scores with suggested players and add another column to dashboard with team score
    # use deepcopy etc.
    top_x_transfers_per_position = []
    position_data = req_data.loc[req_data["element_type"] == position]
    for row in position_data.iterrows():
        data = get_desired_data_from_data_frame(row)
        position_list = create_list_of_players_per_position(fpl_team, position)
        if len(top_x_transfers_per_position) == no_of_players_in_list:
                return top_x_transfers_per_position
        number_of_players_from_specific_team = team_frequency.get(row[1].team, 0)
        if number_of_players_from_specific_team == 3:
            #TODO: There will be cases where we want to replace this player with a player from their team.
            # 3 players from team already
            continue
        
        if player_already_in_team(position_list, data):
            continue
        
        balance = fpl.get_remaining_balance()        
        if (position_list[-1].cost + balance) > row[1].now_cost:
            score_delta = round(row[1].fpl_weekly_score - position_list[-1].score, 3)
            transfer_data = TransferData(data.name, data.chance_of_playing,
                                            data.position, data.cost, data.team, data.rank,
                                            score_delta, position_list[-1].name, data.score, fpl.get_current_gameweek())
            
            top_x_transfers_per_position.append(transfer_data)

def player_already_in_team(position_list, data):
    for player in position_list:
        if player.name == data.name:
            return True
        else:
            continue
    return False
