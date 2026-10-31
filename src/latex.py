"""Renderização LaTeX (tikzposter) e compilação do pôster."""

from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .config import LATEX_TIMEOUT_S, PAPER_SIZES
from .i18n import labels_for
from .templates import TEMPLATES

_ESC = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

_UNICODE_MAP = {
    "≥": r"$\geq$", "≤": r"$\leq$", "±": r"$\pm$", "→": r"$\rightarrow$", "←": r"$\leftarrow$",
    "↑": r"$\uparrow$", "↓": r"$\downarrow$", "≈": r"$\approx$", "≠": r"$\neq$", "∞": r"$\infty$",
    "α": r"$\alpha$", "β": r"$\beta$", "γ": r"$\gamma$", "δ": r"$\delta$", "ε": r"$\epsilon$",
    "θ": r"$\theta$", "λ": r"$\lambda$", "μ": r"$\mu$", "π": r"$\pi$", "σ": r"$\sigma$",
    "φ": r"$\phi$", "ω": r"$\omega$", "Δ": r"$\Delta$", "Σ": r"$\Sigma$", "Ω": r"$\Omega$",
    "∑": r"$\sum$", "√": r"$\surd$", "∂": r"$\partial$", "−": "-", "\u00a0": "~", "\u2009": " ",
    "\u202f": " ", "\u200b": "", "\ufeff": "", "ﬁ": "fi", "ﬂ": "fl", "‐": "-", "‑": "-",
}
_KEEP_HIGH = set("–—‘’‚“”„•…€™†‡‰‹›")

_MATH_CMDS = {
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "theta", "lambda", "mu", "nu", "pi",
    "rho", "sigma", "tau", "phi", "varphi", "chi", "psi", "omega", "Gamma", "Delta", "Theta",
    "Lambda", "Pi", "Sigma", "Phi", "Psi", "Omega", "frac", "sqrt", "sum", "prod", "int", "pm",
    "mp", "times", "cdot", "div", "leq", "geq", "le", "ge", "neq", "approx", "sim", "propto",
    "infty", "partial", "nabla", "rightarrow", "leftarrow", "Rightarrow", "to", "log", "ln", "exp",
    "sin", "cos", "tan", "lim", "min", "max", "mathrm", "mathbf", "mathit", "text", "left", "right",
    "ldots", "cdots", "degree", "circ", "bar", "hat", "vec", "overline", "in", "subset", "cup", "cap",
}
_MATH_OK = re.compile(r"^[A-Za-z0-9\s+\-*/=<>()\[\]{}^_.,;:|'!\\]*$")


def _safe_math(expr: str) -> bool:
    if not expr or len(expr) > 300 or not _MATH_OK.match(expr):
        return False
    return all(c in _MATH_CMDS for c in re.findall(r"\\([A-Za-z]+)", expr)) and "\\\\" not in expr


def escape_latex(text: str) -> str:
    out: List[str] = []
    for ch in text:
        if ch in _ESC:
            out.append(_ESC[ch])
        elif ch in _UNICODE_MAP:
            out.append(_UNICODE_MAP[ch])
        elif ord(ch) > 0x17F and ch not in _KEEP_HIGH:
            continue
        elif ord(ch) < 32 and ch not in "\n\t\x00":
            continue
        else:
            out.append(ch)
    return "".join(out)


def _inline(text: str) -> str:
    """Escapa texto e aplica **negrito**, *itálico* e $math$ seguro."""
    maths: List[str] = []
    text = text.replace("\x00", "")

    def stash(m: "re.Match[str]") -> str:
        expr = m.group(1)
        if _safe_math(expr):
            maths.append(f"${expr}$")
            return f"\x00M{len(maths) - 1}\x00"
        return m.group(0)

    text = re.sub(r"(?<!\\)\$([^$\n]+?)\$", stash, text)
    esc = escape_latex(text)
    esc = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", esc)
    esc = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\\textit{\1}", esc)
    return re.sub(r"\x00M(\d+)\x00", lambda m: maths[int(m.group(1))], esc)


_BULLET = re.compile(r"^\s*(?:[-*•–]\s+)(.*)$")
_NUMBERED = re.compile(r"^\s*\d{1,2}[.)]\s+(.*)$")


