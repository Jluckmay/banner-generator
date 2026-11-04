# banner-generator — Gerador de Pôsteres & Academic Banner Compiler

Gera pôsteres e banners acadêmicos de alta resolução em **LaTeX → PDF** com suporte a múltiplos motores (`tikzposter`, `article`, `sciposter`, `a0poster`, `beamerposter`), com localização completa e consistente em **pt-BR** ("pôster") e **en-US** ("banner").

Oferece duas interfaces completas e integradas:
1. **Aplicação Web (SPA)**: HTML5 + CSS3 responsivo (mobile a desktop) + JavaScript puro, com visualizador PDF.js integrado e rascunho em tempo real, pronta para GitHub Pages e servidor backend Flask.
2. **Aplicação Local Streamlit (`app.py`)**: Interface interativa em Python puro com geração direta, upload de arquivos, chamada a modelos de IA, customização de paleta e visualização em alta resolução.

---

## 📁 Estrutura do Projeto / Project Structure

```
banner-generator/
├── .github/
│   └── workflows/
│       ├── ci.yml               # Pipeline de testes automatizados e lint no GitHub Actions
│       └── deploy-pages.yml     # Deploy contínuo do frontend estático no GitHub Pages
├── assets/                      # Identidade visual, logos e ícones
│   ├── icons/                   # Favicons em múltiplos formatos (SVG, PNG, ICO)
│   └── README.md                # Especificações de design dos assets
├── examples/                    # Payloads e exemplos de uso via API
│   ├── sample_poster.json       # Exemplo em Português (padrão 60x90 cm)
│   ├── sample_poster_en.json    # Exemplo em Inglês (padrão 60x90 cm)
│   └── README.md                # Guia de teste com cURL
├── src/                         # Núcleo da aplicação backend
│   ├── a0poster.py              # Renderizador do template UZH / LiRI (a0poster)
│   ├── article.py               # Renderizador do template Academic Red (article)
│   ├── beamer.py                # Renderizador do template TU Delft (beamerposter)
│   ├── config.py                # Dimensões (POSTER_SIZES), provedores e limites
│   ├── extractors.py            # Extração de texto de PDF, DOCX, TXT, MD e TEX
│   ├── i18n.py                  # Dicionários de localização (pt-BR / en-US)
│   ├── images.py                # Sanitização e decodificação segura de imagens
│   ├── latex.py                 # Compilação pdflatex, fit de fonte e geração zip
│   ├── llm.py                   # Integração com provedores de IA para sumarização
│   ├── poster.py                # Normalização e validação dos dados do pôster
│   ├── sciposter.py             # Renderizador do template Mostra IC (sciposter)
│   └── templates.py             # Registro e paletas dos 9 templates disponíveis
├── tests/                       # Suíte de testes automatizados (pytest)
│   ├── conftest.py              # Fixtures e cliente de teste Flask
│   └── test_poster.py           # Testes de validação, compilação e segurança
├── .dockerignore                # Arquivos ignorados no build Docker
├── .gitignore                   # Arquivos ignorados no versionamento Git
├── .nojekyll                    # Desativa processamento Jekyll no GitHub Pages
├── app.py                       # Interface local interativa em Streamlit
├── Dockerfile                   # Configuração de container Docker para Render/Cloud
├── index.html                   # Interface SPA web (HTML5 + CSS3 responsivo + JS puro)
├── pyproject.toml               # Metadados do pacote Python
├── render.yaml                  # Manifesto de deploy Infrastructure-as-Code no Render
├── requirements.txt             # Dependências do projeto
└── server.py                    # Servidor web Flask e rotas da API REST
```

---

## 🚀 Recursos Principais

1. **Dois Modos de Entrada & Síntese Inteligente**:
   - **Manual**: Preenchimento interativo de seções com pré-visualização em tempo real (Rascunho Interativo).
   - **Upload de Artigo**: Envio de arquivos acadêmicos (`.pdf`, `.docx`, `.txt`, `.md`, `.tex`).
     - *Com IA* (Google Gemini, OpenAI, Claude, DeepSeek, NVIDIA NIM): Sumariza e formata o trabalho diretamente nas seções do banner.
       - **Tabelas e Diagramas em LaTeX**: A IA estrutura automaticamente dados quantitativos em tabelas LaTeX (`tabular` / `booktabs`) na seção de Resultados e fluxogramas em TikZ (`tikzpicture`) na Metodologia, **sem inventar dados** (fidelidade estrita aos dados e etapas do trabalho original).
     - *Sem IA / Heurística*: Extração estrutural automática baseada em cabeçalhos (Resumo, Introdução, Metodologia, Resultados, etc.).

