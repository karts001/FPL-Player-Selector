from dash import Dash, html, dcc, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc

from src.file_paths import get_player_weekly_score_csv_path
import src.common.pandas_methods as pdm
from src.css.styling import external_stylesheets
from src.config.route_names import fpl_player_score_plot, best_xi, my_squad, suggested_transfers

file_path = get_player_weekly_score_csv_path()
df = pdm.convert_data_to_dataframe(file_path)

def create_buttons(btn1, btn2, btn3):
    button_html = html.Div(
            [
                dbc.Button("My Squad", color="primary", size="lg",
                           className="my-squad", href=f"../{btn1}/", external_link=True,
                           style={"margin-top": "5px"}),
                dbc.Button("Suggested Transfers", color="primary", size="lg",
                           className="suggested-transfers", style={"margin-left": "5px",
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

buttons = create_buttons(my_squad, suggested_transfers, best_xi)
app = Dash(__name__,
           requests_pathname_prefix=f"/{fpl_player_score_plot}/",
           external_stylesheets=external_stylesheets)
app.title = "FPL Player Score"
app.layout = html.Div(
    [
        buttons,        
        html.Div(
            children=[
            html.Br(),
            html.H1(children="FPL Player Score", style={'textAlign':'center'}),
            html.Br(),
            html.Div([
                dcc.Dropdown(
                    options=[
                        {"label": "Goalkeeper", "value": 1},
                        {"label": "Defender", "value": 2},
                        {"label": "Midfielder", "value": 3},
                        {"label": "Attacker", "value": 4}
                    ],
                    value=4,
                    id="dropdown-selection"
                )
            ],
                style={"width": "25%",
                    "align-items": "center",
                    "margin": "0 auto",
                }
            ),
            html.Div([
                dcc.Graph(id="graph-content")]
            )
            ]
        )
    ]
)
    
@app.callback(
    Output("graph-content", "figure"),
    Input("dropdown-selection", "value")
)
def create_graph(value):
    dff = df[df.element_type==value]
    scatter_graph = px.scatter(dff, y="X-Rating", x="fpl_weekly_score", hover_name="Full Name", size="fpl_weekly_score")    
    return scatter_graph

if __name__ == "__main__":
    app.run(debug=True)
    