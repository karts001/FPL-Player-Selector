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
    df_filtered = df.filter(["total_points", "points_per_game", "now_cost", "starts_per_90", "element_type", "team", "form"], axis=1)
    
    return df_filtered