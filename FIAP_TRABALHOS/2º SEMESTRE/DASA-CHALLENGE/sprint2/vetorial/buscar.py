"""
Busca Semântica — Sprint 2 / Genera / Dasa

Responsável por:
1. Receber uma pergunta do usuário
2. Gerar embedding da pergunta
3. Consultar a base vetorial ChromaDB
4. Retornar os trechos mais relevantes do relatório
5. Exibir fonte, seção e similaridade

A base vetorial pode ser informada dinamicamente.
Isso permite utilizar uma base ChromaDB isolada para cada relatório.

Uso padrão no terminal:
    python sprint2/vetorial/buscar.py

Uso com uma base específica:
    python sprint2/vetorial/buscar.py caminho/para/chromadb
"""

import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from sentence_transformers import SentenceTransformer


# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

RAIZ = (
    Path(__file__)
    .resolve()
    .parents[2]
)

BASE_VETORIAL = (
    RAIZ
    / "sprint2"
    / "vetorial"
    / "base_vetorial"
)

COLECAO_NOME = "genera_relatorio"

MODELO_NOME = "all-MiniLM-L6-v2"

TOP_K_PADRAO = 3

SIMILARIDADE_MINIMA = 0.35


# =============================================================================
# CARREGAMENTO DO MODELO
# =============================================================================

@lru_cache(maxsize=1)
def carregar_modelo() -> SentenceTransformer:
    """
    Carrega o mesmo modelo utilizado para gerar
    os embeddings dos chunks.

    O cache evita carregar o modelo novamente
    a cada pergunta realizada pelo usuário.
    """

    return SentenceTransformer(
        MODELO_NOME
    )


# =============================================================================
# CARREGAMENTO DA BASE VETORIAL
# =============================================================================

def carregar_colecao(
    base_path: Path = BASE_VETORIAL,
):
    """
    Conecta à base vetorial persistida no ChromaDB.

    O caminho pode ser informado dinamicamente,
    permitindo uma base independente para cada
    relatório.
    """

    base_path = Path(
        base_path
    )

    if not base_path.exists():

        raise FileNotFoundError(
            "Base vetorial não encontrada em: "
            f"{base_path}\n"
            "Prepare o assistente antes "
            "de realizar uma busca."
        )

    cliente = (
        chromadb.PersistentClient(
            path=str(
                base_path
            )
        )
    )

    try:

        colecao = (
            cliente.get_collection(
                COLECAO_NOME
            )
        )

    except Exception as erro:

        raise FileNotFoundError(
            "A coleção vetorial "
            f"'{COLECAO_NOME}' "
            "não foi encontrada em: "
            f"{base_path}"
        ) from erro

    return colecao


# =============================================================================
# BUSCA SEMÂNTICA
# =============================================================================

def buscar_trechos(
    pergunta: str,
    top_k: int = TOP_K_PADRAO,
    similaridade_minima: float = SIMILARIDADE_MINIMA,
    base_path: Path = BASE_VETORIAL,
) -> List[Dict[str, Any]]:
    """
    Recebe uma pergunta em linguagem natural
    e retorna os trechos mais relevantes do
    relatório genético.

    A busca pode utilizar uma base ChromaDB
    específica através de base_path.

    Retorno:
        [
            {
                "conteudo": "...",
                "secao": "...",
                "fonte": "...",
                "similaridade": 0.82
            }
        ]
    """

    if (
        not pergunta
        or not pergunta.strip()
    ):

        raise ValueError(
            "A pergunta não pode estar vazia."
        )


    base_path = Path(
        base_path
    )


    modelo = (
        carregar_modelo()
    )

    colecao = (
        carregar_colecao(
            base_path
        )
    )


    embedding_pergunta = (
        modelo.encode(
            pergunta
        )
        .tolist()
    )


    resultados = (
        colecao.query(
            query_embeddings=[
                embedding_pergunta
            ],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )
    )


    trechos = []


    documentos = (
        resultados.get(
            "documents",
            [[]],
        )[0]
    )

    metadados = (
        resultados.get(
            "metadatas",
            [[]],
        )[0]
    )

    distancias = (
        resultados.get(
            "distances",
            [[]],
        )[0]
    )


    for (
        documento,
        metadata,
        distancia,
    ) in zip(
        documentos,
        metadados,
        distancias,
    ):

        similaridade = (
            round(
                1 - distancia,
                4,
            )
        )

        if (
            similaridade
            < similaridade_minima
        ):
            continue


        trechos.append(
            {
                "conteudo":
                    documento,

                "secao":
                    metadata.get(
                        "secao",
                        "",
                    ),

                "fonte":
                    metadata.get(
                        "fonte",
                        "",
                    ),

                "similaridade":
                    similaridade,
            }
        )


    return trechos


