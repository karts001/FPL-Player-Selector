from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd

from src.weekly_calculation.current_team import rank_current_squad

some_stuff = rank_current_squad()

print(some_stuff)

df = pd.DataFrame(some_stuff)
df[["Index", "_1", "rank", "chance_of_playing_this_round", "element_type", "now_cost"]] = df["row_data"].apply(pd.Series)

app = Dash(__name__,
           requests_pathname_prefix="/suggested_transfers/")

app.layout = html.Div([dash_table.DataTable(
    id="data-table",
    data=df.to_dict("records"),
    columns=[
        {"name": "Player In", "id": "Index"},
        {"name": "FPL Weekly Score", "id": "_1"},
        {"name": "Player Out", "id": "player_out"},
        {"name": "Score Delta", "id": "score_delta"},
        {"name": "Rank", "id": "rank"},
        {"name": "Cost (£m)", "id": "now_cost"},
    ],
    style_header={'textAlign': 'center'},
    sort_action="native",
    sort_mode="multi"
)])

if __name__ == "__main__":
    app.run(debug=True)
