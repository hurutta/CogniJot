from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()
ERROR_WORDS = ["abc", "def"]


@router.post("/")
async def check_errors(request: Request):
    data = await request.json()
    text = data.get("text", "").lower()
    errors = []
    for w in ERROR_WORDS:
        if w in text:
            errors.append({"word": w, "message": f"'{w}' is an error"})
    return JSONResponse({"errors": errors})
