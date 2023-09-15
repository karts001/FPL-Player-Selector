from dash import Dash, html, dash_table

from src.weekly_calculation import current_team
from src.common.team_conversion import position_mapper
from src.css.styling import conditional_style, my_team_columns, external_stylesheets

list_of_player_ids = current_team._create_a_list_of_squad_ids()
req_data = current_team._trim_df_columns()
squad_data = current_team._get_squad_player_data(list_of_player_ids)
df = current_team._convert_squad_data_list_into_df(squad_data, req_data)
df["Full Name"] = df.index
df["element_type"] = df["element_type"].map(position_mapper)

app = Dash(__name__,
           requests_pathname_prefix="/my_team/",
           external_stylesheets=external_stylesheets)
app.title = "My Team"
app.layout = html.Div([
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