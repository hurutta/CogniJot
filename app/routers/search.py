from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/")
async def search_endpoint(request: Request):
    dummy = [
        {
            "title": "FastAPI v0.95 Released",
            "description": "FastAPI 0.95 brings performance improvements and new features.",
            "logo": "https://via.placeholder.com/40",
            "link": "https://fastapi.tiangolo.com/"
        },
        {
            "title": "Gradio 4.0 Launched",
            "description": "Gradio 4.0 introduces a revamped UI and faster load times.",
            "logo": "https://via.placeholder.com/40",
            "link": "https://gradio.app/"
        }
    ]
    return JSONResponse({"results": dummy})
