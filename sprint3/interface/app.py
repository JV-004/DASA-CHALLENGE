"""
Genera AI — Interface da Sprint 3
FIAP · Enterprise Challenge DASA / Genera

Objetivo desta interface:
- transformar a prova de conceito conversacional da Sprint 2 em um produto navegável;
- exibir dashboard com riscos e ancestralidade;
- integrar resumos automáticos e simplificação de linguagem da Sprint 3;
- preservar o RAG, os guardrails e a integração OpenAI da Sprint 2;
- oferecer uma experiência responsiva para desktop e mobile.

Execução (a partir da raiz do repositório):
    streamlit run sprint3/interface/app.py
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv


# -----------------------------------------------------------------------------
# Caminhos / imports compartilhados com as Sprints anteriores
# -----------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parents[2]
JSON_DEMO = RAIZ / "dados_estruturados.json"
PASTA_UPLOADS = RAIZ / "sprint3" / "interface" / "uploads"
PASTA_UPLOADS.mkdir(parents=True, exist_ok=True)

# Mantém compatibilidade com o .env usado na Sprint 2 e permite um .env próprio.
for _env in (
    RAIZ / "sprint3" / "interface" / ".env",
    RAIZ / "sprint2" / "interface" / ".env",
):
    if _env.exists():
        load_dotenv(dotenv_path=_env, override=False)

sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "sprint2" / "interface"))
sys.path.insert(0, str(RAIZ / "sprint2" / "agente"))
sys.path.insert(0, str(RAIZ / "sprint3" / "nlp"))

try:
    from resumos_automaticos import (
        formatar_resumo_interacoes,
        gerar_resumo_interacoes,
        gerar_resumo_relatorio,
    )
except Exception:
    gerar_resumo_relatorio = None
    gerar_resumo_interacoes = None
    formatar_resumo_interacoes = None

try:
    from nlp_simplificacao import simplificar_texto
except Exception:
    simplificar_texto = None


# -----------------------------------------------------------------------------
# Configuração da página
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Genera AI — Seu DNA explicado",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Design system / CSS responsivo
# -----------------------------------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        --bg: #f6f8fb;
        --surface: #ffffff;
        --surface-soft: #f1f4f8;
        --primary: #5b4dd8;
        --primary-soft: #efedff;
        --text: #172033;
        --muted: #667085;
        --border: #e4e8ef;
        --success: #267a62;
        --success-soft: #eaf7f2;
        --attention: #9a6a17;
        --attention-soft: #fff7e7;
        --info: #3567a8;
        --info-soft: #eef5ff;
        --shadow: 0 8px 24px rgba(20, 30, 55, 0.06);
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    [data-testid="stAppViewContainer"] > .main {
        background: var(--bg);
    }

    .block-container {
        max-width: 1240px;
        padding-top: 1.6rem;
        padding-bottom: 4rem;
    }

    [data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: var(--text);
    }

    h1, h2, h3, h4, p, label {
        color: var(--text);
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 0 18px;
    }

    .brand-mark {
        width: 42px;
        height: 42px;
        border-radius: 13px;
        background: var(--primary-soft);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
    }

    .brand h2 {
        font-size: 1.15rem;
        margin: 0;
        line-height: 1.1;
    }

    .brand p {
        color: var(--muted);
        margin: 3px 0 0;
        font-size: .76rem;
    }

    .eyebrow {
        color: var(--primary);
        text-transform: uppercase;
        letter-spacing: .08em;
        font-size: .72rem;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .page-title {
        font-size: clamp(1.65rem, 3vw, 2.35rem);
        line-height: 1.12;
        font-weight: 800;
        letter-spacing: -.035em;
        margin: 0;
    }

    .page-subtitle {
        color: var(--muted);
        margin-top: 8px;
        margin-bottom: 22px;
        max-width: 760px;
        line-height: 1.55;
    }

    .disclaimer {
        background: var(--info-soft);
        border: 1px solid #d9e7fb;
        border-radius: 14px;
        padding: 12px 15px;
        color: #35577d;
        font-size: .84rem;
        line-height: 1.5;
        margin: 0 0 20px;
    }

    .metric-card,
    .content-card,
    .result-card,
    .summary-card,
    .chat-shell,
    .empty-card {
        background: var(--surface);
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        border-radius: 18px;
    }

    .metric-card {
        padding: 18px 18px 16px;
        min-height: 126px;
        margin-bottom: 10px;
    }

    .metric-label {
        color: var(--muted);
        font-size: .77rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .04em;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.05;
        margin: 8px 0 5px;
        color: var(--text);
    }

    .metric-help {
        color: var(--muted);
        font-size: .79rem;
        line-height: 1.35;
    }

    .section-title {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 12px;
        margin: 28px 0 12px;
    }

    .section-title h3 {
        margin: 0;
        font-size: 1.05rem;
    }

    .section-title span {
        color: var(--muted);
        font-size: .78rem;
    }

    .result-card {
        padding: 18px;
        min-height: 248px;
        margin-bottom: 14px;
    }

    .result-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 10px;
    }

    .result-card h4 {
        margin: 0;
        font-size: 1rem;
        line-height: 1.35;
    }

    .result-category {
        color: var(--muted);
        font-size: .75rem;
        margin: 5px 0 12px;
    }

    .risk-pill {
        display: inline-flex;
        border-radius: 999px;
        padding: 5px 9px;
        font-size: .7rem;
        font-weight: 800;
        white-space: nowrap;
    }

    .risk-high {
        background: var(--attention-soft);
        color: var(--attention);
        border: 1px solid #f2dfb7;
    }

    .risk-medium {
        background: var(--info-soft);
        color: var(--info);
        border: 1px solid #d7e5f8;
    }

    .risk-low {
        background: var(--success-soft);
        color: var(--success);
        border: 1px solid #cfeade;
    }

    .result-description {
        color: #465269;
        font-size: .86rem;
        line-height: 1.55;
        margin: 12px 0;
    }

    .result-note {
        background: var(--surface-soft);
        color: #58647a;
        padding: 10px 11px;
        border-radius: 10px;
        font-size: .76rem;
        line-height: 1.45;
    }

    .ancestry-row {
        margin-bottom: 15px;
    }

    .ancestry-meta {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 6px;
        font-size: .83rem;
    }

    .ancestry-region {
        font-weight: 700;
    }

    .ancestry-value {
        color: var(--muted);
        font-weight: 700;
    }

    .ancestry-track {
        width: 100%;
        height: 9px;
        border-radius: 999px;
        background: #e9edf3;
        overflow: hidden;
    }

    .ancestry-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #7265e8, #9a91ef);
    }

    .content-card,
    .summary-card {
        padding: 20px;
    }

    .summary-lead {
        font-size: 1rem;
        line-height: 1.6;
        color: #39445a;
        margin-bottom: 14px;
    }

    .mini-list {
        margin: 0;
        padding-left: 1.1rem;
        color: #4c5870;
        font-size: .86rem;
        line-height: 1.65;
    }

    .chat-user,
    .chat-assistant,
    .chat-blocked,
    .chat-no-context {
        padding: 14px 16px;
        border-radius: 14px;
        margin: 10px 0;
        line-height: 1.55;
        font-size: .9rem;
        border: 1px solid var(--border);
    }

    .chat-user {
        margin-left: 8%;
        background: var(--primary-soft);
        border-color: #ddd8ff;
    }

    .chat-assistant {
        margin-right: 8%;
        background: var(--surface);
    }

    .chat-blocked {
        background: var(--attention-soft);
        border-color: #f1ddb1;
    }

    .chat-no-context {
        background: var(--info-soft);
        border-color: #d8e6f8;
    }

    .chat-name {
        font-size: .75rem;
        font-weight: 800;
        color: var(--muted);
        margin-bottom: 5px;
    }

    .source-card {
        background: var(--surface-soft);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 10px 12px;
        margin: 7px 0;
        font-size: .78rem;
        line-height: 1.45;
        color: #4e596d;
    }

    .empty-card {
        padding: 34px 24px;
        text-align: center;
        color: var(--muted);
    }

    .empty-card .icon {
        font-size: 2rem;
        margin-bottom: 8px;
    }

    .privacy-note {
        color: var(--muted);
        font-size: .72rem;
        line-height: 1.45;
        border-top: 1px solid var(--border);
        margin-top: 18px;
        padding-top: 14px;
    }

    .stButton > button {
        border-radius: 11px;
        border: 1px solid var(--border);
        background: var(--surface);
        color: var(--text);
        font-weight: 650;
        min-height: 40px;
    }

    .stButton > button:hover {
        border-color: #bbb4fa;
        color: var(--primary);
        background: #faf9ff;
    }

    .stTextInput input,
    .stTextArea textarea {
        border-radius: 11px !important;
        border-color: var(--border) !important;
        background: var(--surface) !important;
        color: var(--text) !important;
    }

    div[data-baseweb="select"] > div {
        border-radius: 11px !important;
        border-color: var(--border) !important;
        background: var(--surface) !important;
    }

    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 14px;
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .metric-card {
            min-height: auto;
        }

        .result-card {
            min-height: auto;
        }

        .chat-user {
            margin-left: 2%;
        }

        .chat-assistant {
            margin-right: 2%;
        }

        .section-title {
            align-items: flex-start;
            flex-direction: column;
            gap: 4px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
