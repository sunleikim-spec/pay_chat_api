from fastapi import FastAPI
from database import engine
import models
from api.users import router as users_router
from api.experts import router as experts_router
from api.sessions import router as sessions_router
from api.wallet import router as wallet_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PayChatAPI", version="2.0")

app.include_router(users_router)
app.include_router(experts_router)
app.include_router(sessions_router)
app.include_router(wallet_router)


@app.get("/")
def root():
    return {"message": "PayChatAPI running", "version": "2.0"}
