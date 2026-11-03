"""Normalização e validação dos dados do pôster (entrada manual, upload ou IA)."""

from __future__ import annotations

import re
from typing import Any, Dict, List

from .config import LANGUAGES
from .i18n import labels_for
from .templates import DEFAULT_TEMPLATE, TEMPLATES, default_paper_for, papers_for

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
    paper = data.get("paper") if data.get("paper") in papers_for(template) else default_paper_for(template)
    orientation = "landscape" if data.get("orientation") == "landscape" else "portrait"
    default_cols = TEMPLATES[template].get("default_columns") or (3 if orientation == "landscape" else 2)
    try:
        columns = int(data.get("columns") or default_cols)
    except (TypeError, ValueError):
        columns = default_cols
    columns = max(1, min(4, columns))
    slots = TEMPLATES[template]["logos"]

    def _logo_list(key: str, limit: int) -> List[str]:
        raw = data.get(key) or []
        return [str(p) for p in raw if p][:limit] if isinstance(raw, list) else []

    # `logos` (legado) equivale ao cabeçalho
    logos_header = _logo_list("logos_header" if "logos_header" in data else "logos", slots["header"])
    logos_footer = _logo_list("logos_footer", slots["footer"])

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

    colors: Dict[str, str] = {}
    if isinstance(data.get("colors"), dict):
        for k in ("accent", "title", "subtitle", "body", "caption", "bg"):
            val = data["colors"].get(k)
            if val:
                colors[k] = _hex(val, "")

    return {
        "language": lang,
        "template": template,
        "paper": paper,
        "orientation": orientation,
        "columns": columns,
        "accent": _hex(data.get("accent"), ""),
        "colors": colors,
        "title": _s(data.get("title"), 500),
        "authors": _s(data.get("authors"), 1500),
        "affiliations": _s(data.get("affiliations"), 2000),
        "email": _s(data.get("email"), 200),
        "url": _s(data.get("url"), 300),
        "logos_header": logos_header,
        "logos_footer": logos_footer,
        "sections": sections,
    }
