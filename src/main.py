from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn

from src.dashboards.graph_1 import app as graph_1
from src.dashboards.my_team_dash import app as my_team
from src.dashboards.suggested_transfers import app as suggested_transfers
from src.dashboards.best_team_from_squad import app as best_team

app = FastAPI()
app.mount("/graph_1", WSGIMiddleware(graph_1.server))
app.mount("/my_team", WSGIMiddleware(my_team.server))
app.mount("/suggested_transfers", WSGIMiddleware(suggested_transfers.server))
app.mount("/best_team", WSGIMiddleware(best_team.server))

@app.get("/")
def root():
    return "Welcome to my FPL Team Selector app"
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)