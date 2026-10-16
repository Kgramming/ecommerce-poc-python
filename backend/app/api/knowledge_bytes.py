"""Knowledge Bytes API — serves the repo's knowledge-bytes/*.md as JSON.

GET /api/knowledge-bytes       -> {"bytes": [{"id": "01_Three_Databases", "title": "..."}], "total": 8}
GET /api/knowledge-bytes/{id} -> {"id": "...", "title": "...", "markdown": "..."} | 404
"""
import os
import re
from fastapi import APIRouter, HTTPException

router = APIRouter()

_BYTE_RE = re.compile(r"^\d{2}_.*\.md$")
_SLUG_RE = re.compile(r"^[A-Za-z0-9_]+$")
_TITLE_RE = re.compile(r"^#\s+\d+\s+[—–-]\s+(.+)$", re.M)


def _resolve_dir() -> str | None:
    if os.environ.get("KNOWLEDGE_BYTES_DIR"):
        return os.environ["KNOWLEDGE_BYTES_DIR"]
    cwd = os.getcwd()
    for cand in (
        os.path.join(cwd, "knowledge-bytes"),
        os.path.join(cwd, "..", "knowledge-bytes"),
        os.path.join(cwd, "..", "..", "knowledge-bytes"),
    ):
        if os.path.isdir(cand):
            return os.path.normpath(cand)
    return None


def _parse(path: str) -> tuple[str, str]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = _TITLE_RE.search(text)
    title = m.group(1).strip() if m else os.path.basename(path)[: -len(".md")]
    return title, text


def _list() -> list[dict]:
    d = _resolve_dir()
    if not d:
        return []
    items = []
    for fn in sorted(os.listdir(d)):
        if _BYTE_RE.match(fn):
            slug = fn[: -len(".md")]
            title, _ = _parse(os.path.join(d, fn))
            items.append({"id": slug, "title": title})
    return items


@router.get("/knowledge-bytes")
def list_bytes():
    items = _list()
    return {"bytes": items, "total": len(items)}


@router.get("/knowledge-bytes/{slug}")
def get_byte(slug: str):
    if not _SLUG_RE.match(slug):
        raise HTTPException(404, "knowledge byte not found")
    d = _resolve_dir()
    path = os.path.join(d, slug + ".md") if d else None
    if not path or not os.path.isfile(path) or not _BYTE_RE.match(slug + ".md"):
        raise HTTPException(404, "knowledge byte not found")
    title, text = _parse(path)
    return {"id": slug, "title": title, "markdown": text}
