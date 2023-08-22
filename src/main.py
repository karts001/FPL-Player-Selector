from fastapi import FastAPI
from src.weekly_calculation.current_team import rank_current_squad

app = FastAPI()

@app.get("/")
def root():
    potential_transfers = rank_current_squad()
    return potential_transfers
    