def text_to_latex(text: str) -> str:
    """Converte texto simples (parágrafos, listas com '- ' ou '1. ') em LaTeX."""
    blocks = re.split(r"\n\s*\n", text.strip())
    out: List[str] = []
    for block in blocks:
        lines = [ln for ln in block.split("\n") if ln.strip()]
        i = 0
        while i < len(lines):
            kind = "ul" if _BULLET.match(lines[i]) else "ol" if _NUMBERED.match(lines[i]) else None
            if kind:
                rx = _BULLET if kind == "ul" else _NUMBERED
                items: List[str] = []
                while i < len(lines) and rx.match(lines[i]):
                    items.append(rx.match(lines[i]).group(1))  # type: ignore[union-attr]
                    i += 1
                env = "itemize" if kind == "ul" else "enumerate"
                out.append(
                    f"\\begin{{{env}}}\n"
                    + "\n".join(f"\\item {_inline(it)}" for it in items)
                    + f"\n\\end{{{env}}}"
                )
            else:
                para: List[str] = []
                while i < len(lines) and not _BULLET.match(lines[i]) and not _NUMBERED.match(lines[i]):
                    para.append(lines[i].strip())
                    i += 1
                out.append(_inline(" ".join(para)) + "\n")
    return "\n".join(out)


def references_to_latex(text: str, small: bool = True) -> str:
    items = [ln.strip() for ln in text.split("\n") if ln.strip()]
    items = [re.sub(r"^\s*(?:\[\d+\]|\d+[.)]|[-*•])\s*", "", it) for it in items]
    if not items:
        return ""
    return (
        ("{\\small" if small else "{")
        + "\\begin{enumerate}\n"
        + "\n".join(f"\\item {_inline(it)}" for it in items)
        + "\n\\end{enumerate}}"
    )


def _images_to_latex(images: List[Dict[str, str]], fig_label: str, counter: List[int], cap_cmd: str = "\\small") -> str:
    out: List[str] = []
    for start in range(0, len(images), 2):
        row = images[start : start + 2]
        w = "0.48" if len(row) == 2 else "0.9"
        cells = []
        for img in row:
            counter[0] += 1
            cap = img.get("caption", "")
            caption = (
                f"\\\\[2pt]{{{cap_cmd}\\itshape {fig_label} {counter[0]}: {_inline(cap)}}}" if cap else ""
            )
            cells.append(
                f"\\begin{{minipage}}[t]{{{w}\\linewidth}}\\centering"
                f"\\includegraphics[width=\\linewidth,height=0.22\\textheight,keepaspectratio]"
                f"{{{img['file']}}}{caption}\\end{{minipage}}"
            )
        out.append("\\begin{center}\n" + "\\hfill\n".join(cells) + "\n\\end{center}")
    return "\n".join(out)


def _weight(sec: Dict[str, Any]) -> int:
    return 350 + len(sec["content"]) + 900 * len(sec["images"])


def split_columns(sections: List[Dict[str, Any]], n: int) -> List[List[Dict[str, Any]]]:
    """Distribui seções contíguas em n colunas com carga aproximadamente equilibrada."""
    n = max(1, min(n, len(sections) or 1))
    total = sum(_weight(s) for s in sections)
    cols: List[List[Dict[str, Any]]] = [[]]
    acc = 0
    for s in sections:
        w = _weight(s)
        remaining_cols = n - len(cols)
        target = total * len(cols) / n
        if cols[-1] and remaining_cols > 0 and acc + w / 2 > target:
            cols.append([])
        cols[-1].append(s)
        acc += w
    return cols


_QR_OK = re.compile(r"^https?://[A-Za-z0-9\-._~:/?=@+]+$")


def _hex_to_latex(name: str, value: str) -> str:
    return f"\\definecolor{{{name}}}{{HTML}}{{{value}}}"


