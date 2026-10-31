# Gerador de Banners Acadêmicos / Academic Poster Generator

Gera pôsteres/banners acadêmicos em **LaTeX → PDF** (`tikzposter`), em **pt-BR** ou **en-US**.

## Recursos
1. **Dois modos**: preencher tudo manualmente **ou** enviar o trabalho (PDF, DOCX, TXT, MD, TEX) para gerar o conteúdo.
   - Com IA (Gemini, OpenAI, Claude, DeepSeek, NVIDIA NIM): resume o trabalho em formato de banner, já no idioma escolhido.
   - Sem chave/IA: extração básica por cabeçalhos (Resumo, Introdução, Metodologia…).
2. **Idioma** do banner (rótulos e texto da IA): `pt-BR` / `en-US`.
3. **Templates**: Clássico, Moderno, Minimalista, Ousado, Esmeralda e **DCC/UFMG** (60×90 cm, barras vermelhas, até 2 logos no cabeçalho e 5 no rodapé) + cor de destaque personalizada; papel A0–A3, retrato/paisagem, 1–4 colunas.
4. **Imagens/gráficos por seção** (com legenda), logotipos e QR Code de um link.
5. Seções editáveis: reordenar, remover, adicionar seções personalizadas.
6. **Ajuste automático de fonte** para o conteúdo caber no papel (aviso se mesmo assim não couber).
7. Saída: pré-visualização, PDF e `.zip` com o fonte LaTeX + imagens.

## Requisitos
- Python ≥ 3.10 e `pip install -r requirements.txt`
- `pdflatex` (TeX Live 2023+ ou MiKTeX) com `tikzposter`, `qrcode`, `babel`

## Executar
```powershell
pip install -r requirements.txt
python server.py          # http://127.0.0.1:5000
pytest
```

Chaves de API: informadas na interface (usadas só na requisição, nunca armazenadas) ou via variáveis de ambiente
`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, `NVIDIA_API_KEY`.

## Segurança
- Todo texto é escapado para LaTeX; fórmulas `$...$` só com comandos em lista permitida; `pdflatex -no-shell-escape`.
- Imagens são validadas e reencodadas com Pillow; DOCX lido com `defusedxml`; sem armazenamento (diretório temporário removido após cada requisição).

## Formato do texto das seções
Parágrafos separados por linha em branco, listas com `- ` ou `1. `, `**negrito**`, `*itálico*`, `$fórmula$`.
Em *Referências*, uma referência por linha.

---

## English
Academic poster generator (LaTeX/`tikzposter` → PDF): manual entry or upload your paper (PDF/DOCX/TXT/MD/TEX, optional AI summarisation),
pt-BR/en-US language, 5 templates, per-section image uploads with captions, logos, QR code, auto font-fit, PDF and LaTeX `.zip` export.
Run with `python server.py` (requires `pdflatex`).

