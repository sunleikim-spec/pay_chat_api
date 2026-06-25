from fastapi import FastAPI
from database import engine, Base
from api.users import router as users_router
from api.experts import router as experts_router
from api.sessions import router as sessions_router
from api.wallet import router as wallet_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PayChatAPI", version="2.0")

app.include_router(users_router)
app.include_router(experts_router)
app.include_router(sessions_router)
app.include_router(wallet_router)


@app.get("/")
def root():
    return {"message": "PayChatAPI running", "version": "2.0"}
