import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routers import history, process, tags, search, check

app = FastAPI()

static_path = os.path.join(os.path.dirname(__file__), "assets")
app.mount("/assets", StaticFiles(directory=static_path), name="assets")

# include each router under its prefix
app.include_router(history.router, prefix="/history")
app.include_router(process.router, prefix="/process")
app.include_router(tags.router, prefix="/tags")
app.include_router(search.router, prefix="/search")
app.include_router(check.router, prefix="/check")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
