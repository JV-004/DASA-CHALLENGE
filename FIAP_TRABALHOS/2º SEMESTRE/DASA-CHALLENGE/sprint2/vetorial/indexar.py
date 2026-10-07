"""
Indexador Vetorial — Sprint 2 / Genera / Dasa

Lê chunks.json e indexa os dados em uma base vetorial ChromaDB.

O caminho dos chunks e o caminho da base vetorial podem ser
informados dinamicamente. Isso permite manter uma base isolada
para cada relatório no ambiente de produção.
"""

import json
import sys
from pathlib import Path

import chromadb


# =============================================================================
# CAMINHOS E CONFIGURAÇÕES
# =============================================================================

RAIZ = Path(__file__).resolve().parents[2]

CHUNKS_JSON = (
    RAIZ
    / "sprint2"
    / "embeddings"
    / "chunks.json"
)

BASE_VETORIAL = (
    Path(__file__).parent
    / "base_vetorial"
)

COLECAO_NOME = "genera_relatorio"


# =============================================================================
# CARREGAMENTO DOS CHUNKS
# =============================================================================

def carregar_chunks(
    caminho: Path,
) -> list[dict]:

    caminho = Path(
        caminho
    )

    with open(
        caminho,
        "r",
        encoding="utf-8",
    ) as arquivo:

        return json.load(
            arquivo
        )


# =============================================================================
# INDEXAÇÃO NO CHROMADB
# =============================================================================

def indexar(
    chunks: list[dict],
    base_path: Path,
) -> chromadb.Collection:

    base_path = Path(
        base_path
    )

    base_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    cliente = (
        chromadb.PersistentClient(
            path=str(
                base_path
            )
        )
    )

    # Remove somente a coleção da base
    # que está sendo reindexada.
    #
    # Como cada relatório poderá utilizar
    # uma pasta própria, um relatório não
    # apagará os dados de outro relatório.
    try:

        cliente.delete_collection(
            COLECAO_NOME
        )

        print(
            "  Coleção anterior "
            f"'{COLECAO_NOME}' "
            "removida para reindexação."
        )

    except Exception:

        # A coleção ainda não existe.
        pass


    colecao = (
        cliente.create_collection(
            name=COLECAO_NOME,
            metadata={
                "hnsw:space":
                    "cosine"
            },
        )
    )


    ids = [
        chunk["id"]
        for chunk in chunks
    ]

    embeddings = [
        chunk["embedding"]
        for chunk in chunks
    ]

    documentos = [
        chunk["conteudo"]
        for chunk in chunks
    ]

    metadados = [
        {
            "secao":
                chunk["secao"],

            "fonte":
                chunk["fonte"],
        }
        for chunk in chunks
    ]


    colecao.add(
        ids=ids,
        embeddings=embeddings,
        documents=documentos,
        metadatas=metadados,
    )


    print(
        f"  {colecao.count()} documentos "
        f"indexados na coleção "
        f"'{COLECAO_NOME}'."
    )

    return colecao


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================

def main(
    chunks_path: Path = CHUNKS_JSON,
    base_path: Path = BASE_VETORIAL,
):

    print(
        "=" * 60
    )

    print(
        "INDEXADOR VETORIAL "
        "— Sprint 2 / Genera"
    )

    print(
        "=" * 60
    )


    chunks_path = Path(
        chunks_path
    )

    base_path = Path(
        base_path
    )


    if not chunks_path.exists():

        print(
            "[ERRO] chunks.json "
            "não encontrado: "
            f"{chunks_path}"
        )

        print(
            "       Execute primeiro "
            "a geração dos embeddings."
        )

        sys.exit(
            1
        )


    print(
        "\n[1/3] Carregando chunks: "
        f"{chunks_path}"
    )

    chunks = (
        carregar_chunks(
            chunks_path
        )
    )

    print(
        f"      {len(chunks)} "
        "chunks carregados."
    )


    print(
        "[2/3] Indexando no "
        "ChromaDB em: "
        f"{base_path}"
    )

    colecao = (
        indexar(
            chunks,
            base_path,
        )
    )


    print(
        "[3/3] Verificando indexação..."
    )

    total = (
        colecao.count()
    )


    print(
        "\n[OK] Base vetorial "
        f"criada com {total} documentos."
    )

    print(
        "     Localização: "
        f"{base_path}"
    )


    return colecao


# =============================================================================
# EXECUÇÃO VIA TERMINAL
# =============================================================================

if __name__ == "__main__":

    entrada = (
        Path(
            sys.argv[1]
        )
        if len(sys.argv) > 1
        else CHUNKS_JSON
    )

    base = (
        Path(
            sys.argv[2]
        )
        if len(sys.argv) > 2
        else BASE_VETORIAL
    )

    main(
        entrada,
        base,
    )