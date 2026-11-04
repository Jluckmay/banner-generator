# Gerador de Banners Acadêmicos / Academic Poster Generator

Gera pôsteres e banners acadêmicos em **LaTeX → PDF** com suporte a múltiplos motores (`tikzposter`, `article`, `sciposter`, `a0poster`, `beamerposter`), em **pt-BR** ou **en-US**.

Oferece duas interfaces completas e integradas:
1. **Aplicação Web (SPA)**: HTML5 + CSS3 responsivo + JavaScript puro, com visualizador PDF.js integrado, pronta para GitHub Pages e servidor backend Flask.
2. **Aplicação Local Streamlit (`app.py`)**: Interface interativa em Python puro com geração direta, upload de arquivos, chamada a modelos de IA e visualização em alta resolução.

---

## 📁 Estrutura do Projeto / Project Structure

```
banner-generator/
├── assets/                  # Identidade visual, logos e ícones
│   ├── icons/               # Favicons em múltiplos formatos (SVG, PNG, ICO)
│   └── README.md            # Especificações de design dos assets
├── examples/                # Dados e exemplos de uso via API
│   ├── sample_poster.json   # Payload de exemplo para testes (padrão 60x90)
│   └── README.md            # Guia de teste com cURL
├── src/                     # Núcleo da aplicação backend
│   ├── a0poster.py          # Renderizador do template UZH / LiRI (a0poster)
│   ├── article.py           # Renderizador do template Academic Red (article)
│   ├── beamer.py            # Renderizador do template TU Delft (beamerposter)
│   ├── config.py            # Dimensões (POSTER_SIZES), provedores e limites
│   ├── extractors.py        # Extração de texto de PDF, DOCX, TXT, MD e TEX
│   ├── i18n.py              # Dicionários de localização (pt-BR / en-US)
│   ├── images.py            # Sanitização e decodificação segura de imagens
│   ├── latex.py             # Compilação pdflatex, fit de fonte e geração zip
│   ├── llm.py               # Integração com provedores de IA para sumarização
│   ├── poster.py            # Normalização e validação dos dados do pôster
│   ├── sciposter.py         # Renderizador do template Mostra IC (sciposter)
│   └── templates.py         # Registro e paletas dos 9 templates disponíveis
├── tests/                   # Suíte de testes automatizados (pytest)
│   ├── conftest.py          # Fixtures e cliente de teste Flask
│   └── test_poster.py       # Testes de validação, compilação e segurança
├── .nojekyll                # Desativa processamento Jekyll no GitHub Pages
├── app.py                   # Interface local interativa em Streamlit
├── Dockerfile               # Configuração de container Docker para Render/Cloud
├── index.html               # Interface SPA web (HTML5 + CSS3 + JS puro)
├── pyproject.toml           # Metadados do pacote Python
├── render.yaml              # Manifesto de deploy Infrastructure-as-Code no Render
├── requirements.txt         # Dependências do projeto
└── server.py                # Servidor web Flask e rotas da API REST
```

---

## 🚀 Recursos Principais

1. **Dois Modos de Entrada**:
   - **Manual**: Preenchimento interativo com pré-visualização em tempo real (Draft Preview).
   - **Upload de Artigo**: Envio de arquivos acadêmicos (`.pdf`, `.docx`, `.txt`, `.md`, `.tex`).
     - *Com IA* (Gemini, OpenAI, Claude, DeepSeek, NVIDIA NIM): Sumariza e formata o trabalho diretamente nas seções do banner.
     - *Sem IA*: Extração estrutural automática baseada em cabeçalhos (Resumo, Introdução, Metodologia, etc.).

2. **9 Templates de Estilo Visual**:
   - **Clássico**: Visual tradicional acadêmico para conferências (`tikzposter`).
   - **Moderno**: Gradiente vertical e visual corporativo leve (`tikzposter`).
   - **Minimalista**: Estilo editorial neutro e limpo (`tikzposter`).
   - **Ousado**: Blocos envolventes com cores quentes (`tikzposter`).
   - **Ondas Esmeralda**: Acabamento com curvas e tons esmeralda (`tikzposter`).
   - **Academic Red**: Barras de contraste superior/inferior, suporte a até 5 logos de rodapé (`article`).
   - **Mostra IC**: Estilo científico com caixas de destaque (`sciposter`).
   - **UZH / LiRI**: Layout institucional suíço com tipografia sóbria (`a0poster`).
   - **TU Delft**: Estrutura modular em colunas com base em Beamer (`beamerposter`).

