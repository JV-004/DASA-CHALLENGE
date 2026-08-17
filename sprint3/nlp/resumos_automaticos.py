"""
Módulo de NLP - Resumos Automáticos
DASA / Genera - Sprint 3

Responsável por:
1. gerar resumo estruturado do relatório genético;
2. gerar síntese automática das interações do usuário;
3. identificar os principais temas abordados;
4. atualizar o resumo quando novas interações são adicionadas.

A implementação utiliza regras determinísticas para evitar
a criação de informações que não estejam presentes nos dados
ou no histórico das interações.
"""

import json
import re
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO DE TEMAS
# ============================================================

TEMAS_INTERACAO = {
    "diabetes": {
        "palavras": [
            "diabetes",
            "glicose",
            "glicemia",
            "insulina"
        ],
        "descricao": "risco genético relacionado ao diabetes"
    },

    "cancer": {
        "palavras": [
            "câncer",
            "cancer",
            "carcinoma",
            "brca",
            "tumor",
            "oncológico",
            "oncologico"
        ],
        "descricao": "predisposição genética relacionada ao câncer"
    },

    "cardiovascular": {
        "palavras": [
            "hipertensão",
            "hipertensao",
            "pressão",
            "pressao",
            "cardiovascular",
            "coração",
            "coracao"
        ],
        "descricao": "risco e acompanhamento cardiovascular"
    },

    "ancestralidade": {
        "palavras": [
            "ancestralidade",
            "ancestral",
            "origem",
            "população",
            "populacao"
        ],
        "descricao": "ancestralidade genética"
    },

    "interpretacao_risco": {
        "palavras": [
            "risco alto",
            "risco médio",
            "risco medio",
            "risco baixo",
            "percentil",
            "predisposição",
            "predisposicao",
            "significa risco",
            "o que significa"
        ],
        "descricao": "interpretação dos níveis de risco genético"
    },

    "acompanhamento": {
        "palavras": [
            "médico",
            "medico",
            "consulta",
            "procurar",
            "acompanhamento",
            "especialista",
            "endocrinologista",
            "cardiologista",
            "geneticista"
        ],
        "descricao": "necessidade de acompanhamento profissional"
    },

    "metabolismo": {
        "palavras": [
            "metabolismo",
            "metabólico",
            "metabolico"
        ],
        "descricao": "características genéticas relacionadas ao metabolismo"
    }
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def carregar_dados(caminho_arquivo):
    """
    Carrega os dados estruturados de um arquivo JSON.
    """

    caminho = Path(caminho_arquivo)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def limpar_texto(texto):
    """
    Normaliza espaços e quebras de linha.
    """

    if not texto:
        return ""

    texto = str(texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def garantir_lista(valor):
    """
    Garante que determinado campo seja processado como lista.
    """

    if valor is None:
        return []

    if isinstance(valor, list):
        return valor

    return [valor]


def formatar_item(item):
    """
    Converte diferentes tipos de dados em texto legível.
    """

    if isinstance(item, dict):
        partes = []

        for chave, valor in item.items():
            if valor not in (None, "", [], {}):
                chave_formatada = chave.replace("_", " ").capitalize()
                partes.append(
                    f"{chave_formatada}: {valor}"
                )

        return " | ".join(partes)

    return limpar_texto(item)


def pluralizar(quantidade, singular, plural=None):
    """
    Retorna singular ou plural conforme a quantidade.
    """

    if plural is None:
        plural = singular + "s"

    return singular if quantidade == 1 else plural


# ============================================================
# RESUMO DO RELATÓRIO
# ============================================================

def gerar_resumo_relatorio(dados):
    """
    Gera uma versão estruturada do resumo
    do relatório genético.
    """

    paciente = dados.get("paciente", {})
    sumario = dados.get("sumario", {})

    total = sumario.get(
        "total_condicoes_analisadas",
        0
    )

    alto_risco = sumario.get(
        "condicoes_alto_risco",
        0
    )

    medio_risco = sumario.get(
        "condicoes_medio_risco",
        0
    )

    baixo_risco = sumario.get(
        "condicoes_baixo_risco",
        0
    )

    riscos = garantir_lista(
        sumario.get("principais_riscos_medico")
    )

    recomendacoes = garantir_lista(
        sumario.get("recomendacoes_prioritarias")
    )

    riscos_formatados = []

    for risco in riscos:
        risco_formatado = formatar_item(risco)

        if risco_formatado:
            riscos_formatados.append(
                risco_formatado
            )

    recomendacoes_formatadas = []

    for recomendacao in recomendacoes:
        recomendacao_formatada = formatar_item(
            recomendacao
        )

        if recomendacao_formatada:
            recomendacoes_formatadas.append(
                recomendacao_formatada
            )

    distribuicao = {
        "alto": alto_risco,
        "medio": medio_risco,
        "baixo": baixo_risco
    }

    palavra_condicao = pluralizar(
        total,
        "condição",
        "condições"
    )

    resumo_textual = (
        f"O relatório analisou {total} {palavra_condicao} genéticas: "
        f"{alto_risco} foram classificadas como alto risco, "
        f"{medio_risco} como médio risco e "
        f"{baixo_risco} como baixo risco."
    )

    resultado = {
        "id_relatorio": paciente.get(
            "id_relatorio"
        ),

        "total_condicoes": total,

        "distribuicao_risco": distribuicao,

        "principais_riscos":
            riscos_formatados,

        "recomendacoes":
            recomendacoes_formatadas,

        "resumo_textual":
            resumo_textual
    }

    return resultado


def formatar_resumo_relatorio(resumo):
    """
    Converte o resumo estruturado em texto.
    """

    linhas = [
        "RESUMO AUTOMÁTICO DO RELATÓRIO",
        "",
        resumo["resumo_textual"]
    ]

    if resumo["principais_riscos"]:
        linhas.extend([
            "",
            "PRINCIPAIS RESULTADOS IDENTIFICADOS:"
        ])

        for risco in resumo["principais_riscos"]:
            linhas.append(
                f"- {risco}"
            )

    if resumo["recomendacoes"]:
        linhas.extend([
            "",
            "RECOMENDAÇÕES PRESENTES NO RELATÓRIO:"
        ])

        for recomendacao in resumo["recomendacoes"]:
            linhas.append(
                f"- {recomendacao}"
            )

    return "\n".join(linhas)


# ============================================================
# NLP DAS INTERAÇÕES
# ============================================================

def identificar_temas(texto):
    """
    Identifica temas presentes no texto usando
    um vocabulário controlado.
    """

    texto_normalizado = limpar_texto(
        texto
    ).lower()

    temas_encontrados = []

    for nome_tema, configuracao in TEMAS_INTERACAO.items():

        for palavra in configuracao["palavras"]:

            if palavra.lower() in texto_normalizado:

                if nome_tema not in temas_encontrados:
                    temas_encontrados.append(
                        nome_tema
                    )

                break

    return temas_encontrados


def analisar_interacoes(interacoes):
    """
    Analisa perguntas e respostas do histórico.
    """

    interacoes_validas = []
    ordem_temas = []
    frequencia_temas = {}

    for interacao in interacoes:

        pergunta = limpar_texto(
            interacao.get(
                "pergunta",
                ""
            )
        )

        resposta = limpar_texto(
            interacao.get(
                "resposta",
                ""
            )
        )

        if not pergunta and not resposta:
            continue

        texto_completo = (
            f"{pergunta} {resposta}"
        )

        temas = identificar_temas(
            texto_completo
        )

        for tema in temas:

            frequencia_temas[tema] = (
                frequencia_temas.get(
                    tema,
                    0
                ) + 1
            )

            if tema not in ordem_temas:
                ordem_temas.append(
                    tema
                )

        interacoes_validas.append({
            "pergunta": pergunta,
            "resposta": resposta,
            "temas": temas
        })

    temas_ordenados = sorted(
        ordem_temas,
        key=lambda tema: (
            -frequencia_temas.get(
                tema,
                0
            ),
            ordem_temas.index(
                tema
            )
        )
    )

    return {
        "interacoes":
            interacoes_validas,

        "frequencia_temas":
            frequencia_temas,

        "temas_ordenados":
            temas_ordenados
    }


def gerar_sintese_temas(temas):
    """
    Transforma os temas encontrados em uma
    frase de resumo em linguagem natural.
    """

    descricoes = [
        TEMAS_INTERACAO[tema]["descricao"]
        for tema in temas
        if tema in TEMAS_INTERACAO
    ]

    if not descricoes:
        return (
            "As interações abordaram dúvidas "
            "relacionadas ao conteúdo do relatório genético."
        )

    if len(descricoes) == 1:
        return (
            f"O principal tema abordado foi "
            f"{descricoes[0]}."
        )

    if len(descricoes) == 2:
        return (
            "Os principais temas abordados foram "
            f"{descricoes[0]} e "
            f"{descricoes[1]}."
        )

    inicio = ", ".join(
        descricoes[:-1]
    )

    return (
        "Os principais temas abordados foram "
        f"{inicio} e "
        f"{descricoes[-1]}."
    )


def gerar_resumo_interacoes(interacoes):
    """
    Gera resumo semântico do histórico
    de interações.
    """

    if not interacoes:
        return {
            "total_interacoes": 0,
            "temas": [],
            "frequencia_temas": {},
            "ultima_duvida": None,
            "resumo_textual":
                "Ainda não existem interações para resumir."
        }

    analise = analisar_interacoes(
        interacoes
    )

    interacoes_validas = analise[
        "interacoes"
    ]

    temas = analise[
        "temas_ordenados"
    ]

    if not interacoes_validas:
        return {
            "total_interacoes": 0,
            "temas": [],
            "frequencia_temas": {},
            "ultima_duvida": None,
            "resumo_textual":
                "Não foram encontradas interações válidas."
        }

    total = len(
        interacoes_validas
    )

    ultima_duvida = interacoes_validas[
        -1
    ]["pergunta"]

    sintese_temas = gerar_sintese_temas(
        temas
    )

    palavra_interacao = pluralizar(
        total,
        "interação",
        "interações"
    )

    palavra_valida = pluralizar(
        total,
        "válida",
        "válidas"
    )

    resumo_textual = (
        f"O histórico possui {total} "
        f"{palavra_interacao} {palavra_valida}. "
        f"{sintese_temas}"
    )

    if ultima_duvida:
        resumo_textual += (
            " A dúvida mais recente do usuário foi: "
            f"\"{ultima_duvida}\""
        )

    descricoes_temas = [
        TEMAS_INTERACAO[tema]["descricao"]
        for tema in temas
        if tema in TEMAS_INTERACAO
    ]

    return {
        "total_interacoes":
            total,

        "temas":
            descricoes_temas,

        "frequencia_temas":
            analise[
                "frequencia_temas"
            ],

        "ultima_duvida":
            ultima_duvida,

        "resumo_textual":
            resumo_textual
    }


def atualizar_resumo_interacoes(
    interacoes,
    nova_interacao
):
    """
    Atualiza automaticamente o resumo após
    receber uma nova interação.

    A lista original não é modificada.
    """

    historico_atualizado = list(
        interacoes
    )

    historico_atualizado.append(
        nova_interacao
    )

    return gerar_resumo_interacoes(
        historico_atualizado
    )


def formatar_resumo_interacoes(resumo):
    """
    Formata o resumo das interações
    para visualização.
    """

    linhas = [
        "RESUMO AUTOMÁTICO DAS INTERAÇÕES",
        "",
        resumo["resumo_textual"]
    ]

    if resumo["temas"]:
        linhas.extend([
            "",
            "TEMAS IDENTIFICADOS:"
        ])

        for tema in resumo["temas"]:
            linhas.append(
                f"- {tema}"
            )

    return "\n".join(linhas)


# ============================================================
# TESTES
# ============================================================

if __name__ == "__main__":

    raiz_projeto = Path(
        __file__
    ).resolve().parents[2]

    caminho_json = (
        raiz_projeto /
        "dados_estruturados.json"
    )

    dados = carregar_dados(
        caminho_json
    )

    # --------------------------------------------------------
    # TESTE 1 - RESUMO DO RELATÓRIO
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "TESTE 1 - RESUMO AUTOMÁTICO DO RELATÓRIO"
    )

    print(
        "=" * 70
    )

    resumo_relatorio = gerar_resumo_relatorio(
        dados
    )

    print(
        formatar_resumo_relatorio(
            resumo_relatorio
        )
    )

    # --------------------------------------------------------
    # HISTÓRICO SIMULADO
    # --------------------------------------------------------

    interacoes_teste = [
        {
            "pergunta":
                "O que meu relatório diz sobre diabetes?",

            "resposta":
                "O relatório indica uma predisposição genética "
                "relacionada ao diabetes."
        },

        {
            "pergunta":
                "O que significa risco alto?",

            "resposta":
                "Risco alto indica uma associação genética "
                "mais relevante, mas não representa diagnóstico."
        }
    ]

    # --------------------------------------------------------
    # TESTE 2 - RESUMO DAS INTERAÇÕES
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "TESTE 2 - RESUMO AUTOMÁTICO DAS INTERAÇÕES"
    )

    print(
        "=" * 70
    )

    resumo_interacoes = gerar_resumo_interacoes(
        interacoes_teste
    )

    print(
        formatar_resumo_interacoes(
            resumo_interacoes
        )
    )

    # --------------------------------------------------------
    # TESTE 3 - ATUALIZAÇÃO DO RESUMO
    # --------------------------------------------------------

    nova_interacao = {
        "pergunta":
            "Preciso procurar um médico?",

        "resposta":
            "O relatório recomenda acompanhamento profissional "
            "para interpretação adequada dos resultados."
    }

    print(
        "\n" + "=" * 70
    )

    print(
        "TESTE 3 - ATUALIZAÇÃO DO RESUMO"
    )

    print(
        "=" * 70
    )

    resumo_atualizado = atualizar_resumo_interacoes(
        interacoes_teste,
        nova_interacao
    )

    print(
        formatar_resumo_interacoes(
            resumo_atualizado
        )
    )