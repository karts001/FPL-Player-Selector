from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px

from src.file_paths import get_player_weekly_score_csv_path
import src.common.pandas_methods as pdm

file_path = get_player_weekly_score_csv_path()
df = pdm.convert_data_to_dataframe(file_path)



app = Dash(__name__,
           requests_pathname_prefix="/graph_1/")

app.layout = html.Div([
    html.H1(children="Player FPL Score", style={'textAlign':'center'}),
    dcc.Dropdown(
        options=[
            {"label": "Goalkeeper", "value": 1},
            {"label": "Defender", "value": 2},
            {"label": "Midfielder", "value": 3},
            {"label": "Attacker", "value": 4}],
            value=4,
            id="dropdown-selection"),
    dcc.Graph(id="graph-content"),
])

@app.callback(
    Output("graph-content", "figure"),
    Input("dropdown-selection", "value")
)
def create_graph(value):
    dff = df[df.element_type==value]
    scatter_graph = px.scatter(dff, y="X-Rating", x="FPL Weekly Score", color="element_type", hover_name="Full Name")
    return scatter_graph

    
if __name__ == "__main__":
    app.run(debug=True)