3. **Dimensões e Adaptação Universal**:
   - Dimensões disponíveis: **60 × 90 cm** (Padrão), **90 × 120 cm**, **A0** (84.1 × 118.9 cm), **A1** (59.4 × 84.1 cm), **A2** (42.0 × 59.4 cm).
   - Orientações: **Retrato** (Portrait) e **Paisagem** (Landscape).
   - O template se adapta dinamicamente às dimensões selecionadas sem alterar o estilo visual.

4. **Elementos Ricos**:
   - Upload de imagens e gráficos por seção (com suporte a legendas de figuras).
   - Logotipos em cabeçalho (até 2) e rodapé (até 5).
   - Geração automática de QR Code para links de artigos e repositórios.
   - Algoritmo de redução e ajuste de fonte automático para prevenir transbordamento de página (*Zero-Overflow*).

5. **Exportação**:
   - Pré-visualização instantânea no navegador via PDF.js ou renderizador de imagem.
   - Download do PDF pronto para impressão de alta resolução.
   - Download de arquivo `.zip` contendo o código-fonte LaTeX (`poster.tex`) e todas as imagens/figuras incluídas.

---

## 🔒 Segurança

- **Isolamento de LaTeX**: Execução estrita com `pdflatex -no-shell-escape` e tempo limite configurado (`LATEX_TIMEOUT_S = 150`).
- **Sanitização de Fórmulas Matemáticas**: Expressões matemáticas `$...$` validadas contra lista de comandos permitidos.
- **Zero-Storage**: Todo processamento é efetuado em diretórios efêmeros (`tempfile.mkdtemp`), completamente removidos após a resposta.
- **Prevenção de Ataques XML**: Documentos DOCX processados através de `defusedxml`.
- **Higiene de Imagens**: Arquivos enviados são revalidados e decodificados com o Pillow antes de qualquer inclusão no documento.
- **Segurança Web**: Cabeçalhos Content-Security-Policy (CSP) estritos, escape contra XSS e liberação explícita de memória em `URL.revokeObjectURL`.

---

## 🛠️ Instalação e Execução

