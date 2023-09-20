from unittest.mock import patch
from contextvars import copy_context
from dash._callback_context import context_value
from dash._utils import AttributeDict

from src.dashboards.fpl_player_score_plot import create_graph
from src.dashboards.suggested_transfers import update_table

def test_create_graph_callback_creates_a_graph():
    output = create_graph(1)
    x_axis_data_array_size = output["data"][0]["x"].size
    assert x_axis_data_array_size != 0
    
def test_create_graph_callback_creates_an_empty_graph():
    output = create_graph(10)
    x_axis_data_array_size = output["data"][0]["x"].size
    assert x_axis_data_array_size == 0
 
def test_update_table_callback_loads_combined_transfers_if_dropdown_value_5_selected():
    def run_callback():
        context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "dropwdown-selection"}]}))
        return update_table(0, 5)
    ctx = copy_context()
    output = ctx.run(run_callback)

    assert output[0]["element_type"] == "Goalkeeper"
    assert output[-1]["element_type"] == "Attacker"
    
def test_update_table_callback_loads_attacker_transfers_if_dropdown_value_4_selected():
    def run_callback():
        context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "dropwdown-selection"}]}))
        return update_table(0, 4)
    ctx = copy_context()
    output = ctx.run(run_callback)

    assert output[0]["element_type"] == "Attacker"
    assert output[-1]["element_type"] == "Attacker"
    
def test_update_table_callback_loads_midfielder_transfers_if_dropdown_value_3_selected():
    def run_callback():
        context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "dropwdown-selection"}]}))
        return update_table(0, 3)
    ctx = copy_context()
    output = ctx.run(run_callback)

    assert output[0]["element_type"] == "Midfielder"
    assert output[-1]["element_type"] == "Midfielder"
    
def test_update_table_callback_loads_midfielde_transfers_if_dropdown_value_3_selected():
    def run_callback():
        context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "dropwdown-selection"}]}))
        return update_table(0, 2)
    ctx = copy_context()
    output = ctx.run(run_callback)

    assert output[0]["element_type"] == "Defender"
    assert output[-1]["element_type"] == "Defender"
    
def test_update_table_callback_loads_goalkeeper_transfers_if_dropdown_value_3_selected():
    def run_callback():
        context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "dropwdown-selection"}]}))
        return update_table(0, 1)
    ctx = copy_context()
    output = ctx.run(run_callback)

    assert output[0]["element_type"] == "Goalkeeper"
    assert output[-1]["element_type"] == "Goalkeeper"
    
def test_update_table_callback_recalculates_player_score_when_update_button_is_clicked():
    def run_callback():
        context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "update-scores"}]}))
        return update_table(1, 1)
    ctx = copy_context()

    with patch("src.dashboards.suggested_transfers._load_table") as mock_load_table:
        output = ctx.run(run_callback)
        mock_load_table.assert_called_once_with(1, 3)
    
    