from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from . import process

router = APIRouter()

history_list = []


@router.get("/")
async def get_history():
    return JSONResponse({"history": history_list})


@router.post("/save")
async def save_entry(request: Request):
    data = await request.json()
    idx = data.get("index", -1)
    text = data.get("text", "").strip()
    if not text:
        return JSONResponse({"history": history_list, "index": idx})
    if 0 <= idx < len(history_list):
        history_list[idx] = text
        process.processed_list[idx] = ""
        new_idx = idx
    else:
        history_list.append(text)
        process.processed_list.append("")
        new_idx = len(history_list) - 1
    return JSONResponse({"history": history_list, "index": new_idx})


@router.post("/delete")
async def delete_entry(request: Request):
    data = await request.json()
    idx = data.get("index", -1)
    if 0 <= idx < len(history_list):
        history_list.pop(idx)
        process.processed_list.pop(idx)
    return JSONResponse({"history": history_list})
