from dash import Dash, html, dash_table, Input, Output, dcc, ctx
import dash_bootstrap_components as dbc

from src.weekly_calculation.current_team import combined_transfers, transfer_list
from src.css.styling import conditional_style, suggested_transfers_columns, external_stylesheets
from src.weekly_calculation.player_weekly_score import calculate_player_score
from src.config.route_names import fpl_player_score_plot, best_xi, suggested_transfers, my_squad


df = combined_transfers()
def create_buttons(btn1, btn2, btn3):
    button_html = html.Div(
            [
                dbc.Button("My Squad", color="primary", size="lg",
                           className="my-squad", href=f"../{btn1}/", external_link=True,
                           style={"margin-top": "5px"}),
                dbc.Button("FPL Player Score Plot", color="primary", size="lg",
                           className="fpl-player-score-plot", style={"margin-left": "5px",
                                                                   "margin-top": "5px"},
                           href=f"../{btn2}", external_link=True),
                dbc.Button("Best XI", color="primary", size="lg",
                           className="best-xi", style={"margin-left": "5px",
                                                       "margin-right": "5px",
                                                       "margin-top": "5px"}, href=f"../{btn3}",
                           external_link=True),
                
            ],
            className="d-grid gap-2 d-md-flex justify-content-md-end",
        )
    return button_html

buttons = create_buttons(my_squad, fpl_player_score_plot, best_xi)
app = Dash(__name__,
           requests_pathname_prefix=f"/{suggested_transfers}/",
           external_stylesheets=external_stylesheets)
app.title = "Suggested Transfers"

app.layout = html.Div(
    [
        buttons,
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
            style={"display": "flex", "justify-content": "space-between", "align-items": "center"}
        ),
            
            dash_table.DataTable(
                id="data-table",
                data=df.to_dict("records"),
                columns=suggested_transfers_columns,
                hidden_columns=["element_type", "gameweek"],
                style_header={'textAlign': 'center', "backgroundColor": "black", "color": "white"},
                style_data_conditional=conditional_style,
                sort_action="native",
                sort_mode="multi",
            ),
        ]),
    ]
)

@app.callback(
    Output("data-table", "data"),
    Input("update-scores", "n_clicks"),
    Input("dropdown-selection", "value")
)
def update_table(n_clicks, value):
    triggered_id = ctx.triggered_id
    if triggered_id == "update-scores":
        if _check_if_combined_is_selected(value):
            calculate_player_score()
            return _load_table(value, 1)
        else:
            calculate_player_score()
            return _load_table(value, 3)
 
    if triggered_id == "dropdown-selection" and value == 5:
        return _load_table(value, 1)
    else:
        return _load_table(value, 3)
  
def _check_if_combined_is_selected(value):
    if value == 5:
        return True
    else:
        return False

def _load_table(value, players_in_list):
    if value == 5:
        df = combined_transfers()

    else:
        df = transfer_list(value, players_in_list)
    
    return df.to_dict("records")



            
if __name__ == "__main__":
    app.run(debug=True)