def build_tex(poster: Dict[str, Any], images: Dict[str, str]) -> str:
    """Gera o fonte LaTeX. `images` mapeia caminhos de upload -> nome de arquivo no build."""
    if TEMPLATES[poster["template"]].get("engine") == "article":
        from .article import build_article_tex

        return build_article_tex(poster, images)
    labels = labels_for(poster["language"])
    tpl = TEMPLATES[poster["template"]]
    paper = PAPER_SIZES[poster["paper"]]
    c1, c2, c3 = tpl["colors"]
    if poster.get("accent"):
        c1 = c2 = poster["accent"]
    font = "\\renewcommand{\\familydefault}{\\sfdefault}\n" if tpl["sans"] else ""

    sections = []
    for s in poster["sections"]:
        sections.append(
            {**s, "images": [{"file": images[i["path"]], "caption": i["caption"]} for i in s["images"] if i["path"] in images]}
        )
    contact_bits = []
    if poster["email"]:
        contact_bits.append(_inline(poster["email"]))
    qr = ""
    if _QR_OK.match(poster["url"]):
        qr = f"\\begin{{center}}\\qrcode[height=3cm]{{{poster['url']}}}\\end{{center}}"
        contact_bits.append(escape_latex(poster["url"]))
    elif poster["url"]:
        contact_bits.append(escape_latex(poster["url"]))
    contact_block = None
    if contact_bits:
        contact_block = {
            "id": "contact",
            "title": labels["contact"],
            "latex": "\\\\\n".join(contact_bits) + ("\n" + qr if qr else ""),
            "content": "",
            "images": [],
        }

    cols = split_columns(sections, poster["columns"])
    counter = [0]
    col_tex: List[str] = []
    for ci, col in enumerate(cols):
        parts = [f"\\column{{{1 / len(cols):.4f}}}"]
        for s in col:
            body = references_to_latex(s["content"]) if s["id"] == "references" else text_to_latex(s["content"])
            body += "\n" + _images_to_latex(s["images"], labels["figure"], counter)
            parts.append(f"\\block{{{_inline(s['title'])}}}{{\n{body}\n}}")
        if contact_block and ci == len(cols) - 1:
            parts.append(f"\\block{{{contact_block['title']}}}{{\n{contact_block['latex']}\n}}")
        col_tex.append("\n".join(parts))
    if not sections and contact_block:
        col_tex = [f"\\column{{1}}\n\\block{{{contact_block['title']}}}{{\n{contact_block['latex']}\n}}"]

    logos = "".join(
        f"\\includegraphics[height=6cm]{{{images[p]}}}\\hspace{{2cm}}" for p in poster["logos_header"] if p in images
    )
    title = _inline(poster["title"]) or "~"
    authors = escape_latex(poster["authors"]).replace("\n", ", ")
    institute = "\\\\".join(escape_latex(ln.strip()) for ln in poster["affiliations"].split("\n") if ln.strip())

    return f"""\\documentclass[{poster.get('_font') or paper['font']},{paper['paper']},{poster['orientation']},margin=20mm,innermargin=12mm,blockverticalspace=12mm,colspace=12mm,subcolspace=8mm]{{tikzposter}}
\\usepackage[T1]{{fontenc}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[{labels['babel']}]{{babel}}
\\usepackage{{lmodern}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{qrcode}}
{font}\\definecolorstyle{{PosterColors}}{{
  {_hex_to_latex('colorOne', c1)}
  {_hex_to_latex('colorTwo', c2)}
  {_hex_to_latex('colorThree', c3)}
}}{{
  {_hex_to_latex('posterbg', tpl['bg'])}
  \\colorlet{{backgroundcolor}}{{posterbg}}
  \\colorlet{{framecolor}}{{colorOne}}
  \\colorlet{{titlefgcolor}}{{white}}
  \\colorlet{{titlebgcolor}}{{colorOne}}
  \\colorlet{{blocktitlebgcolor}}{{colorTwo}}
  \\colorlet{{blocktitlefgcolor}}{{white}}
  \\colorlet{{blockbodybgcolor}}{{white}}
  \\colorlet{{blockbodyfgcolor}}{{black}}
  \\colorlet{{innerblocktitlebgcolor}}{{colorThree}}
  \\colorlet{{innerblocktitlefgcolor}}{{black}}
  \\colorlet{{innerblockbodybgcolor}}{{white}}
  \\colorlet{{innerblockbodyfgcolor}}{{black}}
  \\colorlet{{notefgcolor}}{{black}}
  \\colorlet{{notebgcolor}}{{colorThree}}
  \\colorlet{{noteframecolor}}{{colorOne}}
}}
\\usecolorstyle{{PosterColors}}
\\useblockstyle{{{tpl['block']}}}
\\usetitlestyle{{{tpl['title']}}}
\\usebackgroundstyle{{{tpl['background']}}}
\\title{{{title}}}
\\author{{{authors}}}
\\institute{{{institute}}}
\\titlegraphic{{{logos}}}
\\begin{{document}}
\\maketitle
\\begin{{columns}}
{chr(10).join(col_tex)}
\\end{{columns}}
\\end{{document}}
"""


