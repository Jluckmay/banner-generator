"""Definições dos templates visuais (estilos tikzposter + paleta)."""

from __future__ import annotations

from typing import Any, Dict

DEFAULT_TEMPLATE = "classic"

# colors: colorOne (moldura/destaque), colorTwo (título dos blocos), colorThree (realces)
# bg: fundo do pôster (HTML hex sem '#')
TEMPLATES: Dict[str, Dict[str, Any]] = {
    "classic": {
        "name": {"pt-BR": "Clássico", "en-US": "Classic"},
        "block": "Default",
        "title": "Filled",
        "background": "Default",
        "colors": ("1F3A5F", "2E5C8A", "9DB9D8"),
        "bg": "EEF2F7",
        "sans": False,
    },
    "modern": {
        "name": {"pt-BR": "Moderno", "en-US": "Modern"},
        "block": "Basic",
        "title": "Basic",
        "background": "VerticalGradient",
        "colors": ("0F766E", "14B8A6", "99F6E4"),
        "bg": "F0FDFA",
        "sans": True,
    },
    "minimal": {
        "name": {"pt-BR": "Minimalista", "en-US": "Minimal"},
        "block": "Minimal",
        "title": "Empty",
        "background": "Default",
        "colors": ("374151", "6B7280", "D1D5DB"),
        "bg": "FFFFFF",
        "sans": True,
    },
    "bold": {
        "name": {"pt-BR": "Ousado", "en-US": "Bold"},
        "block": "Envelope",
        "title": "Envelope",
        "background": "Default",
        "colors": ("7C2D12", "EA580C", "FED7AA"),
        "bg": "FFF7ED",
        "sans": True,
    },
    "corner": {
        "name": {"pt-BR": "Esmeralda", "en-US": "Emerald"},
        "block": "Corner",
        "title": "Wave",
        "background": "BottomVerticalGradient",
        "colors": ("14532D", "16A34A", "BBF7D0"),
        "bg": "F0FDF4",
        "sans": False,
    },
}


def public_templates() -> Dict[str, Any]:
    return {
        tid: {"name": t["name"], "colors": list(t["colors"]), "bg": t["bg"]}
        for tid, t in TEMPLATES.items()
    }
