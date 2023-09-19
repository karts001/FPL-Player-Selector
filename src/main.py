from fastapi import FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn
from fastapi.templating import Jinja2Templates

from dashboards.fpl_player_score_plot import app as player_score_graph_mware
from src.dashboards.my_team_dash import app as my_squad_mware
from src.dashboards.suggested_transfers import app as suggested_transfers_mware
from src.dashboards.best_team_from_squad import app as best_xi_mware
from src.sql_app.database import engine
from src.sql_app import models
from src.config.route_names import fpl_player_score_plot, best_xi, suggested_transfers, my_squad

app = FastAPI()
app.mount(f"/{fpl_player_score_plot}", WSGIMiddleware(player_score_graph_mware.server))
app.mount(f"/{my_squad}", WSGIMiddleware(my_squad_mware.server))
app.mount(f"/{suggested_transfers}", WSGIMiddleware(suggested_transfers_mware.server))
app.mount(f"/{best_xi}", WSGIMiddleware(best_xi_mware.server))

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="src/templates")

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("general_pages/index.html", {"request": request,
                                                                   "best_xi": best_xi,
                                                                   "suggested_transfers": suggested_transfers,
                                                                   "my_squad": my_squad,
                                                                   "player_score_plot": fpl_player_score_plot})
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    

#TODO: Create separate branch for adding proper landing page and navigation bar
#TODO: Create separate branch for calculating team score for each suggested transfer
#TODO: Make functions private by adding "_" prefix