def make_zip(tex: str, build_dir: Path) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("poster.tex", tex)
        for f in build_dir.iterdir():
            if f.suffix.lower() in (".png", ".jpg"):
                zf.write(f, f.name)
    return buf.getvalue()


def compile_tex(tex: str, build_dir: Path) -> Tuple[bytes, str]:
    """Compila com pdflatex (sem shell-escape). Retorna (pdf, log)."""
    exe = shutil.which("pdflatex")
    if not exe:
        raise RuntimeError("pdflatex não encontrado no PATH (instale TeX Live ou MiKTeX).")
    (build_dir / "poster.tex").write_text(tex, encoding="utf-8")
    (build_dir / "poster.pdf").unlink(missing_ok=True)
    log = ""
    env = {k: v for k, v in os.environ.items() if not k.lower().endswith(("_key", "_token", "_secret"))}
    for _ in range(2):
        proc = subprocess.run(
            [exe, "-interaction=nonstopmode", "-no-shell-escape", "poster.tex"],
            cwd=build_dir, capture_output=True, timeout=LATEX_TIMEOUT_S, env=env,
        )
        log = proc.stdout.decode("utf-8", "replace")
        if "Rerun" not in log:
            break
    pdf = build_dir / "poster.pdf"
    if not pdf.exists() or pdf.stat().st_size == 0:
        err = [ln for ln in log.splitlines() if ln.startswith("!")][:5]
        raise RuntimeError("Falha ao compilar o LaTeX: " + " | ".join(err))
    return pdf.read_bytes(), log


FONT_STEPS = ["12pt", "14pt", "17pt", "20pt", "25pt"]


def content_overflows(pdf: bytes) -> bool:
    """True se algum texto foi posicionado fora (abaixo) da página."""
    from pypdf import PdfReader

    page = PdfReader(io.BytesIO(pdf)).pages[0]
    ys: List[float] = []

    def visit(text: str, cm: Any, tm: Any, _fd: Any, _fs: Any) -> None:
        if text.strip():
            ys.append(tm[5] * cm[3] + cm[5])

    page.extract_text(visitor_text=visit)
    return bool(ys) and min(ys) < 0


ARTICLE_FIT_STEPS = [1.0, 0.92, 0.85, 0.78, 0.72, 0.66, 0.6, 0.55, 0.5, 0.45]


def fit_compile(poster: Dict[str, Any], images: Dict[str, str], build_dir: Path) -> Tuple[bytes, str, bool]:
    """Compila reduzindo a fonte base até o conteúdo caber. Retorna (pdf, tex, overflow)."""
    from pypdf import PdfReader

    pdf, tex, over = b"", "", True
    if TEMPLATES[poster["template"]].get("engine") == "article":
        for fit in ARTICLE_FIT_STEPS:  # transbordo = conteúdo vai para 2ª página
            tex = build_tex({**poster, "_fit": fit}, images)
            pdf, _ = compile_tex(tex, build_dir)
            over = len(PdfReader(io.BytesIO(pdf)).pages) > 1
            if not over:
                break
        return pdf, tex, over
    start = FONT_STEPS.index(PAPER_SIZES[poster["paper"]]["font"])
    for font in FONT_STEPS[start::-1]:
        tex = build_tex({**poster, "_font": font}, images)
        pdf, _ = compile_tex(tex, build_dir)
        over = content_overflows(pdf)
        if not over:
            break
    return pdf, tex, over


def new_build_dir() -> Path:
    return Path(tempfile.mkdtemp(prefix="poster_"))
