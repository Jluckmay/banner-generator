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

### Opção A: Executar a Versão Local em Streamlit (`app.py`)
Executa um **backend próprio e autônomo localmente**, realizando a compilação LaTeX via `pdflatex` da máquina e síntese de IA utilizando a chave de API fornecida diretamente pelo usuário (no formulário interativo ou em arquivo `.env` local):
```bash
streamlit run app.py
```
A aplicação abrirá automaticamente no navegador em `http://localhost:8501`.

### Opção B: Executar a Interface Web SPA com Servidor Local Flask (`server.py`)
Inicia o servidor backend local Flask e serve a interface SPA:
```bash
python server.py
```
Acesse a aplicação web em `http://127.0.0.1:5000`. A página HTML local conecta-se automaticamente ao backend local (`http://127.0.0.1:5000`), sem bloqueios ou dependências externas, com a interface 100% liberada e utilizável imediatamente.

### Rodar a Suíte de Testes Automatizados
```bash
python -m pytest
```

---

## 🔑 Provedores de IA
As chaves de API podem ser inseridas diretamente na interface do usuário (recomendado para uso local ou Streamlit) ou configuradas via variáveis de ambiente:
```bash
export GEMINI_API_KEY="sua-chave"
export OPENAI_API_KEY="sua-chave"
export ANTHROPIC_API_KEY="sua-chave"
export DEEPSEEK_API_KEY="sua-chave"
export NVIDIA_API_KEY="sua-chave"
```

---

## 🌐 Hospedagem, Arquitetura e Políticas de Segurança

- **Página HTML no GitHub Pages (`https://jluckmay.github.io/banner-generator/`)**:
  - Frontend SPA estático hospedado no GitHub Pages com deploy contínuo via `.github/workflows/deploy-pages.yml`.
  - **Restrição Estrita de Conexão (CSP)**: A diretiva `connect-src` autoriza conexões exclusivamente com o backend oficial Render (`https://poster-generator-nkqh.onrender.com`), cdnjs e servidores locais.
  - **Detecção Automática de Backend (`getApiBase`)**: Quando acessada a partir de `jluckmay.github.io`, a página utiliza automaticamente a conexão com o Render. Quando executada localmente (`localhost`, `127.0.0.1` ou `file:`), conecta-se ao servidor local (`http://127.0.0.1:5000`).
  - **Usabilidade Contínua (Sem Travamentos)**: A verificação de conexão com o servidor roda em segundo plano. O usuário pode alternar templates, editar dados, configurar paleta de cores e visualizar o rascunho sem nenhum atraso ou travamento enquanto a conexão é estabelecida.

- **Servidor Backend no Render (`https://poster-generator-nkqh.onrender.com`)**:
  - Container Docker provisionado via `render.yaml` com TeX Live e Gunicorn.
  - **Restrição Estrita de Origens (CORS)**: O servidor backend no Render permite conexões vindas exclusivamente do domínio `https://jluckmay.github.io` (além de origens locais para desenvolvimento). Requisições com origens não autorizadas são bloqueadas com HTTP 403 Forbidden.
  - **Tolerância a Inatividade & Cold-Start**: Mecanismo `robustFetch` com retentativas automáticas e heartbeat periódico para manter o servidor ativo durante o uso.

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

### Deployment, Architecture & Security Policies

- **GitHub Pages Frontend (`https://jluckmay.github.io/banner-generator/`)**:
  - Static SPA frontend deployed via GitHub Actions (`.github/workflows/deploy-pages.yml`).
  - **Strict CSP Connect-Src**: Content Security Policy allows network connections exclusively to the Render production server (`https://poster-generator-nkqh.onrender.com`), CDN libraries, and local development backends.
  - **Dynamic Backend Resolution**: Automatically targets the Render production server on GitHub Pages, while seamlessly routing to the local server (`http://127.0.0.1:5000`) in local environments.
  - **Zero Interface Blocking**: Background wake-up pings never block or freeze UI interactivity; template selection, color customizing, and section editing remain 100% active and responsive while the server establishes connection.

- **Render Production Backend (`https://poster-generator-nkqh.onrender.com`)**:
  - Dockerized TeX Live and Gunicorn backend configured in `render.yaml`.
  - **Strict Origin Whitelist (CORS)**: In production, the Render backend strictly permits requests coming from `https://jluckmay.github.io` (and local development hosts). Disallowed origins are rejected with HTTP 403 Forbidden.
  - **Fault Tolerance**: Automatic retries with exponential backoff (`robustFetch`) to endure Render's cold-starts, supported by keep-alive heartbeats during active sessions.
