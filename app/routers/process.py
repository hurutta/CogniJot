from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

processed_list = []


@router.post("/")
async def process_input(request: Request):
    data = await request.json()

    idx = data.get("index", -1)
    text = data.get("text", "")
    print(idx)

    processed = text.upper()

    if 0 <= idx < len(processed_list):
        processed_list[idx] = processed

    return JSONResponse({"processed": processed})


@router.get("/")
async def get_processed(index: int):
    if 0 <= index < len(processed_list):
        return JSONResponse({"processed": processed_list[index]})
    return JSONResponse({"processed": ""})
