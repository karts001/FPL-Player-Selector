import plotly.express as px
from ..file_paths import get_player_weekly_score_csv_path
import common.pandas_methods as pdm

file_path = get_player_weekly_score_csv_path()
df_player_score = pdm.convert_data_to_dataframe(file_path)

scatter_graph = px.scatter(data_frame=df_player_score, x="Full Name", y="FPL Weekly Score")

scatter_graph.show()
