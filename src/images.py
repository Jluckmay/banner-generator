"""Validação e reencode de imagens enviadas (remove metadados e conteúdo inesperado)."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

from .config import MAX_IMAGE_BYTES

Image.MAX_IMAGE_PIXELS = 80_000_000
MAX_DIM = 3600
ALLOWED = {"PNG", "JPEG", "GIF", "BMP", "WEBP", "TIFF"}


def save_image(raw: bytes, dest_dir: Path, stem: str) -> str:
    """Reencoda para PNG/JPEG em `dest_dir` e retorna o nome do arquivo gerado."""
    if len(raw) > MAX_IMAGE_BYTES:
        raise ValueError("Imagem maior que o limite permitido.")
    try:
        probe = Image.open(io.BytesIO(raw))
        if probe.format not in ALLOWED:
            raise ValueError("Formato de imagem não suportado.")
        img = Image.open(io.BytesIO(raw))
        img.load()
    except ValueError:
        raise
    except Exception:
        raise ValueError("Arquivo de imagem inválido.") from None
    img.thumbnail((MAX_DIM, MAX_DIM))
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        name, fmt, kw = f"{stem}.png", "PNG", {}
    else:
        img = img.convert("RGB")
        name, fmt, kw = f"{stem}.jpg", "JPEG", {"quality": 90}
    img.save(dest_dir / name, fmt, **kw)
    return name
