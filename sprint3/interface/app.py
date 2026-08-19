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
# -----------------------------------------------------------------------------
# Estado da sessão
# -----------------------------------------------------------------------------

VALORES_PADRAO_SESSAO = {
    "pagina": "Visão geral",
    "dados": None,
    "arquivo_relatorio": None,
    "messages": [],
    "assistente_preparado": False,
    "modo_resposta": "Paciente",
    "resumo_relatorio": None,
    "erro_relatorio": None,
}

for chave, valor in VALORES_PADRAO_SESSAO.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor


# -----------------------------------------------------------------------------
# Utilidades
# -----------------------------------------------------------------------------

def escapar(valor: Any) -> str:
    """Escapa conteúdo antes de inserir em HTML."""
    if valor is None:
        return ""
    return html.escape(str(valor))


def carregar_json(caminho: Path) -> dict[str, Any]:
    """Carrega um relatório JSON e garante que o conteúdo seja um objeto."""
    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, dict):
        raise ValueError("O relatório deve conter um objeto JSON na raiz.")

    return dados


def hash_bytes(conteudo: bytes) -> str:
    """Cria identificador curto para evitar salvar uploads duplicados."""
    return hashlib.sha256(conteudo).hexdigest()[:16]


def salvar_upload(nome: str, conteudo: bytes) -> Path:
    """
    Salva temporariamente um relatório enviado pelo usuário.

    O nome final não utiliza diretamente o nome original do arquivo,
    reduzindo problemas com caracteres especiais e colisões.
    """
    extensao = Path(nome).suffix.lower()

    if extensao != ".json":
        raise ValueError("Nesta versão, o relatório deve estar em formato JSON.")

    identificador = hash_bytes(conteudo)
    destino = PASTA_UPLOADS / f"relatorio_{identificador}.json"

    if not destino.exists():
        destino.write_bytes(conteudo)

    return destino


def obter_primeiro(dados: dict[str, Any], *chaves: str, padrao: Any = None) -> Any:
    """Retorna o primeiro campo encontrado entre várias possibilidades."""
    for chave in chaves:
        if chave in dados and dados[chave] not in (None, "", [], {}):
            return dados[chave]

    return padrao


def obter_nome_paciente(dados: dict[str, Any]) -> str:
    """
    Obtém apenas o primeiro nome para personalização da interface.

    CPF e outros identificadores não são exibidos.
    """
    paciente = dados.get("paciente", {})

    if isinstance(paciente, dict):
        nome = obter_primeiro(
            paciente,
            "nome",
            "nome_completo",
            "name",
            padrao="Paciente",
        )
    else:
        nome = "Paciente"

    primeiro_nome = str(nome).strip().split(" ")[0]

    return primeiro_nome or "Paciente"


def obter_resultados(dados: dict[str, Any]) -> list[dict[str, Any]]:
    """Normaliza a lista de resultados genéticos."""
    resultados = dados.get("resultados", [])

    if isinstance(resultados, list):
        return [item for item in resultados if isinstance(item, dict)]

    return []


def obter_ancestralidade(dados: dict[str, Any]) -> list[dict[str, Any]]:
    """Normaliza a seção de ancestralidade."""
    ancestralidade = dados.get("ancestralidade", [])

    if isinstance(ancestralidade, list):
        return [item for item in ancestralidade if isinstance(item, dict)]

    if isinstance(ancestralidade, dict):
        # Alguns formatos agrupam regiões em uma chave interna.
        for chave in ("regioes", "resultados", "composicao"):
            valor = ancestralidade.get(chave)

            if isinstance(valor, list):
                return [item for item in valor if isinstance(item, dict)]

    return []


def normalizar_risco(valor: Any) -> str:
    """
    Converte diferentes nomenclaturas de risco em três categorias visuais.

    A classificação original não é alterada no relatório.
    Ela é apenas traduzida para uma apresentação menos alarmista.
    """
    texto = str(valor or "").strip().lower()

    alto = {
        "alto",
        "alta",
        "elevado",
        "elevada",
        "high",
        "aumentado",
        "aumentada",
        "maior",
    }

    medio = {
        "medio",
        "médio",
        "media",
        "média",
        "moderado",
        "moderada",
        "medium",
        "intermediario",
        "intermediário",
        "intermediaria",
        "intermediária",
    }

    baixo = {
        "baixo",
        "baixa",
        "reduzido",
        "reduzida",
        "low",
        "menor",
    }

    if texto in alto or any(palavra in texto for palavra in alto):
        return "alto"

    if texto in medio or any(palavra in texto for palavra in medio):
        return "medio"

    if texto in baixo or any(palavra in texto for palavra in baixo):
        return "baixo"

    return "indefinido"


def obter_risco_resultado(resultado: dict[str, Any]) -> str:
    """Procura o campo de risco usado pelo relatório."""
    valor = obter_primeiro(
        resultado,
        "risco",
        "nivel_risco",
        "classificacao",
        "predisposicao",
        "risk",
        padrao="",
    )

    return normalizar_risco(valor)


def rotulo_risco(risco: str) -> str:
    """Rótulo mostrado ao paciente."""
    return {
        "alto": "Maior atenção",
        "medio": "Atenção moderada",
        "baixo": "Menor atenção",
        "indefinido": "Informativo",
    }.get(risco, "Informativo")


def classe_risco(risco: str) -> str:
    """Classe CSS correspondente ao nível visual."""
    return {
        "alto": "risk-high",
        "medio": "risk-medium",
        "baixo": "risk-low",
        "indefinido": "risk-medium",
    }.get(risco, "risk-medium")


