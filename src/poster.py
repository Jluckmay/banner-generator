"""Normalização e validação dos dados do pôster (entrada manual, upload ou IA)."""

from __future__ import annotations

import re
from typing import Any, Dict, List

from .config import LANGUAGES, PAPER_SIZES
from .i18n import labels_for
from .templates import DEFAULT_TEMPLATE, TEMPLATES

MAX_SECTIONS = 20
MAX_FIELD = 20_000


def _s(value: Any, limit: int = MAX_FIELD) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        value = "\n".join(str(v) for v in value)
    return str(value).replace("\r\n", "\n").replace("\r", "\n").strip()[:limit]


def _hex(value: Any, default: str) -> str:
    v = _s(value, 16).lstrip("#")
    return v.upper() if re.fullmatch(r"[0-9a-fA-F]{6}", v) else default


def normalize_poster(data: Dict[str, Any]) -> Dict[str, Any]:
    """Retorna um dicionário saneado com todos os campos esperados pelo renderizador."""
    lang = data.get("language") if data.get("language") in LANGUAGES else "pt-BR"
    labels = labels_for(lang)
    template = data.get("template") if data.get("template") in TEMPLATES else DEFAULT_TEMPLATE
    paper = data.get("paper") if data.get("paper") in PAPER_SIZES else "a0"
    orientation = "landscape" if data.get("orientation") == "landscape" else "portrait"
    try:
        columns = int(data.get("columns") or (3 if orientation == "landscape" else 2))
    except (TypeError, ValueError):
        columns = 2
    columns = max(1, min(4, columns))

    sections: List[Dict[str, Any]] = []
    raw_sections = data.get("sections")
    if isinstance(raw_sections, dict):  # formato {id: texto}
        raw_sections = [{"id": k, "content": v} for k, v in raw_sections.items()]
    for i, sec in enumerate((raw_sections or [])[:MAX_SECTIONS]):
        if not isinstance(sec, dict):
            continue
        sid = _s(sec.get("id"), 40) or f"custom{i}"
        title = _s(sec.get("title"), 200) or labels.get(sid, "")
        content = _s(sec.get("content"))
        images = []
        for img in sec.get("images") or []:
            if isinstance(img, dict) and img.get("path"):
                images.append({"path": str(img["path"]), "caption": _s(img.get("caption"), 400)})
        if not (content or images):
            continue
        if not title:
            title = sid.capitalize()
        sections.append({"id": sid, "title": title, "content": content, "images": images})

    return {
        "language": lang,
        "template": template,
        "paper": paper,
        "orientation": orientation,
        "columns": columns,
        "accent": _hex(data.get("accent"), ""),
        "title": _s(data.get("title"), 500),
        "authors": _s(data.get("authors"), 1500),
        "affiliations": _s(data.get("affiliations"), 2000),
        "email": _s(data.get("email"), 200),
        "url": _s(data.get("url"), 300),
        "logos": [str(p) for p in data.get("logos") or []][:4],
        "sections": sections,
    }
