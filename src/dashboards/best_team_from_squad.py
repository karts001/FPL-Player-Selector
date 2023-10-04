import pandas as pd
from dash import Dash, html, dash_table
import dash_bootstrap_components as dbc

from src.weekly_calculation.current_team import _select_best_team_from_current_squad
from src.common.team_conversion import position_mapper, int_to_string_map
from src.css.styling import best_eleven_columns, conditional_style, external_stylesheets
from src.config.route_names import fpl_player_score_plot, best_xi, suggested_transfers, my_squad

squad_data = _select_best_team_from_current_squad()

df = pd.DataFrame(squad_data.fpl_team.team)
df["element_type"] = df["element_type"].map(position_mapper)
df["team"] = df["team"].map(int_to_string_map)

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
                dbc.Button("Suggested Transfers", color="primary", size="lg",
                           className="suggested-transfers", style={"margin-left": "5px",
                                                       "margin-right": "5px",
                                                       "margin-top": "5px"}, href=f"../{btn3}",
                           external_link=True),
                
            ],
            className="d-grid gap-2 d-md-flex justify-content-md-end",
        )
    
    return button_html

buttons = create_buttons(my_squad, fpl_player_score_plot, suggested_transfers)
app = Dash(__name__,
           requests_pathname_prefix=f"/{best_xi}/",
           external_stylesheets=external_stylesheets)
app.title = "Best Team"

app.layout = html.Div(
    [
        buttons,    
        html.Br(),
        html.H1(children="Best XI", style={"textAlign": "center", "font": "Verdana"}),
        html.Br(),
        dash_table.DataTable(
            id="data-table",
            data=df.to_dict("records"),
            columns=best_eleven_columns,
            style_header={"textAlign" : "center", "backgroundColor": "black", "color": "white"},
            style_cell={"textAlign" : "left"},
            style_data_conditional=conditional_style,
            sort_action="native",
            sort_mode="multi"
        )
    ]
)


if __name__ == "__main__":
    app.run(debug=True)