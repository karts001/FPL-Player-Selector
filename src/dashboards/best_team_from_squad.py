import pandas as pd
from dash import Dash, html, dash_table

from src.weekly_calculation.current_team import select_best_team_from_current_squad
from src.common.team_conversion import position_mapper, int_to_string_map
from src.css.styling import best_eleven_columns, conditional_style, external_stylesheets

squad_data = select_best_team_from_current_squad()

df = pd.DataFrame(squad_data.fpl_team.team)
df["element_type"] = df["element_type"].map(position_mapper)
df["team"] = df["team"].map(int_to_string_map)

app = Dash(__name__,
           requests_pathname_prefix="/best_team/",
           external_stylesheets=external_stylesheets)
app.title = "Best Team"

app.layout = html.Div([
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
])

if __name__ == "__main__":
    app.run(debug=True)