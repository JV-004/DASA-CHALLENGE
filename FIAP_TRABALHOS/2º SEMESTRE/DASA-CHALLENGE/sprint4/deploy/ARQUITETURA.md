# Arquitetura de Produção — Genera AI

## Visão Geral

O Genera AI utiliza uma arquitetura baseada em Streamlit, integrando interface,
processamento de dados genéticos, embeddings, banco vetorial ChromaDB, RAG e
integração com modelo de linguagem.

## Arquitetura

```text
                    GitHub
                       │
                       ▼
              Controle de versão
                       │
                       ▼
                Pipeline de CI
                       │
                       ▼
              Ambiente de Produção
                       │
                       ▼
               Aplicação Streamlit
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
     Upload JSON    Pipeline RAG   OpenAI API
          │            │            │
          │        Embeddings        │
          │            │            │
          │         ChromaDB         │
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
              Resposta ao usuário
```

## Componentes

### Interface

A aplicação final utiliza Streamlit.

Entrypoint:

` sprint3/interface/app.py `

A interface é responsável por:

- apresentar o dashboard;
- receber relatórios JSON;
- iniciar o processamento;
- realizar perguntas ao assistente;
- apresentar respostas e fontes utilizadas.

## Pipeline RAG

O pipeline localizado na Sprint 2 é responsável por:

1. receber o relatório;
2. gerar chunks;
3. gerar embeddings;
4. indexar os dados no ChromaDB;
5. permitir busca semântica;
6. fornecer contexto para o modelo de linguagem.

## Banco Vetorial

A solução utiliza ChromaDB.

A base vetorial é um artefato gerado durante a execução e pode ser reconstruída
a partir do relatório original.

Por esse motivo, a base vetorial local não deve ser armazenada no GitHub.

## Integração com LLM

A aplicação utiliza a OpenAI API.

A credencial é obtida através da variável:

`OPENAI_API_KEY`

A chave nunca deve ser armazenada diretamente no código-fonte ou enviada ao
repositório Git.

## Ambientes

### Desenvolvimento

O ambiente de desenvolvimento utiliza:

- execução local;
- arquivo `.env` local;
- dados controlados;
- testes antes do envio para produção.

### Produção

O ambiente de produção deverá utilizar:

- aplicação hospedada em serviço cloud;
- variáveis de ambiente/secrets;
- código vindo da branch principal aprovada;
- logs de execução;
- monitoramento;
- dados temporários não versionados.

## Proteção de Dados

Por trabalhar com informações genéticas, foram adotadas medidas para impedir o
versionamento acidental de dados sensíveis.

São ignorados pelo Git:

```text
sprint3/interface/uploads/
sprint3/interface/runtime/
sprint4/logs/
sprint2/vetorial/base_vetorial/
sprint2/embeddings/chunks.json
.streamlit/secrets.toml
.env
```

## Estado Atual

A arquitetura atual funciona adequadamente como demonstrador.

Como melhoria para ambiente multiusuário, a base vetorial será isolada por
relatório ou sessão para impedir que uma execução substitua os dados vetoriais
utilizados por outra sessão.