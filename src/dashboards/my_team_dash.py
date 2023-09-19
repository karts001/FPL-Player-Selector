from dash import Dash, html, dash_table
import dash_bootstrap_components as dbc

from src.weekly_calculation import current_team
from src.common.team_conversion import position_mapper
from src.css.styling import conditional_style, my_team_columns, external_stylesheets
from src.config.route_names import fpl_player_score_plot, best_xi, suggested_transfers, my_squad

list_of_player_ids = current_team._create_a_list_of_squad_ids()
req_data = current_team._trim_df_columns()
squad_data = current_team._get_squad_player_data(list_of_player_ids)
df = current_team._convert_squad_data_list_into_df(squad_data, req_data)
df["Full Name"] = df.index
df["element_type"] = df["element_type"].map(position_mapper)

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