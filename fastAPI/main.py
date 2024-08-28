import uvicorn
from fastapi import FastAPI
from routers import search

app = FastAPI()

app.include_router(search.router, prefix="/search", tags=["search"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=3)

