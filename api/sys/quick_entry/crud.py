from typing import Optional

_DB: dict[int, dict] = {}
_seq = 1


def get_by_id(entry_id: int) -> Optional[dict]:
    return _DB.get(entry_id)


def list_all() -> list[dict]:
    return sorted(_DB.values(), key=lambda x: x["sort"])


def create(data: dict) -> dict:
    global _seq
    entry = {"id": _seq, **data}
    _DB[_seq] = entry
    _seq += 1
    return entry


def update(entry_id: int, data: dict) -> Optional[dict]:
    entry = _DB.get(entry_id)
    if not entry:
        return None
    for k, v in data.items():
        if v is not None:
            entry[k] = v
    return entry


def delete(entry_id: int) -> bool:
    return _DB.pop(entry_id, None) is not None