2. **9 Templates de Estilo Visual**:
   - **Clássico**: Visual tradicional acadêmico para conferências (`tikzposter`).
   - **Moderno**: Gradiente vertical e visual contemporâneo leve (`tikzposter`).
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
   - O template se adapta dinamicamente às dimensões selecionadas sem forçar distorções no design.

4. **Customização Avançada**:
   - **Paleta de Cores Hexadecimal & Seletor Dark Integrado**:
     - Controle individual das 6 cores do documento (`Destaque`, `Título`, `Autores`, `Texto`, `Legenda`, `Fundo`).
     - Campos hexadecimais explícitos (`#RRGGBB`) em fonte monospace para digitação e cópia/cola direta.
     - Seletor flutuante escuro exclusivo (*Dark Hex Popover*) com canvas 2D de saturação/brilho, slider de matiz (*hue*), ferramenta conta-gotas (*EyeDropper*) e chips de presets dos templates.
     - Suporte nativo ao modo escuro via `<meta name="color-scheme" content="dark">`.
   - **Template LaTeX Próprio (`.tex`)**: Upload e compilação direta de templates `.tex` personalizados com suporte a todos os parâmetros.

5. **Responsividade Total (Mobile a Desktop)**:
   - Layout fluido testado em viewports de 360px a 1920px+.
   - No celular/tablet, a pré-visualização conta com drawer deslizante (bottom sheet), visualizador responsivo e barra de ações flutuante.
   - Prevenção de overflow horizontal e quebras de botões em telas pequenas.

6. **Consistência de Nomenclatura e Idiomas**:
   - **Marca**: Preservada como `~/ banner-generator` em todas as interfaces.
   - **Português (`pt-BR`)**: Terminologia consistente de "pôster" (*Título do Pôster*, *Idioma do Pôster*, *Visualização do Pôster*, *Gerar Pôster*).
   - **Inglês (`en-US`)**: Terminologia consistente de "banner" (*Banner Title*, *Banner Language*, *Banner Preview*, *Generate Banner*).
   - Alternância instantânea de idioma com sincronização de rótulos, botões, placeholders e rascunho ao vivo.

7. **Elementos Acadêmicos Ricos**:
   - Upload de imagens e gráficos por seção (com legendas de figuras numeradas).
   - Logotipos em cabeçalho (até 2) e rodapé (até 5).
   - Geração automática de QR Code para links de artigos e repositórios.
   - Algoritmo de redução e ajuste de fonte automático para prevenir transbordamento de página (*Zero-Overflow*).

