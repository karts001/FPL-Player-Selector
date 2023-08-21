from fastapi import FastAPI
from current_team import *
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}
    