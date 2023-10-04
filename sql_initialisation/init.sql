CREATE TABLE "suggested-combined-transfers" (
    index serial PRIMARY KEY,
    player_in varchar(255) UNIQUE,
    player_out varchar(255) UNIQUE,
    chance_of_playing_this_round int,
    cost float,
    team int,
    rank int UNIQUE,
    score_delta float,
    fpl_weekly_score float,
    gameweek int
)