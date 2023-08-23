from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn

from src.weekly_calculation.current_team import rank_current_squad
from src.dashboards.graph_1 import app as graph_1

app = FastAPI()
app.mount("/graph_1", WSGIMiddleware(graph_1.server))

# @app.get("/")
# def root():
#     potential_transfers = rank_current_squad()
#     return potential_transfers
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)