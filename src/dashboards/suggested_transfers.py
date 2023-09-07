from dash import Dash, html, dash_table, callback, Input, Output, dcc, ctx
import pandas as pd

from src.weekly_calculation.current_team import combined_transfers, transfer_list
from src.css.styling import conditional_style, suggested_transfers_columns, external_stylesheets
from src.common.team_conversion import int_to_string_map, position_mapper
from src.weekly_calculation.player_weekly_score import calculate_player_score

gameweek_transfers = combined_transfers()

df = pd.DataFrame(gameweek_transfers)
df["team"] = df["team"].map(int_to_string_map)
df["element_type"] = df["element_type"].map(position_mapper)

app = Dash(__name__,
           requests_pathname_prefix="/suggested_transfers/",
           external_stylesheets=external_stylesheets)
app.title = "Suggested Transfers"

app.layout = html.Div([
    html.Br(),
    html.H1(
        children="Suggested Transfers Dash",
        style={'textAlign': 'center'}),
    html.Br(),
    html.Div(children=[
        html.Div([
            dcc.Dropdown(
                options=[
                    {"label": "Goalkeepers", "value": 1},
                    {"label": "Defenders", "value": 2},
                    {"label": "Midfielders", "value": 3},
                    {"label": "Attackers", "value": 4},
                    {"label": "Combined", "value": 5}
                ],
                value=5,
                id="dropdown-selection",
                style={"width": "50%",
                       "margin": "0 auto",
                       "textAlign": "center"}
            ),
            html.Button(
                "Update",
                id="update-scores",
                style={"float": "right"}
            ),
        ],
        style={"display": "flex", "justify-content": "space-between", "align-items": "center"}),
        
        dash_table.DataTable(
            id="data-table",
            data=df.to_dict("records"),
            columns=suggested_transfers_columns,
            hidden_columns=["element_type"],
            style_header={'textAlign': 'center', "backgroundColor": "black", "color": "white"},
            style_data_conditional=conditional_style,
            sort_action="native",
            sort_mode="multi",
        ),
    ]),
])

@callback(
    Output("data-table", "data"),
    Input("update-scores", "n_clicks"),
    Input("dropdown-selection", "value")
)
def update_table(n_clicks, value):
    triggered_id = ctx.triggered_id
    print(triggered_id)
    # if triggered_id == "update-scores":
    #     return update_weekly_score_calculation(n_clicks)
    if triggered_id == "dropdown-selection":
        return load_table(value)
    

def update_weekly_score_calculation(n_clicks):   
    if n_clicks == None:
        df = get_suggested_gameweek_transfers()
        return df.to_dict("records")
    
    if n_clicks > 0:
        print("is the button working")
        calculate_player_score()
        df = get_suggested_gameweek_transfers()
        return df.to_dict("records")
    
def get_suggested_gameweek_transfers():
    new_potential_transfers = combined_transfers()
    df = pd.DataFrame(new_potential_transfers)
    df["team"] = df["team"].map(int_to_string_map)
    df["element_type"] = df["element_type"].map(position_mapper)
    
    return df

def load_table(value):
    if value == 5:
        gameweek_transfers = combined_transfers()
        df = pd.DataFrame(gameweek_transfers)
        df["team"] = df["team"].map(int_to_string_map)
        df["element_type"] = df["element_type"].map(position_mapper)
    else:
        player_list = transfer_list(value)
        df = pd.DataFrame(player_list) 
        df["team"] = df["team"].map(int_to_string_map)
        df["element_type"] = df["element_type"].map(position_mapper)
    
    return df.to_dict("records")

            
if __name__ == "__main__":
    app.run(debug=True)
