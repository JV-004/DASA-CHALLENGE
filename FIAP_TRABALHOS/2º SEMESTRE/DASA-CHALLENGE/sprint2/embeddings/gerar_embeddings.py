"""
Gerador de Embeddings — Sprint 2 / Genera / Dasa
Lê o dados_estruturados.json do Sprint 1, divide em chunks e gera embeddings.
"""

import json
import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer


# ── Caminhos ──────────────────────────────────────────────────────────────────

RAIZ = Path(__file__).resolve().parents[2]

JSON_ENTRADA = (
    RAIZ
    / "dados_estruturados.json"
)

JSON_SAIDA = (
    Path(__file__).parent
    / "chunks.json"
)

MODELO_NOME = "all-MiniLM-L6-v2"


# =============================================================================
# CARREGAMENTO DO RELATÓRIO
# =============================================================================

def carregar_relatorio(
    caminho: Path,
) -> dict:

    with open(
        caminho,
        "r",
        encoding="utf-8",
    ) as arquivo:

        return json.load(
            arquivo
        )


# =============================================================================
# GERAÇÃO DOS CHUNKS
# =============================================================================

def gerar_chunks(
    relatorio: dict,
) -> list[dict]:

    """
    Divide o relatório em chunks
    semânticos com metadados.
    """

    chunks = []

    idx = 0


    # ── Paciente ──────────────────────────────────────────────────────────────

    paciente = (
        relatorio.get(
            "paciente",
            {},
        )
    )

    chunks.append(
        {
            "id":
                f"chunk_{idx:03d}",

            "secao":
                "paciente",

            "fonte":
                (
                    "dados_estruturados.json "
                    "> paciente"
                ),

            "conteudo":
                (
                    f"Paciente: "
                    f"{paciente.get('nome', '')}. "

                    f"Data de nascimento: "
                    f"{paciente.get('data_nascimento', '')}. "

                    f"ID do relatório: "
                    f"{paciente.get('id_relatorio', '')}. "

                    f"Data do exame: "
                    f"{paciente.get('data_exame', '')}. "

                    f"Médico solicitante: "
                    f"{paciente.get('medico_solicitante', '')}."
                ),
        }
    )

    idx += 1


    # ── Sumário ───────────────────────────────────────────────────────────────

    sumario = (
        relatorio.get(
            "sumario",
            {},
        )
    )

    recomendacoes = (
        sumario.get(
            "recomendacoes_prioritarias",
            [],
        )
    )

    chunks.append(
        {
            "id":
                f"chunk_{idx:03d}",

            "secao":
                "sumario",

            "fonte":
                (
                    "dados_estruturados.json "
                    "> sumario"
                ),

            "conteudo":
                (
                    f"Resumo do relatório genético: "
                    f"{sumario.get('resumo_executivo_paciente', '')} "

                    f"Total de condições analisadas: "
                    f"{sumario.get('total_condicoes_analisadas', '')}. "

                    f"Condições de risco alto: "
                    f"{sumario.get('condicoes_alto_risco', '')}. "

                    f"Condições de risco médio: "
                    f"{sumario.get('condicoes_medio_risco', '')}. "

                    f"Condições de risco baixo: "
                    f"{sumario.get('condicoes_baixo_risco', '')}. "

                    f"Recomendações prioritárias: "
                    f"{'; '.join(recomendacoes)}."
                ),
        }
    )

    idx += 1


    # ── Resultados ────────────────────────────────────────────────────────────

    for resultado in (
        relatorio.get(
            "resultados",
            [],
        )
    ):

        doenca = (
            resultado.get(
                "doenca",
                "",
            )
        )

        risco = (
            resultado.get(
                "risco",
                "",
            )
        )

        categoria = (
            resultado.get(
                "categoria",
                "",
            )
        )


        # Chunk de descrição simples + impacto

        chunks.append(
            {
                "id":
                    f"chunk_{idx:03d}",

                "secao":
                    (
                        "resultado_"
                        f"{resultado.get('id', '')}"
                    ),

                "fonte":
                    (
                        "dados_estruturados.json "
                        f"> resultados > {doenca}"
                    ),

                "conteudo":
                    (
                        f"Condição: {doenca}. "

                        f"Categoria: {categoria}. "

                        f"Nível de risco: {risco}. "

                        f"{resultado.get('descricao_simples', '')} "

                        f"{resultado.get('impacto_pratico', '')}"
                    ),
            }
        )

        idx += 1


        # Chunk de recomendação + urgência

        chunks.append(
            {
                "id":
                    f"chunk_{idx:03d}",

                "secao":
                    (
                        "recomendacao_"
                        f"{resultado.get('id', '')}"
                    ),

                "fonte":
                    (
                        "dados_estruturados.json "
                        f"> resultados > {doenca} "
                        "> recomendacao"
                    ),

                "conteudo":
                    (
                        f"Recomendação para {doenca} "
                        f"(risco {risco}): "

                        f"{resultado.get('recomendacao', '')} "

                        f"Urgência: "
                        f"{resultado.get('urgencia_medica', '')}."
                    ),
            }
        )

        idx += 1


        # Chunk técnico com marcadores genéticos

        marcadores = (
            resultado.get(
                "marcadores_geneticos",
                [],
            )
        )

        marcadores_txt = "; ".join(
            (
                f"{marcador.get('id_snp', '')} "
                f"({marcador.get('gene', '')}) "
                f"alelo {marcador.get('alelo', '')} — "
                f"{marcador.get('observacao', '')}"
            )
            for marcador in marcadores
        )

        if marcadores_txt:

            chunks.append(
                {
                    "id":
                        f"chunk_{idx:03d}",

                    "secao":
                        (
                            "marcadores_"
                            f"{resultado.get('id', '')}"
                        ),

                    "fonte":
                        (
                            "dados_estruturados.json "
                            f"> resultados > {doenca} "
                            "> marcadores_geneticos"
                        ),

                    "conteudo":
                        (
                            f"Marcadores genéticos "
                            f"para {doenca}: "
                            f"{marcadores_txt}. "

                            f"Descrição técnica: "
                            f"{resultado.get('descricao_tecnica', '')}"
                        ),
                }
            )

            idx += 1


    # ── Ancestralidade ────────────────────────────────────────────────────────

    ancestralidade = (
        relatorio.get(
            "ancestralidade",
            [],
        )
    )

    if ancestralidade:

        ancestralidade_txt = "; ".join(
            (
                f"{item.get('regiao', '')}: "
                f"{item.get('percentual', '')}%"
            )
            for item in ancestralidade
        )

        chunks.append(
            {
                "id":
                    f"chunk_{idx:03d}",

                "secao":
                    "ancestralidade",

                "fonte":
                    (
                        "dados_estruturados.json "
                        "> ancestralidade"
                    ),

                "conteudo":
                    (
                        "Composição ancestral do paciente: "
                        f"{ancestralidade_txt}."
                    ),
            }
        )

        idx += 1


    # ── Metadados ─────────────────────────────────────────────────────────────

    metadata = (
        relatorio.get(
            "metadata",
            {},
        )
    )

    chunks.append(
        {
            "id":
                f"chunk_{idx:03d}",

            "secao":
                "metadata",

            "fonte":
                (
                    "dados_estruturados.json "
                    "> metadata"
                ),

            "conteudo":
                (
                    f"Relatório emitido pelo laboratório "
                    f"{metadata.get('laboratorio', '')}. "

                    f"Responsável técnico: "
                    f"{metadata.get('responsavel_tecnico', '')} "
                    f"({metadata.get('crm_responsavel', '')}). "

                    f"Versão do relatório: "
                    f"{metadata.get('versao_relatorio', '')}. "

                    f"Data de processamento: "
                    f"{metadata.get('data_processamento', '')}."
                ),
        }
    )

    return chunks


