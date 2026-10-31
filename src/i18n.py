"""Rótulos do pôster por idioma e aliases de títulos de seções."""

from __future__ import annotations

from typing import Dict, List

# Seções padrão (ordem do pôster).
DEFAULT_SECTION_IDS: List[str] = [
    "abstract",
    "introduction",
    "objectives",
    "methods",
    "results",
    "discussion",
    "conclusions",
    "references",
    "acknowledgments",
]

LABELS: Dict[str, Dict[str, str]] = {
    "pt-BR": {
        "abstract": "Resumo",
        "introduction": "Introdução",
        "objectives": "Objetivos",
        "methods": "Metodologia",
        "results": "Resultados",
        "discussion": "Discussão",
        "conclusions": "Conclusões",
        "references": "Referências",
        "acknowledgments": "Agradecimentos",
        "figure": "Figura",
        "contact": "Contato",
        "babel": "brazil",
    },
    "en-US": {
        "abstract": "Abstract",
        "introduction": "Introduction",
        "objectives": "Objectives",
        "methods": "Methods",
        "results": "Results",
        "discussion": "Discussion",
        "conclusions": "Conclusions",
        "references": "References",
        "acknowledgments": "Acknowledgments",
        "figure": "Figure",
        "contact": "Contact",
        "babel": "english",
    },
}

# Aliases (minúsculos, sem acento) usados na extração heurística.
SECTION_ALIASES: Dict[str, List[str]] = {
    "abstract": ["abstract", "resumo", "summary", "sumario executivo"],
    "introduction": ["introduction", "introducao", "background", "contexto", "motivation", "motivacao"],
    "objectives": ["objectives", "objetivos", "objective", "objetivo", "aims", "goals", "hypothesis", "hipotese"],
    "methods": [
        "methods", "methodology", "materials and methods", "materials & methods", "metodologia",
        "metodos", "material e metodos", "materiais e metodos", "experimental",
    ],
    "results": ["results", "resultados", "findings", "results and discussion", "resultados e discussao"],
    "discussion": ["discussion", "discussao", "analysis", "analise"],
    "conclusions": [
        "conclusions", "conclusion", "conclusoes", "conclusao", "final remarks",
        "consideracoes finais", "concluding remarks",
    ],
    "references": ["references", "referencias", "bibliography", "bibliografia", "referencias bibliograficas"],
    "acknowledgments": ["acknowledgments", "acknowledgements", "agradecimentos", "acknowledgment"],
}


def labels_for(lang: str) -> Dict[str, str]:
    return LABELS.get(lang, LABELS["pt-BR"])
