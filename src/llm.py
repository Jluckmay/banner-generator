"""Cliente multi-provedor para transformar o texto de um trabalho em conteúdo de pôster."""

from __future__ import annotations

import json
import re
from typing import Any, Dict

import requests

from .config import PROVIDERS, server_key_for
from .i18n import DEFAULT_SECTION_IDS

TIMEOUT_S = 120

_LANG_NAME = {"pt-BR": "Brazilian Portuguese", "en-US": "American English"}

SYSTEM_PROMPT = """You are an expert academic researcher and designer converting academic papers into structured, high-impact content for a scientific poster.
Return ONLY a valid JSON object, no markdown fences, with this exact shape:
{"title": str, "authors": str, "affiliations": str (one per line), "email": str,
 "sections": {"abstract": str, "introduction": str, "objectives": str, "methods": str,
              "results": str, "discussion": str, "conclusions": str,
              "references": str, "acknowledgments": str}}

CRITICAL MANDATORY RULES:

1. TARGET LANGUAGE & TRANSLATION (ABSOLUTE REQUIREMENT):
   - Target Language: {language}.
   - ALL content without exception (title, abstract, introduction, objectives, methods, results, discussion, conclusions, table headers, bullet points, captions) MUST be written strictly in {language}.
   - If the source paper is written in English (or any other language) and the target language is Brazilian Portuguese, you MUST TRANSLATE and synthesize ALL sections into clear, fluent, academic Brazilian Portuguese (PT-BR).
   - NEVER leave English sentences, paragraphs, or table headers in a Brazilian Portuguese poster (except universal acronyms such as IoT, AI, F1, 2PL, LSTM, CUDA, etc.).

2. TABLES, DIAGRAMS & CHARTS (DATA VISUALIZATION):
   - In "results" (and/or "discussion"): If the paper contains quantitative benchmarks, metrics, experimental data, accuracy/F1 comparisons, or model evaluations, YOU MUST synthesize them into a clean, compact LaTeX table using the tabular environment:
     \\begin{center}
     \\small
     \\begin{tabular}{|l|c|c|}
     \\hline
     \\textbf{Modelo / Método} & \\textbf{Macro F1} & \\textbf{Calibração IRT} \\\\
     \\hline
     Random Forest & 0.965 & Alta \\\\
     Transformer & 0.892 & Moderada \\\\
     LSTM & 0.824 & Estável \\\\
     Regressão Logística & 0.731 & Baseline \\\\
     \\hline
     \\end{tabular}
     \\end{center}
     (You may also use Markdown table syntax `| Col1 | Col2 |`). DO NOT bury quantitative results inside a long block of text. Readers MUST see data visualized in a table or chart!
   - In "methods": If the paper presents a multi-stage architecture, pipeline, algorithm, or methodology, synthesize it into a clean, compact TikZ flowchart (\\begin{tikzpicture}...\\end{tikzpicture}) or a structured sequence with boxes and arrows.

3. TEXT FORMATTING & VISUAL SCANNABILITY (NO MONOLITHIC PARAGRAPHS):
   - Academic posters are read from 1 to 2 meters away. NEVER output monolithic walls of text.
   - Format each section using concise, structured bullet points (lines starting with "- ").
   - Use bold lead-ins for key points:
     - **Contexto:** ...
     - **Problema & Lacuna:** ...
     - **Metodologia Proposta:** ...
     - **Principais Achados:** ...
   - Highlight key metrics, numbers, models, and findings in **bold** (e.g. **Macro F1 de 0.965**, **Random Forest**, **6.561.840 respostas**).

4. REFERENCES FILTERING (MAX 3 TO 4 KEY REFERENCES):
   - Scientific posters have strictly limited space. Include ONLY the 3 to 4 most relevant references cited in the paper (e.g. seminal papers, key datasets like CICIoT2023 / Edge-IIoTset).
   - NEVER dump the paper's full bibliography!
   - Format each reference in a single compact line: "[1] Author, A. et al. (Year). Short Title. Conference/Journal."

5. SECTION BALANCING & LENGTH EQUILIBRIUM:
   - Ensure sections are well-balanced in length (approx. 70 to 120 words each, plus any table/diagram) so poster columns are visually harmonious and balanced.
   - If a section like "objectives" or "discussion" is already covered in "introduction" or "results", return "" for it so space is reserved for the primary sections.

6. ABSOLUTE TRUTHFULNESS ("SEM INVENTAR DADOS"):
   - Be strictly faithful to the source paper. NEVER invent, hallucinate, or fabricate facts, metrics, or numbers not present in the paper.
   - Fix broken syllable line-breaks from PDF extraction (e.g., "proper- ties" -> "properties", "differ- ences" -> "differences").
7. Title & Metadata Isolation: "title" must ONLY contain the title of the paper. Keep authors, affiliations and emails strictly separated in their dedicated fields."""


