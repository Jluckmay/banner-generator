"""Testes do gerador de pôsteres."""

import io
import json
import shutil

import pytest
from PIL import Image

from server import app
from src.extractors import extract_text, heuristic_parse
from src.latex import build_tex, escape_latex, split_columns, text_to_latex
from src.poster import normalize_poster
from src.templates import TEMPLATES

PAPER = """Efeito da luz no crescimento de plantas
Maria Silva, João Souza
Universidade Federal de Teste
maria@exemplo.edu

Resumo
Este estudo avaliou o crescimento de plantas sob diferentes espectros de luz durante 30 dias, com 5% de variação.

1. Introdução
A luz é essencial para a fotossíntese.
- Item um
- Item dois

Metodologia
Foram cultivadas 60 plantas.

Resultados
A luz azul aumentou a biomassa em 20%.

Conclusão
A luz importa.

Referências
[1] Autor A. Título. 2020.
[2] Autor B. Outro. 2021.
"""


def test_escape_blocks_injection():
    out = escape_latex(r"\input{/etc/passwd} 50% & #1 _x_ {y}")
    assert "\\input" not in out.replace("\\textbackslash{}input", "")
    assert r"\%" in out and r"\&" in out


def test_math_whitelist():
    assert "$\\alpha^2$" in text_to_latex("Valor $\\alpha^2$ ok")
    bad = text_to_latex(r"Mau $\input{x}$")
    assert "$\\input" not in bad


def test_bold_italic_and_lists():
    tex = text_to_latex("**forte** e *itálico*\n\n- a\n- b\n\n1. um\n2. dois")
    assert "\\textbf{forte}" in tex and "\\textit{itálico}" in tex
    assert "\\begin{itemize}" in tex and "\\begin{enumerate}" in tex


def test_heuristic_parse():
    r = heuristic_parse(PAPER)
    ids = {s["id"] for s in r["sections"]}
    assert {"abstract", "introduction", "methods", "results", "conclusions", "references"} <= ids
    assert r["title"].startswith("Efeito da luz")
    assert r["email"] == "maria@exemplo.edu"


def test_extract_txt_and_unsupported():
    assert "Resumo" in extract_text("a.txt", PAPER.encode())
    with pytest.raises(ValueError):
        extract_text("a.exe", b"x")


def test_split_columns_balanced():
    secs = [{"content": "x" * 500, "images": []} for _ in range(6)]
    cols = split_columns(secs, 3)
    assert len(cols) == 3 and all(cols)


def test_normalize_defaults():
    p = normalize_poster({"template": "nope", "paper": "z", "columns": 99, "sections": [{"id": "abstract", "content": "x"}]})
    assert p["template"] == "classic" and p["paper"] == "a0" and p["columns"] == 4
    assert p["sections"][0]["title"] == "Resumo"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_config_endpoint(client):
    j = client.get("/api/config").get_json()
    assert set(j["templates"]) == set(TEMPLATES) and "pt-BR" in j["languages"]


def test_extract_endpoint_basic(client):
    r = client.post("/api/extract", data={"mode": "basic", "file": (io.BytesIO(PAPER.encode()), "p.txt")})
    assert r.status_code == 200 and r.get_json()["poster"]["title"]


def test_extract_ai_without_key_falls_back(client, monkeypatch):
    for k in ("GEMINI_API_KEY",):
        monkeypatch.delenv(k, raising=False)
    j = client.post("/api/extract", data={"mode": "ai", "file": (io.BytesIO(PAPER.encode()), "p.txt")}).get_json()
    assert j["mode"] == "basic" and j["warning"]


def test_generate_validation(client):
    assert client.post("/api/generate", data={"data": "{}"}).status_code == 400
    assert client.post("/api/generate", data={"data": "nope"}).status_code == 400


def test_bad_image_rejected(client):
    data = {"title": "T", "sections": [{"id": "abstract", "content": "x", "images": [{"path": "i0"}]}]}
    r = client.post("/api/generate?format=tex", data={"data": json.dumps(data), "i0": (io.BytesIO(b"not an image"), "x.png")})
    assert r.status_code == 400


def _png():
    buf = io.BytesIO()
    Image.new("RGB", (200, 120), "red").save(buf, "PNG")
    return buf.getvalue()


