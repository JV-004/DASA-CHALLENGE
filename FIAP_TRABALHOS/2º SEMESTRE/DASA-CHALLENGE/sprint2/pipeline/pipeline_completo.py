"""
Pipeline Completo — Sprint 2 / Genera / Dasa

Une:
1. extração de chunks;
2. geração de embeddings;
3. indexação vetorial.

O pipeline mantém compatibilidade com a Sprint 2, mas também
permite informar uma pasta de runtime exclusiva para cada relatório.

Uso antigo:
    python sprint2/pipeline/pipeline_completo.py

Uso com relatório:
    python sprint2/pipeline/pipeline_completo.py caminho/relatorio.json

Uso isolado por relatório:
    python sprint2/pipeline/pipeline_completo.py caminho/relatorio.json caminho/runtime
"""

import importlib.util
import sys
import time
from pathlib import Path


# =============================================================================
# CAMINHOS
# =============================================================================

RAIZ = Path(__file__).resolve().parents[2]

JSON_PADRAO = (
    RAIZ
    / "dados_estruturados.json"
)

CHUNKS_PADRAO = (
    RAIZ
    / "sprint2"
    / "embeddings"
    / "chunks.json"
)

BASE_VETORIAL_PADRAO = (
    RAIZ
    / "sprint2"
    / "vetorial"
    / "base_vetorial"
)


# =============================================================================
# IMPORTAÇÃO DOS MÓDULOS DAS ETAPAS
# =============================================================================

def _importar(
    caminho_relativo: str,
):
    caminho = (
        RAIZ
        / caminho_relativo
    )

    spec = (
        importlib.util.spec_from_file_location(
            "modulo",
            caminho,
        )
    )

    if (
        spec is None
        or spec.loader is None
    ):
        raise ImportError(
            "Não foi possível carregar "
            f"o módulo: {caminho}"
        )

    modulo = (
        importlib.util.module_from_spec(
            spec
        )
    )

    spec.loader.exec_module(
        modulo
    )

    return modulo


# =============================================================================
# PIPELINE
# =============================================================================

def executar_pipeline(
    caminho_json: Path,
    runtime_dir: Path | None = None,
):

    inicio = (
        time.time()
    )

    caminho_json = Path(
        caminho_json
    )


    # -------------------------------------------------------------------------
    # DEFINE OS CAMINHOS DE EXECUÇÃO
    # -------------------------------------------------------------------------

    if runtime_dir is None:

        chunks_path = (
            CHUNKS_PADRAO
        )

        base_path = (
            BASE_VETORIAL_PADRAO
        )

        modo_execucao = (
            "compatibilidade Sprint 2"
        )

    else:

        runtime_dir = Path(
            runtime_dir
        )

        runtime_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        chunks_path = (
            runtime_dir
            / "chunks.json"
        )

        base_path = (
            runtime_dir
            / "chromadb"
        )

        modo_execucao = (
            "runtime isolado"
        )


    # -------------------------------------------------------------------------
    # CABEÇALHO
    # -------------------------------------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "PIPELINE COMPLETO "
        "— Sprint 2 / Genera / Dasa"
    )

    print(
        "=" * 60
    )

    print(
        "Arquivo de entrada: "
        f"{caminho_json}"
    )

    print(
        "Modo: "
        f"{modo_execucao}"
    )

    print(
        "Chunks: "
        f"{chunks_path}"
    )

    print(
        "Base vetorial: "
        f"{base_path}\n"
    )


    # -------------------------------------------------------------------------
    # VALIDAÇÃO DO RELATÓRIO
    # -------------------------------------------------------------------------

    if not caminho_json.exists():

        raise FileNotFoundError(
            "Arquivo de relatório "
            "não encontrado: "
            f"{caminho_json}"
        )


    # -------------------------------------------------------------------------
    # ETAPA 1 — EMBEDDINGS
    # -------------------------------------------------------------------------

    print(
        ">>> ETAPA 1: "
        "Geração de Embeddings"
    )

    modulo_embeddings = (
        _importar(
            "sprint2/embeddings/"
            "gerar_embeddings.py"
        )
    )

    chunks = (
        modulo_embeddings.main(
            caminho_json,
            chunks_path,
        )
    )


    # -------------------------------------------------------------------------
    # ETAPA 2 — INDEXAÇÃO
    # -------------------------------------------------------------------------

    print(
        "\n>>> ETAPA 2: "
        "Indexação Vetorial"
    )

    modulo_indexacao = (
        _importar(
            "sprint2/vetorial/"
            "indexar.py"
        )
    )

    colecao = (
        modulo_indexacao.main(
            chunks_path,
            base_path,
        )
    )


    # -------------------------------------------------------------------------
    # RESULTADO
    # -------------------------------------------------------------------------

    duracao = (
        time.time()
        - inicio
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "PIPELINE CONCLUÍDO "
        f"em {duracao:.1f}s"
    )

    print(
        "  Chunks gerados: "
        f"{len(chunks)}"
    )

    print(
        "  Documentos indexados: "
        f"{colecao.count()}"
    )

    print(
        "  Arquivo de chunks: "
        f"{chunks_path}"
    )

    print(
        "  Base vetorial: "
        f"{base_path}"
    )

    print(
        "  Pronto para busca semântica."
    )

    print(
        "=" * 60
    )


    return {
        "chunks":
            chunks,

        "chunks_path":
            chunks_path,

        "base_path":
            base_path,

        "total_documentos":
            colecao.count(),

        "duracao_segundos":
            duracao,
    }


# =============================================================================
# EXECUÇÃO VIA TERMINAL
# =============================================================================

if __name__ == "__main__":

    caminho = (
        Path(
            sys.argv[1]
        )
        if len(sys.argv) > 1
        else JSON_PADRAO
    )

    runtime = (
        Path(
            sys.argv[2]
        )
        if len(sys.argv) > 2
        else None
    )

    executar_pipeline(
        caminho,
        runtime,
    )