from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from db.repository import update_item_by_id, get_item_by_id
from services.openai_client import OpenAiCompatibleChatClient

router = APIRouter()
chat_client = OpenAiCompatibleChatClient()


@router.post("/")
async def process_input(request: Request):
    data = await request.json()
    text = data.get("text", "")

    processed = chat_client.format_markdown(user_prompt=text)

    return JSONResponse({"processed": processed})


@router.post("/save")
async def save_processed(request: Request):
    data = await request.json()

    idx = data.get("index", -1)
    text = data.get("text", "")

    processed = chat_client.format_markdown(user_prompt=text)
    if idx != -1:
        update_item_by_id(doc_id=idx, raw=text, processed=processed)

    return JSONResponse({"processed": processed})


@router.get("/")
async def get_processed(index: int):
    if 0 <= index:
        var = get_item_by_id(doc_id=index)
        return JSONResponse({"processed": var.get("processed")})
    return JSONResponse({"processed": ""})