@pytest.mark.skipif(not shutil.which("pdflatex"), reason="pdflatex ausente")
@pytest.mark.parametrize("tpl", list(TEMPLATES))
@pytest.mark.parametrize("lang", ["pt-BR", "en-US"])
def test_generate_pdf_all_templates(client, tpl, lang):
    data = {
        "title": "Título com & caracteres % especiais",
        "authors": "Ana, Bruno",
        "affiliations": "Univ. X",
        "email": "a@b.com",
        "url": "https://exemplo.com/p",
        "language": lang,
        "template": tpl,
        "paper": "a1",
        "orientation": "landscape",
        "columns": 3,
        "sections": [
            {"id": "abstract", "content": "Resumo com $x^2$ e **negrito**."},
            {"id": "results", "content": "- a\n- b", "images": [{"path": "i0", "caption": "Gráfico 50%"}, {"path": "i1"}]},
            {"id": "references", "content": "[1] Ref A\n[2] Ref B"},
            {"id": "custom1", "title": "Minha seção", "content": "texto"},
        ],
        "logos": ["l0"],
    }
    files = {"i0": (io.BytesIO(_png()), "a.png"), "i1": (io.BytesIO(_png()), "b.png"), "l0": (io.BytesIO(_png()), "l.png")}
    r = client.post("/api/generate", data={"data": json.dumps(data), **files})
    assert r.status_code == 200, r.get_data(as_text=True)
    assert r.data.startswith(b"%PDF")


def test_build_tex_has_babel_and_columns():
    p = normalize_poster({"title": "T", "language": "en-US", "columns": 2, "sections": [{"id": "abstract", "content": "x"}, {"id": "results", "content": "y"}]})
    tex = build_tex(p, {})
    assert "[english]{babel}" in tex and tex.count("\\column{") == 2


@pytest.mark.skipif(not shutil.which("pdflatex"), reason="pdflatex ausente")
def test_fit_reduces_font_and_flags_overflow(client):
    big = {"title": "T", "paper": "a3", "columns": 1, "sections": [{"id": f"c{i}", "title": "S", "content": "palavra " * 2500} for i in range(6)]}
    r = client.post("/api/generate", data={"data": json.dumps(big)})
    assert r.status_code == 200 and r.headers.get("X-Poster-Overflow") == "1"
    mid = {"title": "T", "paper": "a2", "columns": 2, "sections": [{"id": "abstract", "content": ("palavra " * 120 + "\n\n") * 6}]}
    r = client.post("/api/generate", data={"data": json.dumps(mid)})
    assert r.status_code == 200 and not r.headers.get("X-Poster-Overflow")


def test_logo_limits_per_template():
    p = normalize_poster({"template": "dcc", "logos_header": list("abc"), "logos_footer": list("abcdefg"), "sections": []})
    assert len(p["logos_header"]) == 2 and len(p["logos_footer"]) == 5 and p["paper"] == "60x90"
    c = normalize_poster({"template": "classic", "logos_header": list("abc"), "logos_footer": ["x"], "paper": "60x90", "sections": []})
    assert len(c["logos_header"]) == 2 and c["logos_footer"] == [] and c["paper"] == "a0"


@pytest.mark.skipif(not shutil.which("pdflatex"), reason="pdflatex ausente")
@pytest.mark.parametrize("paper", ["60x90", "a2"])
def test_dcc_template_with_header_and_footer_logos(client, paper):
    data = {
        "title": "Otimização Avançada", "authors": "A, B", "affiliations": "DCC - UFMG", "email": "a@b.com",
        "url": "https://exemplo.com/p", "template": "dcc", "paper": paper, "columns": 2,
        "logos_header": ["h0", "h1", "h2"], "logos_footer": [f"f{i}" for i in range(6)],
        "sections": [
            {"id": "introduction", "content": "Texto $x^2$ com **negrito**." * 5},
            {"id": "results", "content": "- a\n- b", "images": [{"path": "g0", "caption": "Gráfico"}]},
            {"id": "references", "content": "[1] Ref A\n[2] Ref B"},
        ],
    }
    names = ["h0", "h1", "h2", "g0"] + [f"f{i}" for i in range(6)]
    files = {n: (io.BytesIO(_png()), n + ".png") for n in names}
    r = client.post("/api/generate", data={"data": json.dumps(data), **files})
    assert r.status_code == 200 and r.data.startswith(b"%PDF") and not r.headers.get("X-Poster-Overflow")
    z = client.post("/api/generate?format=zip", data={"data": json.dumps(data), **{n: (io.BytesIO(_png()), n + ".png") for n in names}})
    import zipfile
    with zipfile.ZipFile(io.BytesIO(z.data)) as zf:
        assert "poster.tex" in zf.namelist() and sum(n.endswith((".png", ".jpg")) for n in zf.namelist()) == 8
