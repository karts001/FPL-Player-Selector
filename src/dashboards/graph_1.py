from dash import Dash, html, dcc, Output, Input
import plotly.express as px

from src.file_paths import get_player_weekly_score_csv_path
import src.common.pandas_methods as pdm
from src.css.styling import external_stylesheets

file_path = get_player_weekly_score_csv_path()
df = pdm.convert_data_to_dataframe(file_path)

#TODO: Rename endpoint to something more specific / suitable
#TODO: Add a navigation bar at the top to change between the three endpoints

app = Dash(__name__,
           requests_pathname_prefix="/graph_1/",
           external_stylesheets=external_stylesheets)
app.title = "FPL Player Score"

app.layout = html.Div(
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
            {"label": "Attacker", "value": 4}],
        value=4,
        id="dropdown-selection")],
    style={"width": "25%",
           "align-items": "center",
           "margin": "0 auto",
           }),
    html.Div([
       dcc.Graph(id="graph-content")]),
    ])
    
@app.callback(
    Output("graph-content", "figure"),
    Input("dropdown-selection", "value")
)
def create_graph(value):
    dff = df[df.element_type==value]
    scatter_graph = px.scatter(dff, y="X-Rating", x="fpl_weekly_score", hover_name="Full Name")    
    return scatter_graph

if __name__ == "__main__":
    app.run(debug=True)
    