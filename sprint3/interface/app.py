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

    html_card = (
        f'<div class="result-card">'
        f'<div class="result-top">'
        f'<div>'
        f'<h4>{escapar(nome)}</h4>'
        f'<div class="result-category">{escapar(categoria)}</div>'
        f'</div>'
        f'<span class="risk-pill {classe_risco(risco)}">'
        f'{escapar(rotulo_risco(risco))}'
        f'</span>'
        f'</div>'
        f'<div class="result-description">{escapar(descricao)}</div>'
        f'<div class="result-note">'
        f'<strong>Orientação:</strong> {escapar(recomendacao)}'
        f'</div>'
        f'</div>'
    )

    st.html(html_card)


def barra_ancestralidade(
    regiao: str,
    percentual: float,
) -> None:
    html_barra = (
        f'<div class="ancestry-row">'
        f'<div class="ancestry-meta">'
        f'<span class="ancestry-region">{escapar(regiao)}</span>'
        f'<span class="ancestry-value">{percentual:.1f}%</span>'
        f'</div>'
        f'<div class="ancestry-track">'
        f'<div class="ancestry-fill" style="width: {percentual:.2f}%;"></div>'
        f'</div>'
        f'</div>'
    )

    st.html(html_barra)


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
# -----------------------------------------------------------------------------
# Sidebar / navegação
# -----------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">🧬</div>
            <div>
                <h2>Genera AI</h2>
                <p>Seu DNA explicado com clareza</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    paginas = [
        "Visão geral",
        "Meus resultados",
        "Assistente",
        "Histórico",
    ]

    pagina_escolhida = st.radio(
        "Navegação",
        paginas,
        index=paginas.index(st.session_state.pagina)
        if st.session_state.pagina in paginas
        else 0,
        label_visibility="collapsed",
    )

    st.session_state.pagina = pagina_escolhida

    st.markdown("---")

    st.caption("Relatório")

    upload = st.file_uploader(
        "Enviar outro relatório",
        type=["json"],
        accept_multiple_files=False,
        help="Envie um relatório estruturado em JSON.",
    )

    if upload is not None:
        try:
            conteudo = upload.getvalue()
            caminho_upload = salvar_upload(upload.name, conteudo)

            dados_upload = carregar_json(caminho_upload)

            st.session_state.dados = dados_upload
            st.session_state.arquivo_relatorio = str(caminho_upload)
            st.session_state.resumo_relatorio = None
            st.session_state.messages = []
            st.session_state.assistente_preparado = False
            st.session_state.erro_relatorio = None

            st.success("Relatório carregado.")
        except Exception as erro:
            st.session_state.erro_relatorio = str(erro)
            st.error(f"Não foi possível carregar o relatório: {erro}")

    if st.session_state.arquivo_relatorio:
        st.caption(
            f"Arquivo ativo: {Path(st.session_state.arquivo_relatorio).name}"
        )

    st.markdown("---")

    st.caption("Assistente")

    chave_atual = os.getenv("OPENAI_API_KEY", "")

    chave_digitada = st.text_input(
        "OpenAI API Key",
        value="",
        type="password",
        placeholder="sk-...",
        help=(
            "A chave é utilizada apenas durante esta sessão. "
            "Não publique a chave no GitHub."
        ),
    )

    if chave_digitada.strip():
        os.environ["OPENAI_API_KEY"] = chave_digitada.strip()
        chave_atual = chave_digitada.strip()

    st.session_state.modo_resposta = st.selectbox(
        "Modo de resposta",
        ["Paciente", "Técnico"],
        index=0
        if st.session_state.modo_resposta == "Paciente"
        else 1,
        help=(
            "Paciente prioriza linguagem acessível. "
            "Técnico preserva uma explicação mais detalhada."
        ),
    )

    preparar = st.button(
        "Preparar assistente",
        use_container_width=True,
    )

    if preparar:
        if not st.session_state.arquivo_relatorio:
            st.warning("Carregue um relatório antes de preparar o assistente.")
        else:
            try:
                with st.spinner("Preparando busca semântica..."):
                    pipeline_script = (
                        RAIZ
                        / "sprint2"
                        / "pipeline"
                        / "pipeline_completo.py"
                    )

                    if pipeline_script.exists():
                        resultado = subprocess.run(
                            [
                                sys.executable,
                                str(pipeline_script),
                                st.session_state.arquivo_relatorio,
                            ],
                            cwd=str(RAIZ),
                            capture_output=True,
                            text=True,
                            timeout=240,
                        )

                        if resultado.returncode != 0:
                            detalhe = (
                                resultado.stderr.strip()
                                or resultado.stdout.strip()
                            )

                            raise RuntimeError(
                                detalhe
                                or "O pipeline de ingestão retornou erro."
                            )

                        st.session_state.assistente_preparado = True
                        st.success("Assistente preparado.")
                    else:
                        st.warning(
                            "O pipeline da Sprint 2 não foi encontrado. "
                            "O chat poderá depender da base já existente."
                        )
                        st.session_state.assistente_preparado = True

            except subprocess.TimeoutExpired:
                st.error(
                    "A preparação demorou mais que o esperado. "
                    "Tente novamente."
                )

            except Exception as erro:
                st.error(
                    "Não foi possível preparar o assistente. "
                    f"Detalhes: {erro}"
                )

    status_assistente = (
        "Pronto"
        if st.session_state.assistente_preparado
        else "Aguardando preparação"
    )

    st.caption(f"Status: {status_assistente}")

    st.markdown(
        """
        <div class="privacy-note">
            O dashboard não exibe CPF ou outros identificadores
            desnecessários. O histórico apresentado nesta versão
            permanece somente na sessão atual do Streamlit.
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Validação global dos dados
# -----------------------------------------------------------------------------

if st.session_state.erro_relatorio:
    cabecalho_pagina(
        "Genera AI",
        "Não foi possível abrir o relatório",
        (
            "Verifique o arquivo informado ou carregue outro relatório "
            "pela barra lateral."
        ),
    )

    st.error(st.session_state.erro_relatorio)

    st.stop()

if not isinstance(st.session_state.dados, dict):
    cabecalho_pagina(
        "Genera AI",
        "Nenhum relatório carregado",
        "Envie um arquivo JSON pela barra lateral para começar.",
    )

    tela_vazia(
        "📄",
        "Relatório necessário",
        "Carregue um relatório estruturado para visualizar o dashboard.",
    )

    st.stop()


dados = st.session_state.dados
resultados = obter_resultados(dados)
ancestralidade = obter_ancestralidade(dados)
nome_paciente = obter_nome_paciente(dados)
riscos = contagem_riscos(resultados)


# -----------------------------------------------------------------------------
# Resumo automático do relatório
# -----------------------------------------------------------------------------

def obter_resumo_automatico() -> Any:
    """
    Gera o resumo apenas uma vez por relatório durante a sessão.
    """
    if st.session_state.resumo_relatorio is not None:
        return st.session_state.resumo_relatorio

    if gerar_resumo_relatorio is None:
        return None

    try:
        resumo = gerar_resumo_relatorio(dados)
        st.session_state.resumo_relatorio = resumo
        return resumo
    except Exception:
        return None


def texto_resumo(resumo: Any) -> str:
    """
    Tenta transformar diferentes formatos de resumo em texto legível.
    """
    if resumo is None:
        return ""

    if isinstance(resumo, str):
        return resumo

    if isinstance(resumo, dict):
        for chave in (
            "resumo",
            "texto",
            "resumo_geral",
            "sumario",
            "summary",
        ):
            valor = resumo.get(chave)

            if isinstance(valor, str) and valor.strip():
                return valor.strip()

        partes = []

        for chave, valor in resumo.items():
            if isinstance(valor, (str, int, float)):
                partes.append(
                    f"{str(chave).replace('_', ' ').title()}: {valor}"
                )

        return "\n".join(partes)

    return str(resumo)


# -----------------------------------------------------------------------------
# Página: Visão geral
# -----------------------------------------------------------------------------

if st.session_state.pagina == "Visão geral":
    cabecalho_pagina(
        "Visão geral",
        f"Olá, {nome_paciente} 👋",
        (
            "Veja os principais pontos do seu relatório genético "
            "em uma experiência organizada e acessível."
        ),
    )

    disclaimer()

    total_resultados = len(resultados)
    total_ancestralidade = len(ancestralidade)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        card_metrica(
            "Resultados analisados",
            total_resultados,
            "Condições e características presentes no relatório.",
        )

    with col2:
        card_metrica(
            "Maior atenção",
            riscos.get("alto", 0),
            "Resultados que merecem uma leitura mais cuidadosa.",
        )

    with col3:
        card_metrica(
            "Atenção moderada",
            riscos.get("medio", 0),
            "Predisposições intermediárias no relatório.",
        )

    with col4:
        card_metrica(
            "Ancestralidade",
            total_ancestralidade,
            "Regiões ou populações identificadas.",
        )

    titulo_secao(
        "Principais resultados",
        "Visão resumida do relatório",
    )

    if resultados:
        resultados_priorizados = sorted(
            resultados,
            key=lambda item: {
                "alto": 0,
                "medio": 1,
                "baixo": 2,
                "indefinido": 3,
            }.get(
                obter_risco_resultado(item),
                4,
            ),
        )

        exibidos = resultados_priorizados[:6]

        for inicio in range(0, len(exibidos), 3):
            linha = exibidos[inicio : inicio + 3]
            colunas = st.columns(len(linha))

            for coluna, resultado in zip(colunas, linha):
                with coluna:
                    card_resultado(resultado)

        if len(resultados) > 6:
            st.caption(
                f"Mostrando 6 de {len(resultados)} resultados. "
                "Acesse 'Meus resultados' para ver todos."
            )

    else:
        tela_vazia(
            "🧬",
            "Nenhum resultado encontrado",
            (
                "O relatório carregado não possui uma lista de "
                "resultados genéticos reconhecida."
            ),
        )

    esquerda, direita = st.columns([1.1, 0.9])

    with esquerda:
        titulo_secao(
            "Sua ancestralidade",
            "Composição identificada no relatório",
        )

        st.markdown(
            '<div class="content-card">',
            unsafe_allow_html=True,
        )

        if ancestralidade:
            ancestralidade_ordenada = sorted(
                ancestralidade,
                key=lambda item: dados_regiao_ancestralidade(item)[1],
                reverse=True,
            )

            for item in ancestralidade_ordenada[:8]:
                regiao, percentual = dados_regiao_ancestralidade(item)

                barra_ancestralidade(
                    regiao,
                    percentual,
                )

            if len(ancestralidade) > 8:
                st.caption(
                    f"+ {len(ancestralidade) - 8} regiões no relatório."
                )
        else:
            st.info(
                "O relatório não contém informações de ancestralidade "
                "em um formato reconhecido."
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with direita:
        titulo_secao(
            "Resumo automático",
            "Leitura rápida",
        )

        resumo = obter_resumo_automatico()
        texto = texto_resumo(resumo)

        if texto:
            st.markdown(
                f"""
                <div class="summary-card">
                    <div class="summary-lead">
                        {escapar(texto)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="summary-card">
                    <div class="summary-lead">
                        Seu relatório reúne
                        <strong>{total_resultados}</strong>
                        resultados genéticos.
                    </div>

                    <ul class="mini-list">
                        <li>
                            {riscos.get("alto", 0)}
                            resultado(s) classificados para maior atenção.
                        </li>
                        <li>
                            {riscos.get("medio", 0)}
                            resultado(s) de atenção moderada.
                        </li>
                        <li>
                            {riscos.get("baixo", 0)}
                            resultado(s) de menor atenção.
                        </li>
                        <li>
                            {total_ancestralidade}
                            região(ões) de ancestralidade identificada(s).
                        </li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

    titulo_secao(
        "Pergunte sobre seu DNA",
        "Assistente com contexto do relatório",
    )

    st.markdown(
        """
        <div class="content-card">
            <p style="margin-top: 0; color: #465269; line-height: 1.6;">
                Use o assistente para entender termos técnicos,
                predisposições, características e informações de
                ancestralidade com base no seu próprio relatório.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button(
            "O que merece mais atenção?",
            use_container_width=True,
        ):
            st.session_state.pagina = "Assistente"
            st.session_state.pergunta_sugerida = (
                "Quais resultados do meu relatório merecem mais atenção?"
            )
            st.rerun()

    with col_b:
        if st.button(
            "Explique meus resultados",
            use_container_width=True,
        ):
            st.session_state.pagina = "Assistente"
            st.session_state.pergunta_sugerida = (
                "Explique os principais resultados do meu relatório "
                "em linguagem simples."
            )
            st.rerun()

    with col_c:
        if st.button(
            "Entender ancestralidade",
            use_container_width=True,
        ):
            st.session_state.pagina = "Assistente"
            st.session_state.pergunta_sugerida = (
                "O que os dados de ancestralidade do meu relatório significam?"
            )
            st.rerun()


# -----------------------------------------------------------------------------
# Página: Meus resultados
# -----------------------------------------------------------------------------

elif st.session_state.pagina == "Meus resultados":
    cabecalho_pagina(
        "Meu DNA",
        "Seus resultados genéticos",
        (
            "Consulte cada resultado individualmente e compare "
            "a explicação simples com os detalhes técnicos."
        ),
    )

    disclaimer()

    if not resultados:
        tela_vazia(
            "🧬",
            "Nenhum resultado disponível",
            "O relatório atual não possui resultados reconhecidos.",
        )

    else:
        col_filtro, col_busca = st.columns([0.35, 0.65])

        with col_filtro:
            filtro_risco = st.selectbox(
                "Filtrar por atenção",
                [
                    "Todos",
                    "Maior atenção",
                    "Atenção moderada",
                    "Menor atenção",
                ],
            )

        with col_busca:
            busca = st.text_input(
                "Buscar resultado",
                placeholder="Ex.: diabetes, cafeína, metabolismo...",
            )

        mapa_filtro = {
            "Maior atenção": "alto",
            "Atenção moderada": "medio",
            "Menor atenção": "baixo",
        }

        resultados_filtrados = []

        for resultado in resultados:
            risco = obter_risco_resultado(resultado)
            nome = nome_resultado(resultado)
            categoria = categoria_resultado(resultado)

            if filtro_risco != "Todos":
                if risco != mapa_filtro.get(filtro_risco):
                    continue

            termo = busca.strip().lower()

            if termo:
                conteudo_busca = (
                    f"{nome} {categoria} {descricao_resultado(resultado)}"
                ).lower()

                if termo not in conteudo_busca:
                    continue

            resultados_filtrados.append(resultado)

        st.caption(
            f"{len(resultados_filtrados)} resultado(s) encontrado(s)."
        )

        for resultado in resultados_filtrados:
            risco = obter_risco_resultado(resultado)

            with st.expander(
                f"{nome_resultado(resultado)} · {rotulo_risco(risco)}"
            ):
                col_esq, col_dir = st.columns([0.58, 0.42])

                with col_esq:
                    st.markdown("#### Explicação acessível")
                    st.write(descricao_resultado(resultado))

                    recomendacao = recomendacao_resultado(resultado)

                    if recomendacao:
                        st.markdown("#### Orientação")
                        st.write(recomendacao)

                with col_dir:
                    st.markdown("#### Detalhes do relatório")

                    campos_tecnicos = [
                        ("Categoria", resultado.get("categoria")),
                        ("Risco original", resultado.get("risco")),
                        (
                            "Impacto prático",
                            resultado.get("impacto_pratico"),
                        ),
                        (
                            "Urgência médica",
                            resultado.get("urgencia_medica"),
                        ),
                    ]

                    for rotulo, valor in campos_tecnicos:
                        if valor not in (None, "", [], {}):
                            st.markdown(
                                f"**{rotulo}:** {valor}"
                            )

                    descricao_tecnica = resultado.get(
                        "descricao_tecnica"
                    )

                    if descricao_tecnica:
                        st.markdown("**Descrição técnica:**")
                        st.write(descricao_tecnica)

    titulo_secao(
        "Ancestralidade completa",
        f"{len(ancestralidade)} região(ões)",
    )

    if ancestralidade:
        st.markdown(
            '<div class="content-card">',
            unsafe_allow_html=True,
        )

        for item in sorted(
            ancestralidade,
            key=lambda item: dados_regiao_ancestralidade(item)[1],
            reverse=True,
        ):
            regiao, percentual = dados_regiao_ancestralidade(item)

            barra_ancestralidade(
                regiao,
                percentual,
            )

            intervalo = obter_primeiro(
                item,
                "intervalo_confianca_95",
                "intervalo_confianca",
                "confidence_interval",
                padrao=None,
            )

            if intervalo:
                st.caption(
                    f"Intervalo de confiança informado: {intervalo}"
                )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    else:
        tela_vazia(
            "🌎",
            "Ancestralidade não disponível",
            "O relatório atual não apresenta essa seção.",
        )
# -----------------------------------------------------------------------------
# Integração com RAG + LLM + NLP
# -----------------------------------------------------------------------------

def buscar_contexto_seguro(pergunta: str) -> dict[str, Any]:
    """
    Executa a busca semântica da Sprint 2.

    Retorna:
    {
        "pergunta": "...",
        "encontrou_contexto": True,
        "trechos": [...],
        "contexto": "..."
    }
    """
    try:
        from sprint2.vetorial.buscar import buscar_contexto

        return buscar_contexto(
            pergunta,
            top_k=3,
            similaridade_minima=0.50,
        )

    except FileNotFoundError as erro:
        raise FileNotFoundError(
            "A base vetorial ainda não foi criada."
        ) from erro

    except Exception as erro:
        raise RuntimeError(
            f"Erro na busca semântica: {erro}"
        ) from erro


def obter_api_key() -> str | None:
    """
    Obtém a chave já configurada na variável de ambiente.

    A chave pode ter vindo do .env ou do campo da sidebar.
    """
    chave = os.getenv(
        "OPENAI_API_KEY",
        "",
    ).strip()

    return chave or None


def modo_llm() -> str:
    """
    Converte o rótulo visual usado na Sprint 3 para
    o formato esperado pelo agente da Sprint 2.
    """
    if st.session_state.modo_resposta == "Técnico":
        return "tecnico"

    return "paciente"


def aplicar_nlp_resposta(
    texto: str,
    modo: str,
) -> tuple[str, dict[str, Any]]:
    """
    Aplica simplificação de linguagem apenas no modo paciente.

    Retorna:
        resposta_final
        métricas NLP
    """
    if modo != "paciente":
        return texto, {}

    if simplificar_texto is None:
        return texto, {}

    try:
        resultado = simplificar_texto(texto)

        texto_final = resultado.get(
            "texto_simplificado",
            texto,
        )

        metricas = {
            "original": resultado.get(
                "metricas_original",
                {},
            ),
            "simplificado": resultado.get(
                "metricas_simplificado",
                {},
            ),
        }

        return texto_final, metricas

    except Exception:
        # A indisponibilidade do NLP não deve impedir o chat.
        return texto, {}


def processar_pergunta(pergunta: str) -> dict[str, Any]:
    """
    Fluxo completo do Assistente Sprint 3:

    pergunta
        ↓
    busca semântica
        ↓
    RAG / guardrails
        ↓
    OpenAI
        ↓
    simplificação NLP
        ↓
    resposta ao usuário
    """

    pergunta = pergunta.strip()

    if not pergunta:
        raise ValueError(
            "Digite uma pergunta antes de enviar."
        )

    api_key = obter_api_key()

    if not api_key:
        raise PermissionError(
            "Configure sua OpenAI API Key na barra lateral."
        )

    resultado_busca = buscar_contexto_seguro(
        pergunta
    )

    trechos_completos = resultado_busca.get(
        "trechos",
        [],
    )

    # O agente da Sprint 2 espera apenas os textos dos trechos.
    trechos_texto = []

    for trecho in trechos_completos:
        if isinstance(trecho, dict):
            conteudo = trecho.get(
                "conteudo",
                "",
            )

            if conteudo:
                trechos_texto.append(
                    str(conteudo)
                )

        elif trecho:
            trechos_texto.append(
                str(trecho)
            )

    from llm_connector import responder_com_llm

    modo = modo_llm()

    resultado_llm = responder_com_llm(
        pergunta=pergunta,
        trechos=trechos_texto,
        modo=modo,
        api_key=api_key,
    )

    status = resultado_llm.get(
        "status",
        "sem_contexto",
    )

    resposta_original = str(
        resultado_llm.get(
            "resposta",
            "",
        )
    )

    # Guardrails e ausência de contexto não devem ser
    # reescritos pela simplificação NLP.
    if status == "respondido":
        resposta_final, metricas = aplicar_nlp_resposta(
            resposta_original,
            modo,
        )
    else:
        resposta_final = resposta_original
        metricas = {}

    return {
        "status": status,
        "categoria": resultado_llm.get(
            "categoria",
            "",
        ),
        "resposta_original": resposta_original,
        "resposta": resposta_final,
        "fontes": trechos_completos,
        "modo": modo,
        "metricas_nlp": metricas,
    }


def classe_chat(status: str) -> tuple[str, str]:
    """
    Define estilo e ícone conforme o resultado do agente.
    """
    if status == "bloqueado":
        return "chat-blocked", "⚠️"

    if status == "sem_contexto":
        return "chat-no-context", "ℹ️"

    return "chat-assistant", "🧬"


def exibir_fontes(
    fontes: list[Any],
) -> None:
    """
    Exibe os trechos realmente recuperados pelo RAG.
    """
    if not fontes:
        return

    quantidade = len(fontes)

    with st.expander(
        f"Fontes utilizadas ({quantidade})"
    ):
        for indice, fonte in enumerate(
            fontes,
            start=1,
        ):
            if isinstance(fonte, dict):
                conteudo = str(
                    fonte.get(
                        "conteudo",
                        "",
                    )
                )

                secao = str(
                    fonte.get(
                        "secao",
                        "Relatório",
                    )
                )

                origem = str(
                    fonte.get(
                        "fonte",
                        "Relatório genético",
                    )
                )

                try:
                    similaridade = float(
                        fonte.get(
                            "similaridade",
                            0.0,
                        )
                    )
                except (TypeError, ValueError):
                    similaridade = 0.0

            else:
                conteudo = str(fonte)
                secao = "Relatório"
                origem = "Relatório genético"
                similaridade = 0.0

            trecho_exibido = conteudo

            if len(trecho_exibido) > 320:
                trecho_exibido = (
                    trecho_exibido[:320]
                    + "..."
                )

            st.markdown(
                f"""
                <div class="source-card">
                    <strong>Fonte {indice} · {escapar(secao)}</strong>
                    <br>
                    {escapar(trecho_exibido)}
                    <br>
                    <small>
                        Origem: {escapar(origem)}
                    </small>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if similaridade > 0:
                similaridade_segura = max(
                    0.0,
                    min(
                        similaridade,
                        1.0,
                    ),
                )

                st.progress(
                    similaridade_segura,
                    text=(
                        "Relevância semântica: "
                        f"{similaridade_segura:.0%}"
                    ),
                )


def exibir_metricas_nlp(
    metricas: dict[str, Any],
) -> None:
    """
    Exibe métricas de simplificação apenas como
    informação técnica complementar.
    """
    if not metricas:
        return

    original = metricas.get(
        "original",
        {},
    )

    simplificado = metricas.get(
        "simplificado",
        {},
    )

    if not original and not simplificado:
        return

    with st.expander(
        "Como a linguagem foi simplificada?"
    ):
        st.caption(
            "Estas métricas ajudam a demonstrar a camada "
            "de NLP desenvolvida para a Sprint 3."
        )

        col_original, col_simplificado = st.columns(2)

        with col_original:
            st.markdown("**Texto original**")

            if original:
                for chave, valor in original.items():
                    st.write(
                        f"{str(chave).replace('_', ' ').title()}: "
                        f"{valor}"
                    )
            else:
                st.caption(
                    "Métricas não disponíveis."
                )

        with col_simplificado:
            st.markdown(
                "**Texto apresentado ao paciente**"
            )

            if simplificado:
                for chave, valor in simplificado.items():
                    st.write(
                        f"{str(chave).replace('_', ' ').title()}: "
                        f"{valor}"
                    )
            else:
                st.caption(
                    "Métricas não disponíveis."
                )


def historico_para_resumo() -> list[dict[str, str]]:
    """
    Converte as mensagens do Streamlit para o formato
    esperado por gerar_resumo_interacoes().
    """
    interacoes = []

    pergunta_atual = None

    for mensagem in st.session_state.messages:
        role = mensagem.get(
            "role"
        )

        if role == "user":
            pergunta_atual = str(
                mensagem.get(
                    "content",
                    "",
                )
            )

        elif (
            role == "assistant"
            and pergunta_atual
        ):
            interacoes.append(
                {
                    "pergunta": pergunta_atual,
                    "resposta": str(
                        mensagem.get(
                            "content",
                            "",
                        )
                    ),
                }
            )

            pergunta_atual = None

    return interacoes


# -----------------------------------------------------------------------------
# Página: Assistente
# -----------------------------------------------------------------------------

if st.session_state.pagina == "Assistente":
    cabecalho_pagina(
        "Assistente",
        "Converse sobre seu relatório",
        (
            "Faça perguntas em linguagem natural. "
            "As respostas utilizam busca semântica, RAG e "
            "as salvaguardas desenvolvidas nas Sprints anteriores."
        ),
    )

    disclaimer()

    if not st.session_state.assistente_preparado:
        st.info(
            "Antes de conversar, clique em "
            "'Preparar assistente' na barra lateral."
        )

    st.markdown(
        """
        <div class="content-card">
            <strong>Algumas perguntas que você pode fazer:</strong>
            <br><br>
            • O que merece mais atenção no meu relatório?<br>
            • Explique meu resultado de diabetes em linguagem simples.<br>
            • O que minha ancestralidade significa?<br>
            • Quais recomendações aparecem no meu relatório?
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # Histórico visual
    # -------------------------------------------------------------------------

    if not st.session_state.messages:
        tela_vazia(
            "💬",
            "Nenhuma conversa ainda",
            (
                "Escolha uma pergunta sugerida ou escreva "
                "sua dúvida abaixo."
            ),
        )

    else:
        for mensagem in st.session_state.messages:
            role = mensagem.get(
                "role",
                "",
            )

            conteudo = str(
                mensagem.get(
                    "content",
                    "",
                )
            )

            if role == "user":
                st.markdown(
                    f"""
                    <div class="chat-user">
                        <div class="chat-name">
                            Você
                        </div>
                        {escapar(conteudo).replace(chr(10), "<br>")}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            elif role == "assistant":
                status = mensagem.get(
                    "status",
                    "respondido",
                )

                classe, icone = classe_chat(
                    status
                )

                modo_msg = mensagem.get(
                    "modo",
                    "paciente",
                )

                modo_legivel = (
                    "Paciente"
                    if modo_msg == "paciente"
                    else "Técnico"
                )

                st.markdown(
                    f"""
                    <div class="{classe}">
                        <div class="chat-name">
                            {icone} Genera AI · {escapar(modo_legivel)}
                        </div>
                        {escapar(conteudo).replace(chr(10), "<br>")}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                exibir_fontes(
                    mensagem.get(
                        "fontes",
                        [],
                    )
                )

                exibir_metricas_nlp(
                    mensagem.get(
                        "metricas_nlp",
                        {},
                    )
                )

    # -------------------------------------------------------------------------
    # Pergunta sugerida vinda do Dashboard
    # -------------------------------------------------------------------------

    pergunta_sugerida = st.session_state.pop(
        "pergunta_sugerida",
        "",
    )

    # -------------------------------------------------------------------------
    # Entrada do chat
    # -------------------------------------------------------------------------

    pergunta_chat = st.chat_input(
        "Pergunte sobre seu relatório genético..."
    )

    pergunta_final = (
        pergunta_sugerida
        or pergunta_chat
    )

    if pergunta_final:
        pergunta_final = pergunta_final.strip()

        if not st.session_state.assistente_preparado:
            st.warning(
                "Prepare o assistente pela barra lateral "
                "antes de enviar perguntas."
            )

        elif not obter_api_key():
            st.error(
                "Configure sua OpenAI API Key na barra lateral."
            )

        else:
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": pergunta_final,
                }
            )

            with st.spinner(
                "Analisando seu relatório..."
            ):
                try:
                    resultado = processar_pergunta(
                        pergunta_final
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": resultado[
                                "resposta"
                            ],
                            "resposta_original": resultado[
                                "resposta_original"
                            ],
                            "status": resultado[
                                "status"
                            ],
                            "categoria": resultado[
                                "categoria"
                            ],
                            "fontes": resultado[
                                "fontes"
                            ],
                            "modo": resultado[
                                "modo"
                            ],
                            "metricas_nlp": resultado[
                                "metricas_nlp"
                            ],
                        }
                    )

                except FileNotFoundError:
                    st.session_state.messages.pop()

                    st.error(
                        "A base vetorial não foi encontrada. "
                        "Clique em 'Preparar assistente' novamente."
                    )

                except PermissionError as erro:
                    st.session_state.messages.pop()

                    st.error(
                        str(erro)
                    )

                except RuntimeError as erro:
                    st.session_state.messages.pop()

                    mensagem_erro = str(
                        erro
                    )

                    if (
                        "quota"
                        in mensagem_erro.lower()
                        or "limit"
                        in mensagem_erro.lower()
                    ):
                        st.error(
                            "O limite de uso da API foi atingido."
                        )
                    else:
                        st.error(
                            "Não foi possível gerar a resposta. "
                            f"Detalhes: {mensagem_erro}"
                        )

                except Exception as erro:
                    st.session_state.messages.pop()

                    st.error(
                        "Ocorreu um erro inesperado ao processar "
                        f"a pergunta: {erro}"
                    )

            st.rerun()

    if st.session_state.messages:
        st.markdown("---")

        if st.button(
            "Limpar conversa",
            use_container_width=False,
        ):
            st.session_state.messages = []
            st.rerun()


# -----------------------------------------------------------------------------
# Página: Histórico
# -----------------------------------------------------------------------------

elif st.session_state.pagina == "Histórico":
    cabecalho_pagina(
        "Histórico",
        "Resumo das suas interações",
        (
            "Veja as perguntas realizadas nesta sessão e os "
            "principais temas identificados automaticamente."
        ),
    )

    disclaimer()

    interacoes = historico_para_resumo()

    if not interacoes:
        tela_vazia(
            "🕘",
            "Histórico vazio",
            (
                "As conversas realizadas com o assistente "
                "aparecerão aqui."
            ),
        )

    else:
        col1, col2 = st.columns(
            [0.58, 0.42]
        )

        with col1:
            titulo_secao(
                "Conversas da sessão",
                f"{len(interacoes)} interação(ões)",
            )

            for indice, interacao in enumerate(
                reversed(interacoes),
                start=1,
            ):
                numero_original = (
                    len(interacoes)
                    - indice
                    + 1
                )

                with st.expander(
                    f"Interação {numero_original} · "
                    f"{interacao['pergunta'][:70]}"
                ):
                    st.markdown(
                        "**Pergunta**"
                    )

                    st.write(
                        interacao[
                            "pergunta"
                        ]
                    )

                    st.markdown(
                        "**Resposta**"
                    )

                    st.write(
                        interacao[
                            "resposta"
                        ]
                    )

        with col2:
            titulo_secao(
                "Resumo automático",
                "NLP",
            )

            if gerar_resumo_interacoes is not None:
                try:
                    resumo_historico = (
                        gerar_resumo_interacoes(
                            interacoes
                        )
                    )

                    if (
                        formatar_resumo_interacoes
                        is not None
                    ):
                        resumo_formatado = (
                            formatar_resumo_interacoes(
                                resumo_historico
                            )
                        )
                    else:
                        resumo_formatado = str(
                            resumo_historico
                        )

                    st.markdown(
                        f"""
                        <div class="summary-card">
                            <div class="summary-lead">
                                {
                                    escapar(
                                        resumo_formatado
                                    ).replace(
                                        chr(10),
                                        "<br>"
                                    )
                                }
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                except Exception as erro:
                    st.info(
                        "O resumo das interações não pôde "
                        f"ser gerado: {erro}"
                    )

            else:
                st.info(
                    "O módulo de resumo automático "
                    "não está disponível."
                )

    st.markdown(
        """
        <div class="privacy-note">
            Este histórico utiliza apenas o estado da sessão atual
            do Streamlit. Ao encerrar a sessão, esta interface não
            mantém um banco próprio com as conversas do paciente.
        </div>
        """,
        unsafe_allow_html=True,
    )
