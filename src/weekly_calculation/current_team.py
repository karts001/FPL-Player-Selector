"""Get current team from FPL"""

import requests
from collections import namedtuple
from operator import attrgetter

import src.common.fpl_get_endpoint as fpl
import src.common.pandas_methods as pdm
import src.common.team_conversion as tc
import src.file_paths as fp
from src.model.fpl_team import FPLTeam


current_gameweek_data_endpoint = f"https://fantasy.premierleague.com/api/event/{fpl.get_current_gameweek()}/live/"

"""Create a dataframe which contains my team and their fpl weekly score"""

def rank_current_squad():
    list_of_player_ids = create_a_list_of_squad_ids()
    req_data = trim_df_columns()
    squad_data = get_squad_player_data(list_of_player_ids)
    df = convert_squad_data_list_into_df(squad_data, req_data)
    team_frequency = count_number_of_players_from_same_team(df)
    fpl_team = select_and_validate_team_from_squad(df)
    
    goalkeeper = get_highest_ranked_player_not_in_squad_for_a_given_position(fpl_team, req_data, 1)
    defender = get_highest_ranked_player_not_in_squad_for_a_given_position(fpl_team, req_data, 2)
    midfielder = get_highest_ranked_player_not_in_squad_for_a_given_position(fpl_team, req_data, 3)
    attacker = get_highest_ranked_player_not_in_squad_for_a_given_position(fpl_team, req_data, 4)
    
    PotentialTransfers = namedtuple("PotentialTransfers", ["goalkeeper", "defender", "midfielder", "attacker"])
    potential_transfers = PotentialTransfers(goalkeeper, defender, midfielder, attacker)
    
    return potential_transfers
    

# List of player's element number
def create_a_list_of_squad_ids(): 
    list_of_player_element = [fpl.get_current_fpl_team()[index]["element"] for index in range(15)]
    return list_of_player_element

# Find the associated player data from player_weekly_score.csv
def trim_df_columns():
    file_path = fp.get_player_weekly_score_csv_path()
    df_player_score = pdm.convert_data_to_dataframe(file_path)
    df_player_score = df_player_score.set_index("Full Name")
    req_data = df_player_score.loc[:, ["FPL Weekly Score", "rank", "element_type", "chance_of_playing_this_round", "now_cost", "team"]]
    
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

def select_and_validate_team_from_squad(df):
    fpl_team = FPLTeam()
    PlayerData = namedtuple("PlayerData", ["id", "rank", "name", "element_type", "score", "cost", "team"])
    is_team_valid = False
    
    while not is_team_valid: 
        for row in df.itertuples():
            add_player_data_to_fpl_team_class(fpl_team, PlayerData, row)
            
        if fpl_team.validate_team():
            is_team_valid = True
            break
        else:
            # team is invalid. Remove lowest scoring player and replace with first player on bench
            missing_positions = [k for k, v in fpl_team.validation_tracker.items() if v == False]
            lowest_ranked_player_in_starting_eleven = fpl_team.team.pop(-1)
            fpl_team.bench.append(lowest_ranked_player_in_starting_eleven)
            
            for position in missing_positions:
                if position == "goalkeeper":
                    for player in fpl_team.bench:
                        if player.element_type == 1:
                            fpl_team.bench.remove(player)
                            fpl_team.team.append(player)
                            fpl_team.goalkeeper += 1
                            if fpl_team.validate_team():
                                is_team_valid = True
                                break
        
    
    fpl_team.team.sort(key=attrgetter("rank"))
    fpl_team.bench.sort(key=attrgetter("rank"))
    
    return fpl_team

def add_player_data_to_fpl_team_class(fpl_team, PlayerData, row):
    player_data = PlayerData(id=row.id, rank=row.rank, name=row.Index, element_type=row.element_type,
                            score=row._26, cost=row.now_cost, team=row.team)
    if len(fpl_team.team) >= 11:
        fpl_team.bench.append(player_data)
    else:        
        fpl_team.team_score += row._26
        fpl_team.team.append(player_data)
        fpl_team.increment_position_counter(row.element_type)
    
def get_highest_ranked_player_not_in_squad_for_a_given_position(fpl_team, req_data, position):
    position_data = req_data.loc[req_data["element_type"] == position]
    for row in position_data.itertuples():
        team = row.team
                
        name = row.Index
        
        count = 0
        position_list = [player for player in fpl_team.team if player.element_type == position]
        position_list.extend(player for player in fpl_team.bench if player.element_type == position)
        position_list.sort(key=attrgetter("rank"))
        
        for player in position_list:
            if player.name == name:
            # player already in team
                break
            else:
                count += 1
                if count == len(position_list):
                    balance = fpl.get_remaining_balance()
                    # TODO: need to check if more than 3 players from one team        
                    if (position_list[-1].cost + balance) > row.now_cost:
                        # can afford this player
                        score_delta = row._1 - position_list[-1].score
                        TransferData = namedtuple("TransferData", ["row_data", "score_delta", "player_out"])
                        transfer_data = TransferData(row, score_delta, position_list[-1].name)
                        return transfer_data
                    else:
                        # can't afford player
                        continue
rank_current_squad()