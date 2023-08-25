from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px

from src.weekly_calculation import current_team

list_of_player_ids = current_team.create_a_list_of_squad_ids()
req_data = current_team.trim_df_columns()
squad_data = current_team.get_squad_player_data(list_of_player_ids)
df = current_team.convert_squad_data_list_into_df(squad_data, req_data)
df["Full Name"] = df.index

app = Dash(__name__,
           requests_pathname_prefix="/my_team/")

app.layout = html.Div([dash_table.DataTable(
    id="data-table",
    columns=[
        {"name": "Full Name", "id": "Full Name", "type": "text"},
        {"name": "player id", "id": "id", "type": "numeric"},
        {"name": "ict Index", "id":"ict_index", "type": "numeric"},
        {"name":"Chance of Playing This Round", "id":"chance_of_playing_this_round", "type": "numeric"},
        {"name": "Cost (£m)", "id": "now_cost", "type": "numeric"},
        {"name": "Position", "id":"element_type", "type": "numeric"},
        {"name": "FPL Weekly Score", "id": "FPL Weekly Score", "type": "numeric"}],
    data=df.to_dict("records"),
    style_header={'textAlign': 'center'},
    sort_action="native",
    sort_mode="multi"
    )])

if __name__ == "__main__":
    app.run(debug=True)