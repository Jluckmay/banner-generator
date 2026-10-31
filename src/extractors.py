"""Extração de texto de trabalhos enviados (PDF, DOCX, TXT/MD/TEX) e parser heurístico."""

from __future__ import annotations

import io
import re
import unicodedata
import zipfile
from typing import Any, Dict, List

from .config import MAX_DOC_CHARS
from .i18n import SECTION_ALIASES

ALLOWED_DOC_EXT = (".pdf", ".docx", ".txt", ".md", ".tex")
_MAX_ZIP_XML = 30 * 1024 * 1024


def extract_text(filename: str, raw: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        text = _pdf_text(raw)
    elif name.endswith(".docx"):
        text = _docx_text(raw)
    elif name.endswith(ALLOWED_DOC_EXT):
        text = raw.decode("utf-8", "replace")
        if name.endswith(".tex"):
            text = _strip_tex(text)
    else:
        raise ValueError("Formato não suportado. Use PDF, DOCX, TXT, MD ou TEX.")
    text = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()[:MAX_DOC_CHARS]


def _pdf_text(raw: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(raw))
    if reader.is_encrypted:
        raise ValueError("PDF protegido por senha não é suportado.")
    return "\n".join((p.extract_text() or "") for p in reader.pages[:60])


def _docx_text(raw: bytes) -> str:
    from defusedxml import ElementTree as ET

    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        info = zf.getinfo("word/document.xml")
        if info.file_size > _MAX_ZIP_XML:
            raise ValueError("DOCX grande demais.")
        root = ET.fromstring(zf.read("word/document.xml"))
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paras = []
    for p in root.iter(f"{ns}p"):
        paras.append("".join(t.text or "" for t in p.iter(f"{ns}t")))
    return "\n".join(paras)


def _strip_tex(src: str) -> str:
    src = re.sub(r"(?<!\\)%.*", "", src)
    m = re.search(r"\\begin\{document\}(.*)\\end\{document\}", src, re.S)
    body = m.group(1) if m else src
    title = re.search(r"\\title\{([^}]*)\}", src)
    body = re.sub(r"\\(?:sub)*section\*?\{([^}]*)\}", r"\n\1\n", body)
    body = re.sub(r"\\begin\{abstract\}", "\nAbstract\n", body)
    body = re.sub(r"\\(?:textbf|textit|emph|cite)\{([^}]*)\}", r"\1", body)
    body = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", "", body).replace("{", "").replace("}", "")
    return (title.group(1) + "\n" if title else "") + body


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9 &]", " ", s).strip()


_ALIAS_LOOKUP = {_norm(a): sid for sid, al in SECTION_ALIASES.items() for a in al}
_NUM = re.compile(r"^\s*(?:\d+(?:\.\d+)*\.?|[IVX]+\.)\s+")


def _heading(line: str) -> tuple[str, str] | None:
    """Retorna (id_da_seção, texto_inline) se a linha for um cabeçalho conhecido."""
    raw = line.strip()
    if not raw or len(raw) > 160:
        return None
    body = _NUM.sub("", raw)
    m = re.match(r"^(.{3,40}?)\s*[:—–-]\s+(.+)$", body)
    if m and _ALIAS_LOOKUP.get(_norm(m.group(1))):
        return _ALIAS_LOOKUP[_norm(m.group(1))], m.group(2)
    sid = _ALIAS_LOOKUP.get(_norm(body.rstrip(":")))
    return (sid, "") if sid else None


def _condense(text: str, limit: int) -> str:
    text = re.sub(r"[ \t]+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind(". "), cut.rfind(".\n"))
    return (cut[: end + 1] if end > limit * 0.5 else cut.rstrip() + "…").strip()


def heuristic_parse(text: str) -> Dict[str, Any]:
    """Extração sem IA: detecta título/autores e seções pelos cabeçalhos usuais."""
    lines = text.split("\n")
    sections: Dict[str, List[str]] = {}
    current: str | None = None
    head: List[str] = []
    for line in lines:
        h = _heading(line)
        if h:
            current = h[0]
            sections.setdefault(current, [])
            if h[1]:
                sections[current].append(h[1])
            continue
        if current is None:
            if line.strip():
                head.append(line.strip())
        else:
            sections[current].append(line)

    title = authors = affiliations = ""
    if head:
        title = head[0]
        idx = 1
        while idx < len(head) and len(head[idx - 1]) < 60 and len(head[idx]) < 90 and idx < 3 and not re.search(r"@|,|\band\b| e ", head[idx]):
            title += " " + head[idx]
            idx += 1
        if idx < len(head):
            authors = head[idx]
        affiliations = "\n".join(head[idx + 1 : idx + 5])
    email = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "\n".join(head) or text[:3000])
    limits = {"abstract": 1400, "references": 2500, "acknowledgments": 400}
    out_sections = []
    for sid, buf in sections.items():
        content = "\n".join(buf).strip()
        if content:
            body = content if sid == "references" else _unwrap(content)
            out_sections.append({"id": sid, "content": _condense(body, limits.get(sid, 1100))})
    return {
        "title": title[:300],
        "authors": authors[:600],
        "affiliations": affiliations[:800],
        "email": email.group(0) if email else "",
        "sections": out_sections,
    }


def _unwrap(text: str) -> str:
    """Junta quebras de linha de PDF dentro de parágrafos, preservando listas."""
    out: List[str] = []
    for ln in text.split("\n"):
        s = ln.strip()
        if not s:
            out.append("")
        elif out and out[-1] and not re.match(r"^(?:[-*•–]|\d{1,2}[.)])\s", s) and not out[-1].endswith(":"):
            out[-1] += " " + s
        else:
            out.append(s)
    return "\n".join(out)
