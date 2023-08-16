import pandas as pd

def convert_api_response_to_pandas_dataframe(player_data: list[dict]) -> pd.DataFrame:
    df_fpl = pd.DataFrame.from_dict(player_data)
    
    return df_fpl

def create_full_name_column_and_make_it_the_row_index(df: pd.DataFrame) -> pd.DataFrame:
    """Create a full name column and make it the row headers

    Args:
        df (pd.df_attackers): The pandas df_attackers to update

    Returns:
      df (pd.df_attackers) : Updated pandas df_attackers
    """
    df["Full Name"] = df["first_name"] + " " + df["second_name"]
    df = df.set_index("Full Name")
    
    return df

def filter_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = create_full_name_column_and_make_it_the_row_index(df)
    df_filtered = df.filter(["element_type", "team", "form", "ict_index", "now_cost",
                             "ict_index_rank", "chance_of_playing_next_round", "chance_of_playing_this_round"], axis=1)
    df_filtered["now_cost"] = df_filtered["now_cost"] / 10
    
    return df_filtered

def convert_data_to_dataframe(file_path):
    df = pd.read_csv(file_path)
    
    return df

def get_player_data_from_csv_file(file_path):   
    df = pd.read_csv(file_path)
    df = create_full_name_column_and_make_it_the_row_index(df)
    
    return df

def convert_column_to_float(df, column_name):
    df[column_name] = df[column_name].astype(float)
    
    return df

def convert_column_to_int(df, column_name):
    df[column_name] = df[column_name].astype(int)
    
    return df

def convert_squad_data_into_a_dataframe(list_of_list) -> pd.DataFrame:
    df = pd.DataFrame.from_records(list_of_list)
    stats_columns = df["stats"].apply(pd.Series)
    df.drop(columns=["stats", "explain"], axis=1, inplace=True)
    df = pd.concat([df, stats_columns], axis=1)
    
    return df

def concatenate_dataframes(df1, df2):
    
    df_concat = pd.concat([df1, df2], axis=1)
    
    return df_concat