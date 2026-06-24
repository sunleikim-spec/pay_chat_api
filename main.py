from fastapi import FastAPI
from api.demo import router as demo_router

app = FastAPI()
app.include_router(demo_router)

@app.get("/")
async def root():
    return {"msg": "首页"}