### Pré-requisitos
- Python ≥ 3.10
- Distribuição LaTeX instalada (`pdflatex` no PATH): [TeX Live](https://www.tug.org/texlive/) ou [MiKTeX].

```bash
# 1. Clonar o repositório
git clone https://github.com/Jluckmay/banner-generator.git
cd banner-generator

# 2. Instalar dependências
pip install -r requirements.txt
```

### Opção A: Executar a Versão Local em Streamlit
Uma interface gráfica rica em Python nativo com suporte a upload, IA e renderização local:
```bash
streamlit run app.py
```
A aplicação abrirá automaticamente no navegador em `http://localhost:8501`.

### Opção B: Executar o Servidor Web Flask + Interface SPA
```bash
python server.py
```
Acesse a aplicação web em `http://127.0.0.1:5000`.

### Rodar a Suíte de Testes Automatizados
```bash
python -m pytest
```

---

## 🔑 Provedores de IA (Opcional)
As chaves de API podem ser inseridas diretamente na interface do usuário ou carregadas via variáveis de ambiente:
```bash
export GEMINI_API_KEY="sua-chave"
export OPENAI_API_KEY="sua-chave"
export ANTHROPIC_API_KEY="sua-chave"
export DEEPSEEK_API_KEY="sua-chave"
export NVIDIA_API_KEY="sua-chave"
```

---

## 🌐 Hospedagem e Publicação

- **GitHub Pages (Frontend)**:
  - Configure em **Settings > Pages > Deploy from a branch > main / (root)** ou via **GitHub Actions** (`.github/workflows/deploy-pages.yml`).
  - O arquivo `.nojekyll` garante o carregamento de todos os assets.
- **Render (Backend / Docker)**:
  - Conecte o repositório ao [Render](https://dashboard.render.com).
  - O arquivo `render.yaml` provisiona o container Docker com TeX Live e Gunicorn automaticamente.
  - No frontend do GitHub Pages, aponte a URL do Render no campo de configuração da API.

---

## 🇺🇸 English Documentation

An automated academic poster and banner generator that converts structured data or scientific papers into print-ready **LaTeX → PDF** posters, supporting multiple underlying engines (`tikzposter`, `article`, `sciposter`, `a0poster`, `beamerposter`) with full **pt-BR** and **en-US** localization.

### Key Features

1. **Two Input Modes**:
   - **Manual Mode**: Interactive field editing with live draft preview.
   - **Paper Upload Mode**: Ingest papers in `.pdf`, `.docx`, `.txt`, `.md`, or `.tex` formats.
     - *AI-Powered* (Google Gemini, OpenAI, Claude, DeepSeek, NVIDIA NIM): Automatically summarizes and structures content into designated poster sections.
     - *Heuristic Fallback* (Offline / No Key): Extracts sections based on academic heading patterns (Abstract, Introduction, Methods, Results, etc.).

2. **9 Visual Style Templates**:
   - **Classic**: Traditional academic conference format (`tikzposter`).
   - **Modern**: Clean vertical gradient and contemporary typography (`tikzposter`).
   - **Minimal**: Editorial, minimalist layout with high contrast (`tikzposter`).
   - **Bold**: High-contrast warm blocks (`tikzposter`).
   - **Emerald Waves**: Curved accents in emerald tones (`tikzposter`).
   - **Academic Red**: Contrasting header/footer accent bars with up to 5 footer logos (`article`).
   - **Mostra IC**: Scientific symposium layout with callout boxes (`sciposter`).
   - **UZH / LiRI**: Swiss academic institutional typography (`a0poster`).
   - **TU Delft**: Modular column layout based on Beamer (`beamerposter`).

3. **Decoupled Universal Dimensions**:
   - Supported dimensions: **60 × 90 cm** (Default), **90 × 120 cm**, **A0** (84.1 × 118.9 cm), **A1** (59.4 × 84.1 cm), **A2** (42.0 × 59.4 cm).
   - Orientations: **Portrait** (Vertical) and **Landscape** (Horizontal).
   - Templates dynamically adjust to the chosen size without forced layout constraints.

4. **Rich Academic Elements**:
   - Section image/figure uploads with custom figure captions.
   - Header logos (up to 2) and footer logos (up to 5).
   - Dynamic QR code generation for repository and paper links.
   - Intelligent *Zero-Overflow* font fitting algorithm that automatically scales down point size if text overflows.

5. **Export & Previews**:
   - Real-time client-side draft preview and compiled PDF.js viewer.
   - Download high-resolution print-ready PDF.
   - Download complete LaTeX source bundle (`.zip`) containing `poster.tex` and all referenced figures.

### Installation & Prerequisites

- **Python**: Version 3.10 or higher.
- **LaTeX Distribution**: `pdflatex` available in `PATH` ([TeX Live 2023+] or [MiKTeX]).

```bash
git clone https://github.com/Jluckmay/banner-generator.git
cd banner-generator
pip install -r requirements.txt
```

### Running Locally

#### 1. Local Streamlit Application (`app.py`)
Run the native Python desktop interface:
```bash
streamlit run app.py
```
Opens in your default browser at `http://localhost:8501`.

#### 2. Flask REST Server + Web SPA (`server.py`)
Run the Flask API backend and serve the static SPA:
```bash
python server.py
```
Available at `http://127.0.0.1:5000`.

#### 3. Automated Test Suite
```bash
python -m pytest
```

### Environment Variables (Optional AI Providers)
API keys can be supplied directly in the UI or exported as environment variables:
```bash
export GEMINI_API_KEY="your-api-key"
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
export DEEPSEEK_API_KEY="your-api-key"
export NVIDIA_API_KEY="your-api-key"
```

### Deployment

- **GitHub Pages**: Static hosting of `index.html`. Deploy via GitHub Actions (`.github/workflows/deploy-pages.yml`) or directly from `main / (root)` branch.
- **Render**: Docker deployment configured in `render.yaml`. Builds with TeX Live and Gunicorn for serverless PDF generation. Connect the deployed Render URL inside the web interface's API configuration field.