class LLMError(RuntimeError):
    pass


def resolve_key(provider: str, user_key: str | None) -> str:
    key = (user_key or "").strip() or server_key_for(provider)
    if not key:
        raise LLMError("Chave de API ausente para o provedor selecionado.")
    return key


def chat(provider: str, api_key: str, model: str | None, system: str, user: str) -> str:
    cfg = PROVIDERS.get(provider)
    if not cfg:
        raise LLMError("Provedor desconhecido.")
    model = model or cfg["default_model"]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,79}", model) or ".." in model or model.startswith("/") or (provider == "google" and "/" in model):
        raise LLMError("Nome de modelo inválido.")
    try:
        if provider == "google":
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={"x-goog-api-key": api_key},
                json={
                    "systemInstruction": {"parts": [{"text": system}]},
                    "contents": [{"role": "user", "parts": [{"text": user}]}],
                    "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
                },
                timeout=TIMEOUT_S,
            )
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        if provider == "anthropic":
            r = requests.post(
                cfg["url"],
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                json={
                    "model": model, "max_tokens": 4096, "temperature": 0.2, "system": system,
                    "messages": [{"role": "user", "content": user}],
                },
                timeout=TIMEOUT_S,
            )
            r.raise_for_status()
            return r.json()["content"][0]["text"]
        # Provedores OpenAI / NVIDIA / DeepSeek com fallback resiliente de modelos para NVIDIA NIM
        models_to_try = [model]
        if provider == "nvidia":
            for fb in ("nvidia/nemotron-3.5-super-vl-120b-a12b", "meta/llama-3.1-70b-instruct", "meta/llama-3.1-8b-instruct", "meta/llama-3.3-70b-instruct"):
                if fb not in models_to_try:
                    models_to_try.append(fb)

        last_exc: Exception | None = None
        for m_name in models_to_try:
            try:
                r = requests.post(
                    cfg["url"],
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": m_name, "temperature": 0.2, "max_tokens": 4096,
                        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                    },
                    timeout=TIMEOUT_S,
                )
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"]
            except requests.HTTPError as exc:
                last_exc = exc
                if exc.response.status_code in (404, 410) and len(models_to_try) > 1:
                    continue
                raise
        if last_exc:
            raise last_exc
        raise LLMError("Nenhum modelo disponível para o provedor.")
    except requests.HTTPError as exc:  # nunca expõe cabeçalhos/chave
        raise LLMError(f"Provedor retornou HTTP {exc.response.status_code}.") from None
    except (requests.RequestException, KeyError, IndexError, ValueError):
        raise LLMError("Falha ao consultar o provedor de IA.") from None


def parse_json_object(raw: str) -> Dict[str, Any]:
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        raise LLMError("Resposta da IA não contém JSON válido.")
    snippet = raw[start : end + 1]
    try:
        obj = json.loads(snippet)
    except json.JSONDecodeError:
        # Repara escapes de contrabarra do LaTeX em strings JSON (ex: \begin, \hline, \alpha)
        repaired = re.sub(r'\\(?![/"\\bfnrtu]|u[0-9a-fA-F]{4})', r'\\\\', snippet)
        try:
            obj = json.loads(repaired)
        except json.JSONDecodeError:
            raise LLMError("Resposta da IA não contém JSON válido.") from None
    if not isinstance(obj, dict):
        raise LLMError("Resposta da IA inválida.")
    return obj


def ai_extract(text: str, language: str, provider: str, api_key: str, model: str | None) -> Dict[str, Any]:
    system = SYSTEM_PROMPT.replace("{language}", _LANG_NAME.get(language, "Brazilian Portuguese"))
    obj = parse_json_object(chat(provider, api_key, model, system, f"<paper>\n{text[:60000]}\n</paper>"))
    secs = obj.get("sections") if isinstance(obj.get("sections"), dict) else {}
    return {
        "title": obj.get("title") or "",
        "authors": obj.get("authors") or "",
        "affiliations": obj.get("affiliations") or "",
        "email": obj.get("email") or "",
        "sections": [{"id": sid, "content": secs.get(sid) or ""} for sid in DEFAULT_SECTION_IDS],
    }
