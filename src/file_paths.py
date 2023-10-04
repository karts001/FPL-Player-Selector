from os.path import dirname, join


def get_filtered_players_csv_path():
    filtered_players_file = "filtered_players.csv"
    current_dir = dirname(__file__)
    full_path = join(current_dir, filtered_players_file)
    
    return full_path

def get_raw_player_data_path():
    player_data_22_23_file = "players_raw_22_23.csv"
    current_dir = dirname(__file__)
    player_data_file_path = join(current_dir, "csv_files", player_data_22_23_file)
    
    return player_data_file_path

def get_player_weekly_score_csv_path():
    player_weekly_score_file = "player_weekly_score.csv"
    current_dir = dirname(__file__)
    player_weekly_score_path = join(current_dir, player_weekly_score_file)
    
    return player_weekly_score_path