"""Renderização para template baseado em `sciposter` (Mostra de Iniciação Científica - Mostra IC)."""

from __future__ import annotations

from typing import Any, Dict, List

from .config import POSTER_SIZES
from .i18n import labels_for
from .templates import TEMPLATES

_UNNUMBERED = {"references", "acknowledgments"}


def _pt(v: float) -> str:
    return f"{v:.2f}"


def build_sciposter_tex(poster: Dict[str, Any], images: Dict[str, str]) -> str:
    from .latex import (
        _QR_OK, _hex_to_latex, _images_to_latex, _inline, escape_latex,
        references_to_latex, text_to_latex,
    )

    labels = labels_for(poster["language"])
    tpl = TEMPLATES[poster["template"]]
    c1, c2, c3 = tpl["colors"]
    bg_color = tpl.get("bg", "FFFFFF")
    if poster.get("colors"):
        colors = poster["colors"]
        if colors.get("accent"):
            c1 = colors["accent"]
        if colors.get("subtitle"):
            c2 = colors["subtitle"]
        if colors.get("title"):
            c3 = colors["title"]
        if colors.get("bg"):
            bg_color = colors["bg"]
    elif poster.get("accent"):
        c1 = c2 = poster["accent"]

    paper_key = poster.get("paper", "a0")
    orient = poster.get("orientation", "portrait")
    cols = max(1, poster.get("columns", 2))

    sections = [
        {**sec, "images": [{"file": images[i["path"]], "caption": i["caption"]} for i in sec["images"] if i["path"] in images]}
        for sec in poster["sections"]
    ]

    body: List[str] = []
    counter, fig = 0, [0]
    for idx, sec in enumerate(sections):
        title = _inline(sec["title"])
        if sec["id"] not in _UNNUMBERED:
            counter += 1
            title = f"{counter}. {title}"
        text = references_to_latex(sec["content"], small=True) if sec["id"] == "references" else text_to_latex(sec["content"])
        body.append(
            f"\\section{{{title}}}\n"
            f"{text}\n"
            f"{_images_to_latex(sec['images'], labels['figure'], fig, '\\small')}\n"
        )

    contact_bits = []
    if poster.get("email"):
        contact_bits.append(escape_latex(poster["email"]))
    if poster.get("url"):
        contact_bits.append(escape_latex(poster["url"]))
    qr = ""
    if _QR_OK.match(poster.get("url", "")):
        qr = f"\\begin{{center}}\\qrcode[height=2.5cm]{{{poster['url']}}}\\end{{center}}"

    if contact_bits:
        body.append(
            f"\\section*{{{labels['contact']}}}\n"
            + "\\\\\n".join(contact_bits)
            + ("\n" + qr if qr else "")
        )

    authors = escape_latex(poster.get("authors", "")).replace("\n", ", ")
    affil = "\\\\".join(escape_latex(ln.strip()) for ln in poster.get("affiliations", "").split("\n") if ln.strip())
    email = escape_latex(poster.get("email", ""))

    header_logos = [images[p] for p in poster.get("logos_header", []) if p in images]
    left_logo = f"\\leftlogo[1.2]{{{header_logos[0]}}}" if len(header_logos) >= 1 else ""
    right_logo = f"\\rightlogo[1.2]{{{header_logos[1]}}}" if len(header_logos) >= 2 else ""

    sciposter_size = paper_key if paper_key in ("a0", "a1", "a2") else "a0"
    col_str = "2" if cols == 2 else str(cols)

    return f"""\\documentclass[{sciposter_size},{orient}]{{sciposter}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage[{labels['babel']}]{{babel}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{multicol}}
\\usepackage{{graphicx}}
\\usepackage{{qrcode}}
\\usepackage{{xcolor}}

{_hex_to_latex('mainCol', c1)}
{_hex_to_latex('titleCol', c2)}
{_hex_to_latex('bgCol', bg_color)}

\\definecolor{{BoxCol}}{{HTML}}{{{c1}}}
\\definecolor{{SectionCol}}{{HTML}}{{{c1}}}

\\title{{{_inline(poster.get('title', '')) or '~'}}}
\\author{{{authors}}}
\\institute{{{affil}}}
\\email{{{email}}}

{left_logo}
{right_logo}

\\begin{{document}}
\\maketitle

\\begin{{multicols*}}{{{col_str}}}
{chr(10).join(body)}
\\end{{multicols*}}

\\end{{document}}
"""
