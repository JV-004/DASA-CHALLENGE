"""
Módulo de NLP — Simplificação de Linguagem

Responsável por transformar textos técnicos do relatório genético
em explicações mais acessíveis para usuários leigos.

Também fornece métricas simples de legibilidade para comparar
o texto original com o texto simplificado.
"""

import re


TERMOS_TECNICOS = {
    "predisposição genética": "maior chance relacionada à genética",
    "variante genética": "alteração encontrada no DNA",
    "marcadores genéticos": "características analisadas no DNA",
    "fenótipo": "característica observável",
    "genótipo": "informação genética presente no DNA",
    "risco aumentado": "chance maior",
    "risco reduzido": "chance menor",
    "herdabilidade": "influência da genética sobre uma característica",
    "polimorfismo": "variação comum no DNA",
    "alelo": "versão de um gene",
}


def substituir_termo(texto: str, termo: str, explicacao: str) -> str:
    """
    Substitui um termo técnico sem diferenciar maiúsculas e minúsculas.
    Evita substituir partes internas de outras palavras.
    """

    padrao = re.compile(
        rf"\b{re.escape(termo)}\b",
        flags=re.IGNORECASE
    )

    return padrao.sub(explicacao, texto)


def simplificar_termos(texto: str) -> str:
    """
    Substitui termos técnicos conhecidos por explicações mais acessíveis.
    """

    texto_simplificado = texto

    # Substitui termos maiores primeiro
    termos_ordenados = sorted(
        TERMOS_TECNICOS.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )

    for termo, explicacao in termos_ordenados:
        texto_simplificado = substituir_termo(
            texto_simplificado,
            termo,
            explicacao
        )

    return texto_simplificado


def limpar_texto(texto: str) -> str:
    """
    Remove espaços duplicados e normaliza quebras de linha.
    """

    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n\s*\n", "\n", texto)

    return texto.strip()


def dividir_frases(texto: str) -> list:
    """
    Divide o texto em frases de forma simples.
    """

    frases = re.split(r"[.!?]+", texto)

    return [
        frase.strip()
        for frase in frases
        if frase.strip()
    ]


def calcular_metricas(texto: str) -> dict:
    """
    Calcula métricas simples de legibilidade.

    Retorna:
    - quantidade de palavras
    - quantidade de frases
    - média de palavras por frase
    - média de caracteres por palavra
    """

    palavras = re.findall(r"\b\w+\b", texto)
    frases = dividir_frases(texto)

    quantidade_palavras = len(palavras)
    quantidade_frases = len(frases)

    if quantidade_palavras == 0:
        media_caracteres = 0
    else:
        media_caracteres = sum(
            len(palavra)
            for palavra in palavras
        ) / quantidade_palavras

    if quantidade_frases == 0:
        media_palavras_frase = 0
    else:
        media_palavras_frase = (
            quantidade_palavras / quantidade_frases
        )

    return {
        "palavras": quantidade_palavras,
        "frases": quantidade_frases,
        "media_palavras_por_frase": round(
            media_palavras_frase,
            2
        ),
        "media_caracteres_por_palavra": round(
            media_caracteres,
            2
        ),
    }


def simplificar_texto(texto: str) -> dict:
    """
    Função principal do módulo.

    Recebe um texto técnico e retorna:
    - texto original
    - texto simplificado
    - métricas antes
    - métricas depois
    """

    if not texto or not texto.strip():
        return {
            "texto_original": "",
            "texto_simplificado": "",
            "metricas_original": {},
            "metricas_simplificado": {},
        }

    texto_original = limpar_texto(texto)

    texto_simplificado = simplificar_termos(
        texto_original
    )

    texto_simplificado = limpar_texto(
        texto_simplificado
    )

    return {
        "texto_original": texto_original,
        "texto_simplificado": texto_simplificado,
        "metricas_original": calcular_metricas(
            texto_original
        ),
        "metricas_simplificado": calcular_metricas(
            texto_simplificado
        ),
    }


if __name__ == "__main__":

    texto_teste = """
    O relatório identificou uma variante genética associada
    a uma predisposição genética para determinada condição.
    Esse resultado indica risco aumentado, mas não representa
    um diagnóstico definitivo.
    """

    resultado = simplificar_texto(texto_teste)

    print("\nTEXTO ORIGINAL:")
    print(resultado["texto_original"])

    print("\nTEXTO SIMPLIFICADO:")
    print(resultado["texto_simplificado"])

    print("\nMÉTRICAS DO TEXTO ORIGINAL:")
    print(resultado["metricas_original"])

    print("\nMÉTRICAS DO TEXTO SIMPLIFICADO:")
    print(resultado["metricas_simplificado"])