# =============================================================================
# MONTAGEM DO CONTEXTO
# =============================================================================

def montar_contexto(
    trechos: List[
        Dict[str, Any]
    ],
) -> str:
    """
    Monta o contexto que será enviado
    ao agente / LLM.
    """

    if not trechos:
        return ""


    contexto = (
        "TRECHOS RECUPERADOS "
        "DO RELATÓRIO GENÉTICO:\n\n"
    )


    for (
        indice,
        trecho,
    ) in enumerate(
        trechos,
        start=1,
    ):

        contexto += (
            f"[Fonte {indice}]\n"
        )

        contexto += (
            "Seção: "
            f"{trecho['secao']}\n"
        )

        contexto += (
            "Origem: "
            f"{trecho['fonte']}\n"
        )

        contexto += (
            "Similaridade: "
            f"{trecho['similaridade']}\n"
        )

        contexto += (
            "Conteúdo: "
            f"{trecho['conteudo']}\n\n"
        )


    return contexto.strip()


# =============================================================================
# FUNÇÃO PRINCIPAL PARA INTEGRAÇÃO COM O AGENTE
# =============================================================================

def buscar_contexto(
    pergunta: str,
    top_k: int = TOP_K_PADRAO,
    similaridade_minima: float = SIMILARIDADE_MINIMA,
    base_path: Path = BASE_VETORIAL,
) -> Dict[str, Any]:
    """
    Função principal para integração com
    o agente.

    A base vetorial pode ser informada
    através de base_path.

    Retorna:
        {
            "pergunta": "...",
            "encontrou_contexto": True,
            "trechos": [...],
            "contexto": "..."
        }
    """

    trechos = (
        buscar_trechos(
            pergunta=pergunta,
            top_k=top_k,
            similaridade_minima=(
                similaridade_minima
            ),
            base_path=base_path,
        )
    )


    contexto = (
        montar_contexto(
            trechos
        )
    )


    return {
        "pergunta":
            pergunta,

        "encontrou_contexto":
            len(trechos) > 0,

        "trechos":
            trechos,

        "contexto":
            contexto,
    }


# =============================================================================
# EXIBIÇÃO NO TERMINAL
# =============================================================================

def imprimir_resultados(
    pergunta: str,
    trechos: List[
        Dict[str, Any]
    ],
) -> None:
    """
    Exibe os resultados da busca
    no terminal.
    """

    print(
        "\n"
        + "=" * 70
    )

    print(
        "BUSCA SEMÂNTICA — RESULTADO"
    )

    print(
        "=" * 70
    )

    print(
        f"Pergunta: {pergunta}"
    )


    if not trechos:

        print(
            "\nNenhum trecho com "
            "similaridade suficiente "
            "foi encontrado."
        )

        print(
            "O agente deve responder "
            "que não encontrou informação "
            "no relatório."
        )

        return


    for (
        indice,
        trecho,
    ) in enumerate(
        trechos,
        start=1,
    ):

        print(
            "\n"
            + "-" * 70
        )

        print(
            f"Fonte {indice}"
        )

        print(
            "-" * 70
        )

        print(
            "Similaridade: "
            f"{trecho['similaridade']}"
        )

        print(
            "Seção: "
            f"{trecho['secao']}"
        )

        print(
            "Fonte: "
            f"{trecho['fonte']}"
        )

        print(
            "Trecho: "
            f"{trecho['conteudo']}"
        )


# =============================================================================
# EXECUÇÃO VIA TERMINAL
# =============================================================================

def main(
    base_path: Path = BASE_VETORIAL,
) -> None:

    print(
        "=" * 70
    )

    print(
        "BUSCA SEMÂNTICA "
        "— Sprint 2 / Genera / Dasa"
    )

    print(
        "=" * 70
    )

    print(
        "Base vetorial: "
        f"{base_path}"
    )


    try:

        pergunta = input(
            "\nDigite sua pergunta "
            "sobre o relatório genético: "
        ).strip()


        resultado = (
            buscar_contexto(
                pergunta,
                base_path=base_path,
            )
        )


        imprimir_resultados(
            pergunta=(
                resultado[
                    "pergunta"
                ]
            ),
            trechos=(
                resultado[
                    "trechos"
                ]
            ),
        )


    except Exception as erro:

        print(
            "\n[ERRO] Falha ao "
            "executar busca semântica."
        )

        print(
            str(
                erro
            )
        )

        sys.exit(
            1
        )


if __name__ == "__main__":

    base = (
        Path(
            sys.argv[1]
        )
        if len(sys.argv) > 1
        else BASE_VETORIAL
    )

    main(
        base
    )