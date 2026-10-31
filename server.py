"""Servidor Flask: API de extração e geração de pôsteres + interface web."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Tuple

from flask import Flask, Response, jsonify, request, send_from_directory

from src import config
from src.extractors import ALLOWED_DOC_EXT, extract_text, heuristic_parse
from src.i18n import DEFAULT_SECTION_IDS, LABELS
from src.images import save_image
from src.latex import build_tex, fit_compile, make_zip, new_build_dir
from src.llm import LLMError, ai_extract, resolve_key
from src.poster import normalize_poster
from src.templates import public_templates

ROOT = Path(__file__).parent.resolve()
app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_BYTES


def _err(msg: str, code: int = 400) -> Tuple[Response, int]:
    return jsonify({"error": msg}), code


@app.after_request
def _headers(resp: Response) -> Response:
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.get("/")
def index() -> Response:
    return send_from_directory(ROOT / "web", "index.html")


@app.get("/assets/<path:name>")
def assets(name: str) -> Response:
    return send_from_directory(ROOT / "assets", name)


@app.get("/healthz")
def healthz() -> Response:
    return jsonify({"status": "ok", "pdflatex": bool(shutil.which("pdflatex"))})


@app.get("/api/config")
def api_config() -> Response:
    return jsonify(
        {
            "languages": list(config.LANGUAGES),
            "papers": list(config.PAPER_SIZES),
            "templates": public_templates(),
            "providers": config.public_provider_info(),
            "sections": DEFAULT_SECTION_IDS,
            "labels": {lang: {k: v for k, v in d.items() if k != "babel"} for lang, d in LABELS.items()},
            "doc_extensions": list(ALLOWED_DOC_EXT),
        }
    )


@app.post("/api/extract")
def api_extract() -> Tuple[Response, int] | Response:
    """Recebe um trabalho (PDF/DOCX/TXT/MD/TEX) e devolve os campos do pôster."""
    f = request.files.get("file")
    if not f or not f.filename:
        return _err("Nenhum arquivo enviado.")
    language = request.form.get("language", config.DEFAULT_LANGUAGE)
    mode = request.form.get("mode", "ai")
    try:
        text = extract_text(f.filename, f.read())
    except ValueError as exc:
        return _err(str(exc))
    except Exception:
        return _err("Não foi possível ler o arquivo.")
    if len(text) < 80:
        return _err("O arquivo não contém texto suficiente.")

    warning = ""
    result: Dict[str, Any] | None = None
    if mode == "ai":
        provider = request.form.get("provider", "google")
        try:
            key = resolve_key(provider, request.form.get("api_key"))
            result = ai_extract(text, language, provider, key, request.form.get("model") or None)
        except LLMError as exc:
            warning = str(exc)
    if result is None:
        result = heuristic_parse(text)
        if mode == "ai":
            warning = (warning + " — ").lstrip(" —") + "usando extração básica (sem IA)."
    return jsonify({"poster": result, "mode": "ai" if not warning and mode == "ai" else "basic", "warning": warning})


@app.post("/api/generate")
def api_generate() -> Tuple[Response, int] | Response:
    """Gera o pôster. Campo `data` (JSON) + arquivos de imagem referenciados por nome de campo."""
    try:
        data = json.loads(request.form.get("data", ""))
        if not isinstance(data, dict):
            raise ValueError
    except ValueError:
        return _err("Dados do pôster inválidos.")
    fmt = request.args.get("format", "pdf")
    if fmt not in ("pdf", "zip", "tex"):
        return _err("Formato inválido.")

    poster = normalize_poster(data)
    if not poster["title"]:
        return _err("Informe o título do pôster.")
    if not poster["sections"]:
        return _err("Adicione conteúdo em pelo menos uma seção.")

    wanted = [i["path"] for s in poster["sections"] for i in s["images"]] + poster["logos_header"] + poster["logos_footer"]
    if len(wanted) > config.MAX_IMAGES_TOTAL:
        return _err("Imagens demais.")

    build = new_build_dir()
    try:
        images: Dict[str, str] = {}
        for n, field in enumerate(dict.fromkeys(wanted)):
            up = request.files.get(field)
            if not up:
                continue
            try:
                images[field] = save_image(up.read(), build, f"img{n}")
            except ValueError as exc:
                return _err(f"{up.filename or field}: {exc}")
        tex = build_tex(poster, images)
        if fmt == "tex":
            return Response(tex, mimetype="text/plain", headers={"Content-Disposition": 'attachment; filename="poster.tex"'})
        try:
            pdf, tex, overflow = fit_compile(poster, images, build)
        except RuntimeError as exc:
            return _err(str(exc), 500)
        except Exception:
            return _err("Tempo esgotado ou erro ao compilar o pôster.", 500)
        extra = {"X-Poster-Overflow": "1"} if overflow else {}
        if fmt == "zip":
            return Response(make_zip(tex, build), mimetype="application/zip", headers={"Content-Disposition": 'attachment; filename="poster-latex.zip"', **extra})
        return Response(pdf, mimetype="application/pdf", headers={"Content-Disposition": 'inline; filename="poster.pdf"', **extra})
    finally:
        shutil.rmtree(build, ignore_errors=True)


@app.errorhandler(413)
def too_large(_: Exception) -> Tuple[Response, int]:
    return _err("Upload maior que o limite permitido.", 413)


def main() -> None:
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")))


if __name__ == "__main__":
    main()
