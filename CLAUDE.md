# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Visão geral

Projeto acadêmico FIAP para a Dasa/Genera: transforma relatórios genéticos em PDF em uma experiência interativa via RAG (Retrieval-Augmented Generation). A Sprint 1 é majoritariamente documentação (problema, schema de dados, arquitetura conceitual). A Sprint 2 (`sprint2/`) contém a implementação real, dividida por integrante: pipeline de embeddings + indexação vetorial ChromaDB (`embeddings/`, `vetorial/`, `pipeline/`), agente especialista com guardrails (`agente/`) e interface Streamlit conectada à API OpenAI real (`interface/`). O agente em si (`agente_especialista.responder()`) continua usando uma resposta **simulada** — quem chama o LLM de verdade (GPT-4.1 Mini) é a camada separada `sprint2/interface/llm_connector.py`, usada pelo `app.py`.

## Comandos

### Setup
```
pip install -r requirements.txt
```
Instala as dependências do pipeline (chromadb, sentence-transformers) e da interface (streamlit, openai, python-dotenv). A interface também tem seu próprio `sprint2/interface/requirements_interface.txt` com o mesmo conteúdo, documentado separadamente no README do integrante 4.

### Pipeline completo (gera embeddings + indexa no ChromaDB)
```
python sprint2/pipeline/pipeline_completo.py [caminho/para/relatorio.json]
```
Sem argumento, usa `dados_estruturados.json` da raiz. Apaga e recria a coleção ChromaDB inteira a cada execução (reindexação completa, ~15s) — é o comando a rodar sempre que `dados_estruturados.json` mudar.

### Etapas individuais do pipeline
```
python sprint2/embeddings/gerar_embeddings.py [caminho/para/relatorio.json]   # gera sprint2/embeddings/chunks.json
python sprint2/vetorial/indexar.py [caminho/para/chunks.json]                 # indexa em sprint2/vetorial/base_vetorial/
```

### Busca semântica
```
python sprint2/testes/testar_busca.py   # roda um conjunto fixo de perguntas contra a base já indexada
python sprint2/vetorial/buscar.py       # busca interativa via input() no terminal
```
Ambos exigem que o pipeline já tenha sido rodado localmente (base vetorial não é versionada).

### Testes do agente
```
python sprint2/agente/testes_agente.py
```
Não há framework de testes (pytest etc.) configurado — é um script de validação manual que imprime o resultado no console (não existe nenhum arquivo `test_*.py`/`*_test.py` no repo, então `pytest` não coleta nada aqui).

### Interface (Streamlit + OpenAI real)
```
cp sprint2/interface/.env.example sprint2/interface/.env   # preencher OPENAI_API_KEY=sk-...
python sprint2/pipeline/pipeline_completo.py                # gerar a base vetorial antes do primeiro uso
streamlit run sprint2/interface/app.py
```
A API key também pode ser digitada direto na sidebar da interface, sem `.env`.

### CI (GitHub Actions)
`.github/workflows/python-app.yml` roda `flake8` e depois `pytest` a cada push/PR em `main`; `.github/workflows/pylint.yml` roda `pylint` sobre todo `.py` versionado. Ambos foram adicionados por outro integrante e ainda não foram validados neste ambiente — o passo `pytest` deve falhar por não haver nenhum teste no formato que o pytest reconhece (ver acima).

## Arquitetura

### Pipeline de dados ponta a ponta
```
relatorio PDF (relatorio_genera_simulado.pdf)
   ↓ extração conceitual — documentada em README_engenheiro_dados.md, não implementada em código
dados_estruturados.json          fonte única de verdade: dados do paciente, resultados, ancestralidade, metadata
   ↓ sprint2/embeddings/gerar_embeddings.py
sprint2/embeddings/chunks.json   chunks semânticos + embeddings (all-MiniLM-L6-v2, 384 dim) — gerado, git-ignored
   ↓ sprint2/vetorial/indexar.py
sprint2/vetorial/base_vetorial/  ChromaDB persistente, coleção "genera_relatorio", distância cosseno — gerado, git-ignored
   ↓ sprint2/vetorial/buscar.py (buscar_trechos / buscar_contexto)
sprint2/agente/agente_especialista.py (responder())
   ↓
resposta (hoje simulada) + fontes rastreáveis
```
`sprint2/pipeline/pipeline_completo.py` carrega os módulos de embeddings e indexação dinamicamente via `importlib` (não por import normal) e roda as duas etapas em sequência.

