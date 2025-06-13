from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from db.repository import add_item, update_item_by_id, remove_item_by_id, get_items

router = APIRouter()


@router.get("/")
async def get_history():
    items = get_items()
    raw_list = [{str(k): v['raw']} for k, v in items.items()]
    return JSONResponse({"history": raw_list})


@router.post("/save")
async def save_entry(request: Request):
    data = await request.json()
    idx = data.get("index", -1)
    text = data.get("text", "").strip()

    if not text:
        items = get_items()
        raw_list = [{str(k): v['raw']} for k, v in items.items()]
        return JSONResponse({"history": raw_list, "index": idx})
    if idx is not None and 0 <= int(idx):
        index = update_item_by_id(doc_id=int(idx), raw=text)
    else:
        index = add_item(raw=text, processed="")
    items = get_items()
    raw_list = [{str(k): v['raw']} for k, v in items.items()]
    return JSONResponse({"history": raw_list, "index": index})


@router.post("/delete")
async def delete_entry(request: Request):
    data = await request.json()
    idx = data.get("index", -1)

    remove_item_by_id(doc_id=int(idx))
    items = get_items()
    raw_list = [{str(k): v['raw']} for k, v in items.items()]

    return JSONResponse({"history": raw_list})
