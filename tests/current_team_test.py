from unittest.mock import patch

from src.weekly_calculation.current_team import combined_transfers
from src.sql_app.database import engine

def test_if_gameweek_is_equal_to_current_gameweek_data_is_taken_from_database():
    with patch("src.common.fpl_get_endpoint.get_current_gameweek") as mock_gameweek:
        mock_gameweek.return_value = 1
    with patch("src.weekly_calculation.current_team._get_gameweek_from_database") as mock_gameweek_in_db:
        mock_gameweek_in_db.return_value = 1
        with patch("src.weekly_calculation.current_team.read_sql") as mock_read_from_db:
            combined_transfers()
            mock_read_from_db.assert_called_once_with("suggested-combined-transfers", engine)