from dash import Dash, html, dash_table, Output, Input
import dash_bootstrap_components as dbc

from src.weekly_calculation import current_team, player_weekly_score
from src.common.team_conversion import position_mapper
from src.css.styling import conditional_style, my_team_columns, external_stylesheets
from src.config.route_names import fpl_player_score_plot, best_xi, suggested_transfers, my_squad


df = current_team.get_current_team()

def create_buttons(btn1, btn2, btn3):
    button_html = html.Div(
            [
                dbc.Button("Suggested Transfers", color="primary", size="lg",
                           className="suggested-transfers", href=f"../{btn1}/", external_link=True,
                           style={"margin-top": "5px",
                                  "margin-left": "5px"}),
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

buttons = create_buttons(suggested_transfers, fpl_player_score_plot, best_xi)
app = Dash(__name__,
           requests_pathname_prefix=f"/{my_squad}/",
           external_stylesheets=external_stylesheets)
app.title = "My Squad"
app.layout = html.Div(
    [
        buttons,        
        html.Br(),
        html.H1(children="My Team Dash", style={'textAlign':'center'}),
        html.Br(),
        html.Div([
            dash_table.DataTable(
                id="data-table",
                columns=my_team_columns,
                data=df.to_dict("records"),
                style_data_conditional=conditional_style,
                style_header={'textAlign': 'center', "backgroundColor": "black", "color": "white"},
                sort_action="native",
                sort_mode="multi"
            )
        ])
    ])
    

if __name__ == "__main__":
    app.run(debug=True)