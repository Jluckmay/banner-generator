"""Definições dos templates visuais (estilos tikzposter + `article`/multicols + paleta)."""

from __future__ import annotations

from typing import Any, Dict

from .config import MAX_LOGOS_FOOTER, MAX_LOGOS_HEADER

DEFAULT_TEMPLATE = "classic"

TIKZ_PAPERS = ["a0", "a1", "a2", "a3"]

# colors: colorOne (moldura/destaque), colorTwo, colorThree
# bg: fundo do pôster (HTML hex sem '#')
# logos: vagas de logotipos por região do template (cabeçalho/rodapé)
TEMPLATES: Dict[str, Dict[str, Any]] = {
    "classic": {
        "name": {"pt-BR": "Clássico", "en-US": "Classic"},
        "engine": "tikzposter",
        "block": "Default", "title": "Filled", "background": "Default",
        "colors": ("1F3A5F", "2E5C8A", "9DB9D8"), "bg": "EEF2F7", "sans": False,
        "logos": {"header": MAX_LOGOS_HEADER, "footer": 0},
    },
    "modern": {
        "name": {"pt-BR": "Moderno", "en-US": "Modern"},
        "engine": "tikzposter",
        "block": "Basic", "title": "Basic", "background": "VerticalGradient",
        "colors": ("0F766E", "14B8A6", "99F6E4"), "bg": "F0FDFA", "sans": True,
        "logos": {"header": MAX_LOGOS_HEADER, "footer": 0},
    },
    "minimal": {
        "name": {"pt-BR": "Minimalista", "en-US": "Minimal"},
        "engine": "tikzposter",
        "block": "Minimal", "title": "Empty", "background": "Default",
        "colors": ("374151", "6B7280", "D1D5DB"), "bg": "FFFFFF", "sans": True,
        "logos": {"header": MAX_LOGOS_HEADER, "footer": 0},
    },
    "bold": {
        "name": {"pt-BR": "Ousado", "en-US": "Bold"},
        "engine": "tikzposter",
        "block": "Envelope", "title": "Envelope", "background": "Default",
        "colors": ("7C2D12", "EA580C", "FED7AA"), "bg": "FFF7ED", "sans": True,
        "logos": {"header": MAX_LOGOS_HEADER, "footer": 0},
    },
    "corner": {
        "name": {"pt-BR": "Esmeralda", "en-US": "Emerald"},
        "engine": "tikzposter",
        "block": "Corner", "title": "Wave", "background": "BottomVerticalGradient",
        "colors": ("14532D", "16A34A", "BBF7D0"), "bg": "F0FDF4", "sans": False,
        "logos": {"header": MAX_LOGOS_HEADER, "footer": 0},
    },
    "dcc": {
        "name": {"pt-BR": "DCC/UFMG (vermelho)", "en-US": "DCC/UFMG (red)"},
        "engine": "article",
        "colors": ("CC0000", "444444", "1A1A1A"), "bg": "FFFFFF", "sans": True,
        "papers": ["60x90", "a0", "a1", "a2", "a3"], "default_paper": "60x90",
        "default_columns": 2,
        "logos": {"header": MAX_LOGOS_HEADER, "footer": MAX_LOGOS_FOOTER},
    },
}


def papers_for(tid: str) -> list:
    return TEMPLATES[tid].get("papers", TIKZ_PAPERS)


def default_paper_for(tid: str) -> str:
    return TEMPLATES[tid].get("default_paper", "a0")


def public_templates() -> Dict[str, Any]:
    return {
        tid: {
            "name": t["name"],
            "colors": list(t["colors"]),
            "bg": t["bg"],
            "papers": papers_for(tid),
            "default_paper": default_paper_for(tid),
            "logos": t["logos"],
        }
        for tid, t in TEMPLATES.items()
    }
