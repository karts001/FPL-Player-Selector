from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd

from src.weekly_calculation.current_team import rank_current_squad

some_stuff = rank_current_squad()

df = pd.DataFrame(some_stuff)
df[["Index", "_1", "rank", "chance_of_playing_this_round", "element_type", "now_cost", "team"]] = df["row_data"].apply(pd.Series)

app = Dash(__name__,
           requests_pathname_prefix="/suggested_transfers/")
app.title = "Suggested Transfers"

app.layout = html.Div([
    html.H1(children="Suggested Transfers Dash", style={'textAlign':'center'}),
    dash_table.DataTable(
    id="data-table",
    data=df.to_dict("records"),
    columns=[
        {"name": "Player In", "id": "Index"},
        {"name": "FPL Weekly Score", "id": "_1"},
        {"name": "Player Out", "id": "player_out"},
        {"name": "Score Delta", "id": "score_delta"},
        {"name": "Rank", "id": "rank"},
        {"name": "Cost (£m)", "id": "now_cost"},
        {"name": "Team Code", "id": "team"}
    ],
    style_header={'textAlign': 'center'},
    sort_action="native",
    sort_mode="multi"
)])

if __name__ == "__main__":
    app.run(debug=True)
