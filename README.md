# Gerador de Banners Acadêmicos / Academic Poster Generator

Gera pôsteres e banners acadêmicos em **LaTeX → PDF** com suporte a múltiplos motores (`tikzposter`, `article`, `sciposter`, `a0poster`, `beamerposter`), em **pt-BR** ou **en-US**.

---

## 📁 Estrutura do Projeto

```
banner-generator/
├── assets/                  # Identidade visual, logos e ícones
│   ├── icons/               # Favicons em múltiplos formatos (SVG, PNG, ICO)
│   └── README.md            # Especificações de design dos assets
├── examples/                # Dados e exemplos de uso via API
│   ├── sample_poster.json   # Payload de exemplo para testes
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
├── web/                     # Frontend da aplicação
│   └── index.html           # Interface SPA completa (HTML5 + CSS3 + JS puro)
├── Dockerfile               # Configuração de container Docker
├── pyproject.toml           # Metadados do pacote Python
├── requirements.txt         # Dependências do projeto
└── server.py                # Servidor web Flask e rotas da API
```

---

## 🚀 Recursos

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
   - Dimensões disponíveis: **A0** (84.1 × 118.9 cm), **60 × 90 cm**, **90 × 120 cm**, **A1** (59.4 × 84.1 cm), **A2** (42.0 × 59.4 cm).
   - Orientações: **Retrato** (Portrait) e **Paisagem** (Landscape).
   - O template se adapta dinamicamente às dimensões selecionadas sem forçar troca de papel.

4. **Elementos Ricos**:
   - Upload de imagens e gráficos por seção (com suporte a legendas).
   - Logotipos em cabeçalho e rodapé.
   - Geração automática de QR Code para links de artigos e repositórios.
   - Algoritmo de redução e ajuste de fonte automático para prevenir transbordamento de página (*Zero-Overflow*).

5. **Exportação**:
   - Pré-visualização instantânea no navegador via PDF.js.
   - Download do PDF pronto para impressão de alta resolução.
   - Download de arquivo `.zip` contendo o código-fonte LaTeX (`poster.tex`) e todas as imagens/figuras incluídas.

---

## 🔒 Segurança

- **Isolamento de LaTeX**: Execução estrita com `pdflatex -no-shell-escape` e tempo limite configurado (`LATEX_TIMEOUT_S = 150`).
- **Sanitização de Fórmulas Matemáticas**: Expressões matemáticas `$...$` validadas contra lista de comandos permitidos.
- **Zero-Storage**: Todo processamento é efetuado em diretórios efêmeros (`tempfile.mkdtemp`), completamente removidos após a resposta HTTP.
- **Prevenção de Ataques XML**: Documentos DOCX processados através de `defusedxml`.
- **Higiene de Imagens**: Arquivos enviados são revalidados e decodificados com o Pillow antes de qualquer inclusão no documento.
- **Segurança Web**: Cabeçalhos Content-Security-Policy (CSP) estritos, escape contra XSS e liberação explícita de memória em `URL.revokeObjectURL`.

---

## 🛠️ Instalação e Execução

### Pré-requisitos
- Python ≥ 3.10
- Distribuição LaTeX instalada (`pdflatex` no PATH): [TeX Live](https://www.tug.org/texlive/) ou [MiKTeX].

### Executando Localmente
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar servidor
python server.py
# Acesso disponível em http://127.0.0.1:5000

# 3. Rodar suíte de testes
python -m pytest
```

### Variáveis de Ambiente Opcionais (Provedores de IA)
As chaves podem ser inseridas na própria interface ou configuradas via variáveis de ambiente:
```bash
export GEMINI_API_KEY="sua-chave"
export OPENAI_API_KEY="sua-chave"
export ANTHROPIC_API_KEY="sua-chave"
export DEEPSEEK_API_KEY="sua-chave"
export NVIDIA_API_KEY="sua-chave"
```

---

## English Summary

Academic poster generator producing print-ready LaTeX PDFs with multi-engine support (`tikzposter`, `article`, `sciposter`, `a0poster`, `beamerposter`). Supports manual editing or paper uploads (PDF, DOCX, TXT, MD, TEX) with optional AI summarization. Features 9 templates, decoupled adaptable dimensions (A0, 60×90, 90×120, A1, A2), automatic font fitting, image uploads, QR codes, and full LaTeX source `.zip` export.
