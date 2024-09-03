import uvicorn
from fastapi import FastAPI
from routers import search, tools

app = FastAPI()

app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(tools.router, prefix="/tools", tags=["tools"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=3)