8. **Exportação**:
   - Visualização dupla no navegador: **Rascunho Interativo** em tempo real e visualizador **PDF.js** com zoom e navegação.
   - Download do PDF pronto para impressão de alta qualidade.
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
- Distribuição LaTeX instalada (`pdflatex` no PATH): [TeX Live](https://www.tug.org/texlive/) ou [MiKTeX](https://miktex.org/).

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

- **Servidor Oficial de Produção**: `https://banner-generator-t5p4.onrender.com`
  - **Despertar Automático & Persistência a Inatividade**: Ao carregar o frontend, uma rotina em segundo plano dispara imediatamente uma solicitação de wake-up ao servidor Render com badge interativo no cabeçalho (*Render: Conectando/Online*).
  - **Tolerância a Falhas**: Todas as requisições (`/api/extract`, `/api/generate`) possuem mecanismo de retentativas automáticas e backoff exponencial (`robustFetch`) que mantêm a operação resiliente durante o cold-start de ~30-60s do Render gratuito, além de heartbeat periódico para evitar hibernação durante o uso.
- **GitHub Pages (Frontend)**:
  - Configure em **Settings > Pages > Deploy from a branch > main / (root)** ou via **GitHub Actions** (`.github/workflows/deploy-pages.yml`).
  - O arquivo `.nojekyll` garante o carregamento de todos os assets.
  - O frontend detecta automaticamente o ambiente (`getApiBase`): conecta-se ao servidor Render padrão quando hospedado no GitHub Pages e utiliza caminhos relativos ao executar localmente.
- **Render (Backend / Docker)**:
  - Conecte o repositório ao [Render](https://dashboard.render.com).
  - O arquivo `render.yaml` provisiona o container Docker com TeX Live e Gunicorn automaticamente.
  - Endereço de produção provisionado: `https://banner-generator-t5p4.onrender.com`.

---

## 🇺🇸 English Documentation

An automated academic poster and banner generator that converts structured data or scientific papers into print-ready **LaTeX → PDF** documents, supporting multiple underlying engines (`tikzposter`, `article`, `sciposter`, `a0poster`, `beamerposter`) with full localization in **pt-BR** ("pôster") and **en-US** ("banner").

The project provides two complete interfaces:
1. **Web SPA Frontend (`index.html`)**: Responsive HTML5 + CSS3 + vanilla JavaScript application with PDF.js viewer, real-time draft rendering, and GitHub Pages compatibility.
2. **Local Desktop Streamlit App (`app.py`)**: Native Python interactive application for local generation, AI extraction, custom palette management, and instant compilation.

### Key Features

1. **Two Input Modes & AI Synthesis**:
   - **Manual Mode**: Interactive field editing with live draft preview.
   - **Paper Upload Mode**: Ingest scientific papers in `.pdf`, `.docx`, `.txt`, `.md`, or `.tex` formats.
     - *AI-Powered* (Google Gemini, OpenAI, Claude, DeepSeek, NVIDIA NIM): Automatically summarizes and structures content into designated banner sections.
       - **LaTeX Tables and Diagrams**: AI automatically formats numerical data into compact LaTeX tables (`tabular` / `booktabs`) in Results and process pipelines into TikZ flowcharts (`tikzpicture`) in Methodology, **with zero hallucination / strictly without inventing data** (pure fidelity to the explicit text and metrics).
     - *Heuristic Fallback* (Offline / No Key): Automatically extracts sections using structural academic heading patterns (Abstract, Introduction, Methods, Results, Conclusions, etc.).

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
   - Templates dynamically adjust to the chosen dimensions without forced layout constraints or visual distortion.

4. **Advanced Customization**:
   - **Hexadecimal Color Palette & Integrated Dark Popover**:
     - Dedicated control for all 6 document colors (`Accent`, `Title`, `Authors`, `Body`, `Caption`, `Background`).
     - Monospace hex input fields (`#RRGGBB`) with direct typing, pasting, and bidirectional synchronization.
     - Custom *Dark Hex Popover* with 2D saturation/brightness canvas, hue slider, eyedropper tool (*EyeDropper API*), and template preset chips.
     - Full dark theme consistency enforced with `<meta name="color-scheme" content="dark">`.
   - **Custom LaTeX Template (`.tex`)**: Upload and direct compilation of external `.tex` templates.

5. **Full Mobile & Desktop Responsiveness**:
   - Fluid responsive layout optimized from 360px mobile viewports up to 1920px+ desktop displays.
   - Mobile slide-out drawer (bottom sheet), floating action buttons, and touch-friendly controls.

6. **Consistent Naming & Localization**:
   - **Brand**: Preserved as `~/ banner-generator` across both languages.
   - **Portuguese (`pt-BR`)**: Strictly uses "pôster" (*Título do Pôster*, *Idioma do Pôster*, *Visualização do Pôster*, *Gerar Pôster*).
   - **English (`en-US`)**: Strictly uses "banner" (*Banner Title*, *Banner Language*, *Banner Preview*, *Generate Banner*).
   - Live UI language switcher with synchronized labels, placeholders, and draft fallbacks.

7. **Rich Academic Elements**:
   - Section image/figure uploads with custom numbered captions.
   - Header logos (up to 2) and footer logos (up to 5).
   - Dynamic QR code generation for repository and paper links.
   - Intelligent *Zero-Overflow* font fitting algorithm that automatically scales down point size if text overflows.

8. **Export & Previews**:
   - Real-time client-side interactive draft preview and compiled PDF.js viewer with zoom and page controls.
   - Download high-resolution print-ready PDF.
   - Download complete LaTeX source bundle (`.zip`) containing `poster.tex` and all referenced figures.

### Installation & Prerequisites

- **Python**: Version 3.10 or higher.
- **LaTeX Distribution**: `pdflatex` available in `PATH` ([TeX Live](https://www.tug.org/texlive/) or [MiKTeX](https://miktex.org/)).

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

- **Default Production Server**: `https://banner-generator-t5p4.onrender.com`
  - **Instant Server Wakeup & Spin-Down Resilience**: When loading the frontend, a non-blocking background wake-up ping triggers immediately, showing real-time connectivity status via a header badge (*Render: Waking up/Online*).
  - **Cold-Start Fault Tolerance**: All network calls (`/api/extract`, `/api/generate`) utilize automatic retries with backoff (`robustFetch`) to seamlessly endure Render's free-tier ~30-60s cold-start, paired with background keep-alive heartbeats during editing sessions.
- **GitHub Pages**: Static hosting of `index.html`. Deploy via GitHub Actions (`.github/workflows/deploy-pages.yml`) or directly from `main / (root)` branch. Automatically connects to the default Render server when hosted online, or uses local endpoints during local development.
- **Render**: Docker deployment configured in `render.yaml`. Builds with TeX Live and Gunicorn for serverless PDF generation. Pre-configured service URL: `https://banner-generator-t5p4.onrender.com`.