### Chunking (`gerar_embeddings.py`)
Cada item de `resultados[]` no JSON gera até 3 chunks, um por perfil de consumo:
- `resultado_{id}` — descrição simples + impacto prático (paciente)
- `recomendacao_{id}` — recomendação clínica + urgência
- `marcadores_{id}` — marcadores genéticos + descrição técnica (médico)

Mais chunks fixos de `paciente`, `sumario`, `ancestralidade` e `metadata`. Todo chunk carrega um campo `fonte` rastreável até o caminho de origem no JSON, usado depois para citar a fonte nas respostas do agente.

### Agente especialista (`sprint2/agente/`)
Fluxo de `agente_especialista.responder()`: pergunta → `guardrails.verificar_guardrails()` (bloqueia diagnóstico/prescrição/risco alto/fora de escopo por matching de termos em português) → `guardrails.validar_contexto()` (garante que há trechos recuperados) → `construir_prompt_final()` (combina `prompts.SYSTEM_PROMPT` + modo + contexto + pergunta) → `gerar_resposta_simulada()` (placeholder fixo, não chama LLM real).

- `config_llm.py` guarda os parâmetros do modelo alvo (GPT-4.1 Mini / Gemini Flash) e flags de comportamento. Dentro do próprio módulo do agente eles não são usados (a resposta é simulada); é `sprint2/interface/llm_connector.py` que importa `MODELO`, `TEMPERATURA`, `TOP_P`, `MAX_TOKENS` daqui para a chamada real à API OpenAI.
- Dois modos de resposta — `paciente` (linguagem simples) e `tecnico` (linguagem detalhada) — selecionados por parâmetro explícito, não por detecção automática de perfil.
- Guardrails em `guardrails.py` são listas de termos (`TERMOS_DIAGNOSTICO`, `TERMOS_PRESCRICAO`, `TERMOS_RISCO_ALTO`, `TERMOS_FORA_ESCOPO`) checadas por substring, case-insensitive — não é um classificador.

### Interface (`sprint2/interface/`)
`app.py` (Streamlit) orquestra o fluxo completo end-to-end: carrega/roda o pipeline, chama `buscar_contexto()` (`sprint2/vetorial/buscar.py`) para recuperar trechos, passa o resultado para `responder()` do agente para aplicar guardrails e montar o prompt, e então usa `llm_connector.chamar_openai()` — em vez de `gerar_resposta_simulada()` — para gerar a resposta final com GPT-4.1 Mini. `llm_connector.py` só chama a API quando o status do agente não é `bloqueado`/`sem_contexto`, ou seja, os guardrails decidem antes de qualquer gasto de tokens.

### Imports entre módulos que não formam um pacote Python
`sprint2/agente/agente_especialista.py` e `sprint2/agente/testes_agente.py` usam imports diretos (`from prompts import ...`, `from agente_especialista import responder`) sem prefixo de pacote. Isso só resolve porque quem importa insere manualmente `sprint2/agente` no `sys.path` antes do import — é o que `app.py` e `llm_connector.py` fazem explicitamente (`sys.path.insert(0, ...)`), e o que acontece automaticamente ao rodar `python sprint2/agente/arquivo.py` diretamente (Python adiciona o diretório do script ao `sys.path`). Importar esses módulos de qualquer outro lugar sem esse ajuste quebra. `sprint2/testes/testar_busca.py` já resolve isso de forma diferente, adicionando a raiz do repo ao `sys.path` para importar via `sprint2.vetorial.buscar`.

### `dados_estruturados.json`
Schema único consumido por toda a Sprint 2: `paciente` → `sumario` → `resultados[]` (`doenca`, `categoria`, `risco`, `marcadores_geneticos[]`, `escore_poligênico_percentil`, `descricao_tecnica`, `descricao_simples`, `recomendacao`, `urgencia_medica`) → `ancestralidade[]` → `metadata`. Detalhado em `README_engenheiro_dados.md` e `mapeamento_secoes.md`.

### Documentação do produto
A especificação de produto (problema, justificativa de RAG, guard rails de negócio para saúde, UX, governança/LGPD) está em `README.md`, `README_engenheiro_dados.md`, `sprint2/README_sprint2.md` e `sprint2/agente/README_agente.md`. Decisões já fixadas nesses documentos (modelo de embeddings `all-MiniLM-L6-v2`, LLM alvo GPT-4.1 Mini/Gemini Flash, regras de guardrail) devem ser respeitadas ao alterar o código, a menos que o usuário peça explicitamente para revisá-las.
