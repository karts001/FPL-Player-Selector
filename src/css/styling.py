"""Contains CSS styling for the Best XI dashboard"""

conditional_style = [
    {
        "if" : {
            "filter_query": "{element_type} = 'Attacker'",
        },
        "backgroundColor": "#008744",
        "color": "black"
    },
    {
        "if": {
            "filter_query": "{element_type} = 'Midfielder'",
        },
        "backgroundColor": "#0057e7",
        "color": "black"
    },
    {
        "if": {
            "filter_query": "{element_type} = 'Defender'",
        },
        "backgroundColor": "#d62d20",
        "color": "black"
    },
    {
        "if": {
            "filter_query": "{element_type} = 'Goalkeeper'",
        },
        "backgroundColor": "#ffa700",
        "color": "black"
    }
]

best_eleven_columns = [
    {"name": "Player Name", "id": "name"},
    {"name": "Position", "id": "element_type"},
    {"name": "Team", "id": "team"},            
    {"name": "Cost (£m)", "id": "cost"},
    {"name": "FPL Weekly Score", "id": "score"}
]

suggested_transfers_columns = [
    {"name": "Player In", "id": "player_in"},
    {"name": "Player Out", "id": "player_out"},
    {"name": "Cost (£m)", "id": "cost"},
    {"name": "Team", "id": "team"},
    {"name": "Score Delta", "id": "score_delta"},
    {"name": "FPL Weekly Score", "id": "fpl_weekly_score"},
    {"name": "Position", "id": "element_type"}
]

my_team_columns = [
    {"name": "Full Name", "id": "Full Name", "type": "text"},
    {"name": "player id", "id": "id", "type": "numeric"},
    {"name": "ict Index", "id":"ict_index", "type": "numeric"},
    {"name":"Chance of Playing This Round", "id":"chance_of_playing_this_round", "type": "numeric"},
    {"name": "Cost (£m)", "id": "now_cost", "type": "numeric"},
    {"name": "Position", "id":"element_type", "type": "numeric"},
    {"name": "FPL Weekly Score"   , "id": "fpl_weekly_score", "type": "numeric"}
]


external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]