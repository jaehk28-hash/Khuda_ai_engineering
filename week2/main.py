from fastapi import FastAPI

from week2.database import Base, engine
from week2.router import auth_router, game_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wordle API")

app.include_router(auth_router)
app.include_router(game_router)


@app.get("/")
def root():
    return {"message": "Wordle API"}
