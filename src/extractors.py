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
    text = clean_hyphens(text)
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


_SUFFIX_FRAGMENTS = {
    "ties", "ence", "ences", "tion", "tions", "ment", "ments", "ted",
    "ting", "able", "ible", "ing", "ings", "ity", "ities", "ive", "ives",
    "ally", "al", "als", "ularization", "ization", "izations", "ised", "ized",
    "ness", "nesses", "sion", "sions", "ture", "tures", "ous", "ously",
    "ated", "ating", "ates", "ance", "ances", "ism", "isms", "ist", "ists"
}

_AFFIL_KEYWORDS = {
    "universidade", "university", "dept", "department", "departamento",
    "instituto", "institute", "laboratorio", "laboratory", "ufmg", "usp",
    "unicamp", "ufrj", "unesp", "puc", "faculdade", "faculty", "college",
    "school", "center", "centro", "federal", "campus"
}


def clean_hyphens(text: str) -> str:
    """Conserta palavras quebradas por hífens de fim de linha ou OCR em PDFs."""
    # Quebra de linha direta com hífen: word-\nnext -> wordnext
    text = re.sub(r"(\b[A-Za-z]{2,})-\s*\n\s*([a-z]{2,}\b)", r"\1\2", text)
    # Hífen com espaço inline oriundo de quebra de página/coluna: differ- ences -> differences
    def _fix_broken(m: re.Match) -> str:
        w1, w2 = m.group(1), m.group(2)
        if w2.lower() in _SUFFIX_FRAGMENTS or len(w1) <= 3:
            return w1 + w2
        return f"{w1}-{w2}"

    return re.sub(r"\b([A-Za-z]{2,})-\s+([a-z]{2,}\b)", _fix_broken, text)


def _format_references(raw: str) -> str:
    """Formata referências bibliográficas uma por linha, separando marcadores [1], [2], etc."""
    text = clean_hyphens(raw)
    text = re.sub(r"\s*(\[\d{1,3}\])\s*", r"\n\1 ", text)
    text = re.sub(r"(?<=[.\s])(\d{1,2}\.\s+[A-Z])", r"\n\1", text)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    return "\n".join(ln for ln in lines if ln)


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
    text = clean_hyphens(text)
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

    # Identificar emails e tokens de nome de usuário dos autores
    header_blob = "\n".join(head)
    emails = re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", header_blob or text[:3000])
    email_tokens = set()
    for e in emails:
        user = e.split("@")[0]
        for part in re.split(r"[._+-]", user):
            if len(part) >= 3:
                email_tokens.add(_norm(part))

    title_parts: List[str] = []
    authors_list: List[str] = []
    affiliations_list: List[str] = []

    idx = 0
    while idx < len(head) and idx < 3:
        line = head[idx]
        h_norm = _norm(line)
        if "@" in line or any(k in h_norm.split() for k in _AFFIL_KEYWORDS):
            break

        words = line.split()
        matched = [i for i, w in enumerate(words) if _norm(w) in email_tokens]
        if matched:
            first_m = matched[0]
            start = max(0, first_m - 1)
            t_part = " ".join(words[:start]).strip()
            a_part = " ".join(words[start:]).strip()
            if t_part:
                title_parts.append(t_part)
            if a_part:
                authors_list.append(a_part)
            idx += 1
            break
        else:
            if idx > 0 and ("," in line or re.search(r"\band\b| e ", line)):
                break
            title_parts.append(line)
            idx += 1
            if len(line) < 40 and idx > 1:
                break

    title = " ".join(title_parts).strip()

    for h_line in head[idx:]:
        line_no_emails = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", " ", h_line).strip()
        if not line_no_emails:
            continue
        line_tokens = [_norm(w) for w in line_no_emails.split()]
        is_affil = any(k in line_tokens for k in _AFFIL_KEYWORDS)
        has_author_match = any(t in email_tokens for t in line_tokens)

        if is_affil and not has_author_match:
            affiliations_list.append(line_no_emails)
        elif has_author_match:
            subparts = line_no_emails.split()
            auth_sub = []
            aff_sub = []
            for sp in subparts:
                if _norm(sp) in _AFFIL_KEYWORDS:
                    aff_sub.append(sp)
                else:
                    auth_sub.append(sp)
            if auth_sub:
                authors_list.append(" ".join(auth_sub))
            if aff_sub:
                affiliations_list.append(" ".join(aff_sub))
        else:
            if not authors_list:
                authors_list.append(line_no_emails)
            else:
                affiliations_list.append(line_no_emails)

    authors = ", ".join(dict.fromkeys([a.strip() for a in authors_list if a.strip()]))
    affiliations = "\n".join(dict.fromkeys([af.strip() for af in affiliations_list if af.strip()]))

    limits = {"abstract": 1400, "references": 2500, "acknowledgments": 400}
    out_sections = []
    for sid, buf in sections.items():
        content = "\n".join(buf).strip()
        if content:
            body = _format_references(content) if sid == "references" else _unwrap(clean_hyphens(content))
            out_sections.append({"id": sid, "content": _condense(body, limits.get(sid, 1100))})

    return {
        "title": title[:300].strip(),
        "authors": authors[:600].strip(),
        "affiliations": affiliations[:800].strip(),
        "email": emails[0] if emails else "",
        "sections": out_sections,
    }


def _unwrap(text: str) -> str:
    """Junta quebras de linha de PDF dentro de parágrafos, preservando listas e hífens corrigidos."""
    text = clean_hyphens(text)
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