def nome_resultado(resultado: dict[str, Any]) -> str:
    """Obtém o nome principal da condição/característica."""
    return str(
        obter_primeiro(
            resultado,
            "doenca",
            "condicao",
            "caracteristica",
            "titulo",
            "nome",
            padrao="Resultado genético",
        )
    )


def categoria_resultado(resultado: dict[str, Any]) -> str:
    return str(
        obter_primeiro(
            resultado,
            "categoria",
            "tipo",
            "grupo",
            padrao="Perfil genético",
        )
    )


def descricao_resultado(resultado: dict[str, Any]) -> str:
    """Prioriza a descrição já simplificada quando disponível."""
    return str(
        obter_primeiro(
            resultado,
            "descricao_simples",
            "explicacao_simples",
            "descricao",
            "interpretacao",
            "descricao_tecnica",
            padrao="Consulte os detalhes deste resultado no relatório.",
        )
    )


def recomendacao_resultado(resultado: dict[str, Any]) -> str:
    return str(
        obter_primeiro(
            resultado,
            "recomendacao",
            "orientacao",
            "impacto_pratico",
            padrao=(
                "Este resultado é informativo e deve ser interpretado "
                "junto ao contexto clínico e familiar."
            ),
        )
    )


def para_percentual(valor: Any) -> float:
    """
    Converte valores de ancestralidade para percentual de 0 a 100.

    Aceita tanto 35 como 0.35.
    """
    try:
        numero = float(
            str(valor)
            .replace("%", "")
            .replace(",", ".")
            .strip()
        )
    except (TypeError, ValueError):
        return 0.0

    if 0 <= numero <= 1:
        numero *= 100

    return max(0.0, min(numero, 100.0))


def dados_regiao_ancestralidade(item: dict[str, Any]) -> tuple[str, float]:
    regiao = obter_primeiro(
        item,
        "regiao",
        "origem",
        "populacao",
        "nome",
        padrao="Outra região",
    )

    percentual = obter_primeiro(
        item,
        "percentual",
        "porcentagem",
        "valor",
        "percentage",
        padrao=0,
    )

    return str(regiao), para_percentual(percentual)


def contagem_riscos(resultados: list[dict[str, Any]]) -> dict[str, int]:
    contagem = {
        "alto": 0,
        "medio": 0,
        "baixo": 0,
        "indefinido": 0,
    }

    for resultado in resultados:
        risco = obter_risco_resultado(resultado)
        contagem[risco] = contagem.get(risco, 0) + 1

    return contagem


# -----------------------------------------------------------------------------
# Componentes visuais
# -----------------------------------------------------------------------------

def cabecalho_pagina(
    eyebrow: str,
    titulo: str,
    subtitulo: str,
) -> None:
    st.markdown(
        f"""
        <div>
            <div class="eyebrow">{escapar(eyebrow)}</div>
            <h1 class="page-title">{escapar(titulo)}</h1>
            <p class="page-subtitle">{escapar(subtitulo)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def disclaimer() -> None:
    st.markdown(
        """
        <div class="disclaimer">
            <strong>Informação importante:</strong>
            esta experiência apresenta interpretações educativas baseadas
            exclusivamente no relatório genético analisado. Os resultados
            representam predisposições e características genéticas e
            <strong>não constituem diagnóstico médico</strong>.
            Para decisões relacionadas à saúde, procure um profissional qualificado.
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_metrica(
    titulo: str,
    valor: Any,
    ajuda: str,
) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{escapar(titulo)}</div>
            <div class="metric-value">{escapar(valor)}</div>
            <div class="metric-help">{escapar(ajuda)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def titulo_secao(titulo: str, complemento: str = "") -> None:
    st.markdown(
        f"""
        <div class="section-title">
            <h3>{escapar(titulo)}</h3>
            <span>{escapar(complemento)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_resultado(resultado: dict[str, Any]) -> None:
    risco = obter_risco_resultado(resultado)

    nome = nome_resultado(resultado)
    categoria = categoria_resultado(resultado)
    descricao = descricao_resultado(resultado)
    recomendacao = recomendacao_resultado(resultado)

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-top">
                <div>
                    <h4>{escapar(nome)}</h4>
                    <div class="result-category">
                        {escapar(categoria)}
                    </div>
                </div>

                <span class="risk-pill {classe_risco(risco)}">
                    {escapar(rotulo_risco(risco))}
                </span>
            </div>

            <div class="result-description">
                {escapar(descricao)}
            </div>

            <div class="result-note">
                <strong>Orientação:</strong>
                {escapar(recomendacao)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def barra_ancestralidade(
    regiao: str,
    percentual: float,
) -> None:
    st.markdown(
        f"""
        <div class="ancestry-row">
            <div class="ancestry-meta">
                <span class="ancestry-region">{escapar(regiao)}</span>
                <span class="ancestry-value">{percentual:.1f}%</span>
            </div>

            <div class="ancestry-track">
                <div
                    class="ancestry-fill"
                    style="width: {percentual:.2f}%;">
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tela_vazia(
    icone: str,
    titulo: str,
    texto: str,
) -> None:
    st.markdown(
        f"""
        <div class="empty-card">
            <div class="icon">{escapar(icone)}</div>
            <strong>{escapar(titulo)}</strong>
            <p>{escapar(texto)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Carregamento inicial do relatório
# -----------------------------------------------------------------------------

if st.session_state.dados is None:
    if JSON_DEMO.exists():
        try:
            st.session_state.dados = carregar_json(JSON_DEMO)
            st.session_state.arquivo_relatorio = str(JSON_DEMO)
            st.session_state.erro_relatorio = None
        except Exception as erro:
            st.session_state.erro_relatorio = str(erro)
    else:
        st.session_state.erro_relatorio = (
            "O arquivo dados_estruturados.json não foi encontrado na raiz "
            "do projeto."
        )
