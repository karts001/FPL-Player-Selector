from unittest.mock import patch
from src.common import fpl_get_endpoint
from datetime import datetime


def test_get_manager_response_returns_correct_data():
    response = fpl_get_endpoint.get_manager_response()
    assert response["player_first_name"] == "Shiva"
    assert response["player_last_name"] == "Karthikeyan"
    assert response["name"] == "Top Of The Klopps"

def test_sort_base_response_by_id_orders_players_by_id():
    response = fpl_get_endpoint.sort_base_response_by_id()
    index_0 = 0
    index_1 = 1
    assert response[0]["id"] == index_0 + 1
    assert response[1]["id"] == index_1 + 1
    
def test_my_team_endpoint_returns_200_status_code():
    response = fpl_get_endpoint._get_my_team()
    assert response != None
   
def test_get_current_gameweek_returns_correct_gameweek(requests_mock):
    fake_response = {
        "events": [
            {
                "id": 1,
                "deadline_time": "2023-08-11T17:30:00Z"
            },
            {
                "id": 2,
                "deadline_time": "2023-08-18T17:15:00Z"
            },
            {
                "id": 3,
                "deadline_time": "2023-08-25T17:30:00Z"
            }
        ]
    }
    requests_mock.get("https://fantasy.premierleague.com/api/bootstrap-static/", json=fake_response)
    with patch(f"{fpl_get_endpoint.__name__}.datetime", wraps=datetime) as mock_date:
        mock_date.now.return_value = datetime(2023, 8, 15, 10, 27, 21, 240752)
        gameweek = fpl_get_endpoint.get_current_gameweek()
        
        assert gameweek == 2
    