# =============================================================================
# GERAÇÃO DOS EMBEDDINGS
# =============================================================================

def gerar_embeddings(
    chunks: list[dict],
    modelo: SentenceTransformer,
) -> list[dict]:

    print(
        f"  Gerando embeddings para "
        f"{len(chunks)} chunks..."
    )

    textos = [
        chunk["conteudo"]
        for chunk in chunks
    ]

    vetores_raw = (
        modelo.encode(
            textos,
            show_progress_bar=True,
        )
    )

    vetores = [
        vetor.tolist()
        for vetor in vetores_raw
    ]

    for chunk, vetor in zip(
        chunks,
        vetores,
    ):

        chunk["embedding"] = (
            vetor
        )

    return chunks


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================

def main(
    caminho_json: Path = JSON_ENTRADA,
    caminho_saida: Path = JSON_SAIDA,
):

    print(
        "=" * 60
    )

    print(
        "GERADOR DE EMBEDDINGS "
        "— Sprint 2 / Genera"
    )

    print(
        "=" * 60
    )

    caminho_json = Path(
        caminho_json
    )

    caminho_saida = Path(
        caminho_saida
    )

    if not caminho_json.exists():

        print(
            "[ERRO] Arquivo não encontrado: "
            f"{caminho_json}"
        )

        sys.exit(
            1
        )


    print(
        f"\n[1/4] Carregando relatório: "
        f"{caminho_json}"
    )

    relatorio = (
        carregar_relatorio(
            caminho_json
        )
    )


    print(
        "[2/4] Dividindo em chunks semânticos..."
    )

    chunks = (
        gerar_chunks(
            relatorio
        )
    )

    print(
        f"      {len(chunks)} "
        "chunks gerados."
    )


    print(
        "[3/4] Carregando modelo "
        f"de embeddings: {MODELO_NOME}"
    )

    modelo = (
        SentenceTransformer(
            MODELO_NOME
        )
    )


    print(
        "[4/4] Gerando embeddings..."
    )

    chunks_com_embeddings = (
        gerar_embeddings(
            chunks,
            modelo,
        )
    )


    caminho_saida.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        caminho_saida,
        "w",
        encoding="utf-8",
    ) as arquivo:

        json.dump(
            chunks_com_embeddings,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )


    print(
        "\n[OK] chunks.json salvo em: "
        f"{caminho_saida}"
    )

    print(
        "     Total de chunks: "
        f"{len(chunks_com_embeddings)}"
    )

    print(
        "     Dimensão dos embeddings: "
        f"{len(chunks_com_embeddings[0]['embedding'])}"
    )

    return chunks_com_embeddings


# =============================================================================
# EXECUÇÃO VIA TERMINAL
# =============================================================================

if __name__ == "__main__":

    entrada = (
        Path(
            sys.argv[1]
        )
        if len(sys.argv) > 1
        else JSON_ENTRADA
    )

    saida = (
        Path(
            sys.argv[2]
        )
        if len(sys.argv) > 2
        else JSON_SAIDA
    )

    main(
        entrada,
        saida,
    )