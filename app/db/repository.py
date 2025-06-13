from tinydb import TinyDB

db = TinyDB("db.json", indent=4)
items_tbl = db.table("items")


def add_item(raw: str, processed: str) -> int:
    """
    Insert a new record with both raw and processed strings.
    Returns the auto-generated numeric id (doc_id).
    """
    return items_tbl.insert({"raw": raw, "processed": processed})


def get_items() -> dict[int, dict[str, str]]:
    """
    Return a mapping of doc_id → {"raw": ..., "processed": ...}
    """
    return {
        doc.doc_id: {"raw": doc["raw"], "processed": doc["processed"]}
        for doc in items_tbl.all()
    }


def get_item_by_id(doc_id: int) -> dict[str, str] | None:
    """
    Retrieve one record by its numeric id.
    Returns {"raw": ..., "processed": ...} or None if not found.
    """
    doc = items_tbl.get(doc_id=doc_id)
    if doc is None:
        return None
    return {"raw": doc["raw"], "processed": doc["processed"]}


def update_item_by_id(doc_id: int, raw: str | None = None, processed: str | None = None) -> int | None:
    """
    Update the record with the given doc_id.
    Only fields provided (raw and/or processed) will be updated.
    Returns the doc_id if the update was applied, otherwise None.
    """
    update_data: dict[str, str] = {}
    if raw is not None:
        update_data["raw"] = raw
    if processed is not None:
        update_data["processed"] = processed

    if not update_data:
        return None

    # TinyDB.update returns a list of updated doc_ids
    updated_ids = items_tbl.update(update_data, doc_ids=[doc_id])
    return doc_id if updated_ids else None


def remove_item_by_id(doc_id: int) -> bool:
    """
    Remove the record by its numeric id. Returns True if removed.
    """
    return bool(items_tbl.remove(doc_ids=[doc_id]))
