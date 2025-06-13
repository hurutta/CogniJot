from urllib.parse import urlparse

from duckduckgo_search import DDGS
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from services.openai_client import OpenAiCompatibleChatClient

router = APIRouter()
chat_client = OpenAiCompatibleChatClient()


@router.post("/")
async def search_endpoint(request: Request):
    data = await request.json()
    text = data.get("query", "")

    search_query = chat_client.find_gist(user_prompt=text)

    hits = ddg_search_actual(search_query, max_results=10)

    return JSONResponse({"results": hits, "title": "chicken man"})


def ddg_search_actual(query: str, max_results: int = 10):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, safesearch="Off"):
            href = r.get("href") or r.get("link")
            if not href:
                continue
            domain = urlparse(href).netloc
            results.append({
                "title": r.get("title", ""),
                "link": href,
                "description": r.get("body", ""),
                "logo": f"https://icons.duckduckgo.com/ip3/{domain}.ico"
            })
            if len(results) >= max_results:
                break
    return results
