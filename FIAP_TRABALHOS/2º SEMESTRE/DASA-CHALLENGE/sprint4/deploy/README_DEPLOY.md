# Sprint 4 — Deploy e DevOps

## Genera AI — Challenge DASA

Este documento descreve a preparação, configuração e estratégia de deploy da
aplicação Genera AI durante a Sprint 4.

## Responsabilidade DevOps

A etapa de Deploy e DevOps tem como objetivos:

- preparar a aplicação para ambiente de produção;
- separar arquivos de desenvolvimento e runtime;
- proteger credenciais e informações sensíveis;
- garantir uma execução reproduzível;
- validar o funcionamento ponta a ponta;
- documentar o processo de publicação;
- preparar automações e integração contínua.

## Aplicação

A aplicação final é executada através de:

```text
sprint3/interface/app.py
```

Tecnologia principal:

```text
Streamlit
```

O Streamlit concentra interface e servidor Python na mesma aplicação.

Por isso, não é necessário separar artificialmente o projeto em frontend e
backend independentes para esta versão.

## Dependências

As principais dependências são:

```text
streamlit
chromadb
sentence-transformers
openai
python-dotenv
```

As dependências principais também foram disponibilizadas em:

```text
sprint3/interface/requirements.txt
```

para facilitar o processo de publicação da aplicação.

## Execução Local

A partir da pasta:

```text
FIAP_TRABALHOS/2º SEMESTRE/DASA-CHALLENGE
```

crie o ambiente virtual:

```powershell
python -m venv .venv
```

Ative:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

Execute a aplicação:

```powershell
streamlit run sprint3/interface/app.py
```

O endereço local padrão é:

```text
http://localhost:8501
```

## Secrets e Variáveis de Ambiente

A chave da OpenAI não deve ser colocada no repositório.

Variável utilizada:

```text
OPENAI_API_KEY
```

Também é possível manter:

```text
GOVERNANCE_LOG_CONTENT=false
```

para impedir que conteúdo sensível seja incluído nos logs de governança.

## Arquivos Temporários

Os seguintes arquivos e diretórios são considerados dados de runtime:

```text
sprint3/interface/uploads/
sprint3/interface/runtime/
sprint4/logs/
sprint2/vetorial/base_vetorial/
sprint2/embeddings/chunks.json
```

Eles não devem ser enviados ao GitHub.

## Segurança

O arquivo `.gitignore` foi atualizado para evitar o versionamento de:

- uploads de usuários;
- bases vetoriais;
- arquivos temporários;
- logs;
- secrets;
- arquivos `.env`.

Essa configuração reduz o risco de exposição de informações genéticas ou
credenciais de serviços externos.

## Otimização do Modelo de Embeddings

O carregamento do modelo `all-MiniLM-L6-v2` utiliza cache em memória.

Dessa forma, o modelo não precisa ser carregado novamente para cada pergunta
realizada durante a mesma execução da aplicação.

Isso reduz:

- tempo de resposta;
- consumo desnecessário de CPU;
- tempo de processamento.

## Fluxo de Produção

```text
Usuário
   │
   ▼
Streamlit
   │
   ▼
Upload JSON
   │
   ▼
Pipeline de processamento
   │
   ├── Chunks
   ├── Embeddings
   └── ChromaDB
   │
   ▼
Busca Semântica / RAG
   │
   ▼
OpenAI
   │
   ▼
Validação / Governança
   │
   ▼
Resposta apresentada ao usuário
```

## Checklist de Deploy

- [ ] aplicação executada localmente;
- [ ] dependências instaladas;
- [ ] upload JSON funcionando;
- [ ] pipeline de embeddings funcionando;
- [ ] ChromaDB funcionando;
- [ ] busca semântica funcionando;
- [ ] integração OpenAI funcionando;
- [ ] API Key armazenada como secret;
- [ ] `.gitignore` revisado;
- [ ] deploy remoto realizado;
- [ ] teste ponta a ponta realizado;
- [ ] evidências do deploy armazenadas;
- [ ] CI configurado;
- [ ] README final atualizado.

## Evidências

As evidências relacionadas ao deploy deverão ser armazenadas em:

```text
sprint4/evidencias/
```

Sugestão de evidências:

```text
deploy_01_build
deploy_02_aplicacao_online
deploy_03_secrets
deploy_04_upload
deploy_05_pipeline
deploy_06_resposta_rag
deploy_07_logs
deploy_08_ci
```

Nenhuma captura deverá revelar a chave da OpenAI.

## Próximas Etapas

As próximas etapas do trabalho de DevOps são:

1. isolamento do ChromaDB por relatório;
2. teste completo local;
3. configuração de integração contínua;
4. publicação da aplicação;
5. configuração de secrets;
6. testes em produção;
7. geração das evidências da Sprint 4.