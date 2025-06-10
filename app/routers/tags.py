import re

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/")
async def random_text(request: Request):
    data = await request.json()
    text = data.get("text", "")
    words = re.findall(r"\b\w+\b", text)
    unique = []
    for w in words:
        lw = w.lower()
        if lw not in unique and len(lw) > 2:
            unique.append(lw)
        if len(unique) >= 10:
            break
    return JSONResponse({"tags": unique})
