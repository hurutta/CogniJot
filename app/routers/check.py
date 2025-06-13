import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from services.openai_client import OpenAiCompatibleChatClient

router = APIRouter()
chat_client = OpenAiCompatibleChatClient()


@router.post("/")
async def check_errors(request: Request):
    data = await request.json()
    text = data.get("text", "")

    reply = chat_client.ask(user_prompt=text)
    clean_raw = cleanup_markdown(reply)
    errors = string_to_dict(clean_raw)

    errors = [
        {"word": item["error"], "message": item["suggestion"]}
        for item in errors
    ]

    return JSONResponse({"errors": errors})


def cleanup_markdown(raw: str):
    start = raw.find('[')
    end = raw.rfind(']')
    if start == -1 or end == -1 or end < start:
        return ""
    return raw[start:end + 1]


def string_to_dict(raw: str):
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None
