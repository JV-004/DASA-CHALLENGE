<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="docs/images/logo-fiap.png" alt="FIAP" width="35%"/>
  </a>
</p>

<h1 align="center">Projeto Genera · Dasa</h1>
<h3 align="center">Sprint 2 — Fase de Inteligência do Sistema</h3>
<h4 align="center">Transformando relatórios genéticos em uma experiência conversacional inteligente</h4>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python"/>
  <img src="https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square&logo=streamlit"/>
  <img src="https://img.shields.io/badge/ChromaDB-vetorial-green?style=flat-square"/>
  <img src="https://img.shields.io/badge/RAG-LLM-purple?style=flat-square"/>
  <img src="https://img.shields.io/badge/LGPD-compliant-orange?style=flat-square"/>
</p>

---

## 👨‍🎓 Equipe

| Nome | RM |  Sprint 2 |
|---|---:|---|
| João | RM565999 | Integrante 1 · Minerador de Dados (Embeddings + Base Vetorial) |
| Endrew Alves | RM563646 |Integrantes 2 · Arquiteto da Busca |
| Tayná Esteves | RM562491 |Integrantes 3 · Domador do Agente |
| Carlos Eduardo | RM566487 | Integrante 4 · Construtor da Experiência (Interface + Integração LLM) |



### 👩‍🏫 Professores

**Tutor:** [John Paul Lima](https://www.linkedin.com/in/john-paul-lima/)  
**Coordenador:** [André Godoi Chiovato](https://www.linkedin.com/in/andregodoichiovato/)

---

## 📋 Índice

1. [O que foi construído nesta Sprint](#1-o-que-foi-construído-nesta-sprint)
2. [Como o sistema funciona — visão geral](#2-como-o-sistema-funciona--visão-geral)
3. [Arquitetura completa](#3-arquitetura-completa)
4. [Integrante 1 — Minerador de Dados](#4-integrante-1--minerador-de-dados)
5. [Integrante 2 — Arquiteto da Busca](#5-integrante-2--arquiteto-da-busca)
6. [Integrante 3 — Domador do Agente](#6-integrante-3--domador-do-agente)
7. [Integrante 4 — Construtor da Experiência](#7-integrante-4--construtor-da-experiência)
8. [Como executar o projeto](#8-como-executar-o-projeto)
9. [Estrutura do repositório](#9-estrutura-do-repositório)
10. [Governança, Ética e LGPD](#10-governança-ética-e-lgpd)
11. [Continuidade — da Sprint 1 para a Sprint 2](#11-continuidade--da-sprint-1-para-a-sprint-2)
12. [Vídeo de apresentação](#12-vídeo-de-apresentação)
13. [Sprint 3 — Personalização do RAG](#13-sprint-3--personalização-do-rag)

---

## 1. O que foi construído nesta Sprint

A Sprint 1 resolveu o problema da estruturação: transformar o PDF do relatório genético Genera em um JSON organizado e legível por máquina.

**A Sprint 2 constrói a inteligência sobre esses dados.**

Nesta fase foram implementados quatro componentes que, conectados em sequência, permitem que qualquer pessoa possa conversar com seu próprio relatório genético em linguagem natural:

| Componente | O que faz |
|---|---|
| **Pipeline de Embeddings** | Divide o JSON em unidades semânticas e gera representações vetoriais |
| **Base Vetorial (ChromaDB)** | Armazena e indexa os vetores para busca por significado |
| **Busca Semântica** | Encontra os trechos do relatório mais relevantes para cada pergunta |
| **Agente Especialista + LLM** | Interpreta os trechos e responde em linguagem natural, com guardrails médicos |
| **Interface de Chat (Streamlit)** | Permite a interação do usuário com o sistema completo |

---

## 2. Como o sistema funciona — visão geral

> *"Você contratou um médico geneticista que leu seu relatório inteiro, memorizou tudo, e está pronto para responder qualquer pergunta — em português claro, sem jargão, sem te assustar. Mas esse médico é uma IA."*

**O fluxo em linguagem simples:**

```
Você digita uma pergunta
        ↓
O sistema busca no SEU relatório os trechos mais relevantes
        ↓
Esses trechos são entregues ao modelo de linguagem como contexto
        ↓
O modelo responde com base exclusivamente no que está no relatório
        ↓
A resposta aparece no chat — com as fontes que a embasaram
```

**Por que esse processo evita invenções?**  
Modelos de linguagem podem "completar frases" com informações que parecem verdadeiras mas não são — isso se chama alucinação. A arquitetura RAG (Retrieval-Augmented Generation) resolve isso: antes de responder, o sistema recupera os dados reais do relatório e os entrega ao modelo como contexto obrigatório. O modelo responde com base no que encontrou — não no que imagina.

---

## 3. Arquitetura completa

```
┌─────────────────────────────────────────────────────────────────────┐
│  SPRINT 1 (base herdada)                                            │
│  relatorio_genera_simulado.pdf  →  dados_estruturados.json          │
│  pdfplumber + PyMuPDF · limpeza · schema JSON padronizado           │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  INTEGRANTE 1 — Minerador de Dados                                  │
│  gerar_embeddings.py                                                │
│  dados_estruturados.json → 25 chunks semânticos → embeddings 384D  │
│  Modelo: all-MiniLM-L6-v2 (local, gratuito)                        │
│                                                                     │
│  indexar.py                                                         │
│  chunks.json → ChromaDB (distância cosseno, persistido em disco)   │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ base_vetorial/ pronta
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  INTEGRANTE 2 — Arquiteto da Busca                                  │
│  buscar.py · buscar_contexto()                                      │
│  pergunta → embedding → query ChromaDB → top-3 trechos             │
│  filtro: similaridade mínima 0.50 · retorna conteudo, secao,       │
│  fonte, similaridade                                                │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ trechos relevantes
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  INTEGRANTE 3 — Domador do Agente                                   │
│  guardrails.py → valida pergunta (diagnóstico? prescrição? escopo?) │
│  prompts.py → SYSTEM_PROMPT com tom, restrições e formato           │
│  agente_especialista.py → monta prompt final e orquestra resposta  │
│  config_llm.py: GPT-4.1 Mini · temp 0.2 · top_p 0.8 · 700 tokens  │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ prompt final estruturado
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  INTEGRANTE 4 — Construtor da Experiência                           │
│  llm_connector.py → chamada real à API OpenAI (GPT-4.1 Mini)       │
│  app.py (Streamlit) → chat, upload, fontes, disclaimers, guardrails │
│  Tema escuro genômico · modo paciente / técnico · rastreabilidade  │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
                          Usuário recebe resposta
                    com fontes e trechos do relatório
```

---

## 4. Integrante 1 — Minerador de Dados

> *"Eu transformo o caos em ordem."*

### O que foi feito

O Integrante 1 recebeu o `dados_estruturados.json` produzido na Sprint 1 e construiu o pipeline completo de vetorização — a infraestrutura que torna o relatório pesquisável por significado, não apenas por palavras-chave.

### Estratégia de chunking

Cada chunk representa uma **unidade semântica**, não um número fixo de caracteres. Para cada condição genética do relatório são gerados 3 chunks distintos:

| Chunk | Conteúdo | Para quem |
|---|---|---|
| `resultado_2.X` | Descrição simples + impacto prático | Paciente leigo |
| `recomendacao_2.X` | Recomendação clínica + urgência | Ações preventivas |
| `marcadores_2.X` | Marcadores genéticos + descrição técnica | Médico / perfil clínico |

Além disso, chunks específicos para: `paciente`, `sumario`, `ancestralidade` e `metadata`.

**Resultado: 25 chunks · 384 dimensões · distância cosseno**

### Decisões técnicas

**Por que ChromaDB?**  
Local e gratuito, sem dependência de serviço externo ou API key. Persiste em disco e reutiliza a base entre execuções. Distância cosseno configurada nativamente.

**Por que `all-MiniLM-L6-v2`?**  
Roda completamente offline após o primeiro download. Leve (384 dimensões), rápido e com boa qualidade para busca semântica em textos de saúde. Padrão da comunidade para RAG em projetos acadêmicos.

### Arquivos

| Arquivo | Função |
|---|---|
| `sprint2/embeddings/gerar_embeddings.py` | Divide o JSON em chunks e gera embeddings |
| `sprint2/vetorial/indexar.py` | Indexa os chunks no ChromaDB |
| `sprint2/pipeline/pipeline_completo.py` | Executa as duas etapas em sequência |
| `sprint2/testes/testar_busca.py` | Valida a busca com perguntas de exemplo |

---

## 5. Integrante 2 — Arquiteto da Busca

> *"Eu faço a IA achar a agulha no palheiro."*

### O que foi feito

O Integrante 2 implementou a camada de busca semântica que transforma uma pergunta em linguagem natural em trechos do relatório — a "ponte" entre a pergunta do usuário e o contexto que o LLM vai usar para responder.

### Como a busca funciona

```
Pergunta do usuário ("Tenho risco de diabetes?")
        ↓
Embedding da pergunta via all-MiniLM-L6-v2
        ↓
Query no ChromaDB: distância cosseno entre pergunta e todos os chunks
        ↓
Filtro: similaridade ≥ 0.50
        ↓
Top-3 chunks mais próximos semanticamente retornados
```

### Contrato da função principal

```python
from sprint2.vetorial.buscar import buscar_contexto

resultado = buscar_contexto(pergunta="Tenho risco de diabetes?", top_k=3)

# Retorna:
# {
#   "pergunta": str,
#   "encontrou_contexto": bool,
#   "trechos": [{"conteudo", "secao", "fonte", "similaridade"}],
#   "contexto": str  # trechos formatados prontos para o LLM
# }
```

### Parâmetros configurados

| Parâmetro | Valor | Justificativa |
|---|---|---|
| `top_k` | 3 | Equilíbrio entre contexto suficiente e janela do LLM |
| `similaridade_minima` | 0.50 | Evita trechos irrelevantes sem ser restritivo demais |
| Distância | Cosseno | Padrão para busca semântica — invariante à magnitude |

---

## 6. Integrante 3 — Domador do Agente

> *"Eu decido como a IA pensa e fala."*

### O que foi feito

O Integrante 3 construiu toda a lógica de comportamento do agente: como ele valida perguntas, monta o contexto, escolhe o tom e garante que nunca ultrapasse os limites de segurança médica.

### Modelo e hiperparâmetros

| Parâmetro | Valor | Justificativa |
|---|---|---|
| Modelo | GPT-4.1 Mini | Bom desempenho em português, baixo custo, adequado para RAG |
| Temperatura | 0.2 | Respostas consistentes e precisas, sem variação excessiva |
| Top-p | 0.8 | Vocabulário controlado |
| Max tokens | 700 | Respostas completas sem prolixidade |

### Guardrails implementados

O agente bloqueia categorias de perguntas **antes** de chamar o LLM:

| Categoria bloqueada | Exemplo | Resposta do agente |
|---|---|---|
| Diagnóstico | "Tenho câncer?" | Redireciona para profissional de saúde |
| Prescrição | "Qual remédio devo tomar?" | Recusa e explica o escopo |
| Previsão médica absoluta | "Quanto tempo vou viver?" | Contextualiza limitações da genética |
| Fora do relatório | "Qual dieta devo fazer?" | Informa que responde só sobre o relatório |
| Sem contexto suficiente | Nenhum chunk recuperado | Admite ausência de informação |

### Modos de resposta

**Modo Paciente:** linguagem simples, acolhedora, sem jargão, explica termos  
**Modo Técnico:** linguagem detalhada, terminologia genômica, voltado a profissionais

### Formato de resposta do agente

```
Resumo:       [resposta curta e direta]
Explicação:   [contextualização do dado genético]
Na prática:   [o que isso significa no dia a dia]
Baseado em:   [seções do relatório utilizadas]
```

### Arquivos

| Arquivo | Função |
|---|---|
| `sprint2/agente/agente_especialista.py` | Orquestrador do fluxo principal |
| `sprint2/agente/prompts.py` | SYSTEM_PROMPT, FALLBACK_PROMPT |
| `sprint2/agente/guardrails.py` | Validação de perguntas e contexto |
| `sprint2/agente/config_llm.py` | Modelo e hiperparâmetros |
| `sprint2/agente/testes_agente.py` | 9 casos de teste (normal, borda, bloqueio) |

---

## 7. Integrante 4 — Construtor da Experiência

> *"Eu faço tudo isso chegar até o usuário."*

### O que foi feito

O Integrante 4 conectou todos os módulos anteriores e entregou a interface funcional que o usuário final vê e usa. A contribuição central é o `llm_connector.py` — a camada que substitui a resposta simulada do agente pela chamada real à API OpenAI.

### Contribuição técnica central — `llm_connector.py`

O `agente_especialista.py` do Integrante 3 produz o prompt final mas usa uma função simulada para gerar a resposta. O `llm_connector.py` envolve essa lógica e faz a chamada real ao GPT-4.1 Mini, respeitando exatamente os hiperparâmetros definidos em `config_llm.py`, sem alterar nenhum arquivo dos outros integrantes.

### Interface — funcionalidades

**Sidebar:**
- Campo seguro para inserção da API key (se não configurada via `.env`)
- Upload de relatório JSON ou PDF
- Botão "Usar relatório de demonstração" (carrega `dados_estruturados.json`)
- Modo de resposta: Paciente / Técnico
- 5 botões de perguntas frequentes clicáveis
- Botão "Limpar conversa"
- Disclaimer de privacidade LGPD

**Área de chat:**
- Histórico persistente durante a sessão
- Respostas com efeito de streaming
- Expander "📄 Fontes utilizadas" em cada resposta — mostra os trechos exatos do relatório com seção, origem e barra de similaridade
- Mensagens distintas para respostas bloqueadas pelos guardrails

**Banner de disclaimer (sempre visível):**
> ⚠️ Este assistente é informativo e não substitui avaliação médica. As respostas são baseadas exclusivamente no seu relatório genético. Consulte sempre um médico geneticista.

### Arquivos

| Arquivo | Função |
|---|---|
| `sprint2/interface/app.py` | Interface Streamlit completa |
| `sprint2/interface/llm_connector.py` | Integração real com a API OpenAI |
| `requirements.txt` (raiz) | Dependências do projeto, incluindo as da interface |
| `sprint2/interface/.env.example` | Template de configuração da API key |
| `sprint2/interface/README_integrante4.md` | Documentação técnica do Integrante 4 |

---

## 8. Como executar o projeto

### Pré-requisitos

- Python 3.10 ou superior
- Conta na OpenAI com créditos disponíveis ([platform.openai.com](https://platform.openai.com))
- Git

### Instalação

```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd <nome-da-pasta>

# 2. Instalar dependências
pip install -r requirements.txt
```

### Configuração da API Key

```bash
# Copiar o arquivo de exemplo
cp sprint2/interface/.env.example sprint2/interface/.env

# Editar o arquivo e inserir sua chave
# OPENAI_API_KEY=sk-...
```

> A chave também pode ser inserida diretamente na sidebar da interface, sem necessidade do arquivo `.env`.

### Gerar a base vetorial (necessário apenas na primeira vez ou ao trocar relatório)

```bash
python sprint2/pipeline/pipeline_completo.py
```

Saída esperada:
```
PIPELINE CONCLUÍDO em ~15s
  Chunks gerados: 25
  Base vetorial: sprint2/vetorial/base_vetorial/
  Pronto para busca semântica.
```

### Iniciar a interface

```bash
streamlit run sprint2/interface/app.py
```

Acesse no navegador: `http://localhost:8501`

### Validar a busca (opcional)

```bash
python sprint2/testes/testar_busca.py
```

### Executar testes do agente (opcional)

```bash
cd sprint2/agente
python testes_agente.py
```

---

## 9. Estrutura do repositório

```
projeto/
│
├── dados_estruturados.json              ← JSON do relatório (gerado na Sprint 1, consumido pela Sprint 2)
├── README.md                            ← README geral
├── requirements.txt                     ← dependências do pipeline + interface
├── CLAUDE.md                            ← guia de contexto para agentes de IA no repositório
│
├── sprint1/
│   ├── README_engenheiro_dados.md       ← documentação do Engenheiro de Dados
│   ├── relatorio_genera_simulado.pdf    ← PDF original simulado
│   ├── mapeamento_secoes.md
│   ├── extracao_tecnica.md
│   ├── priorizacao_campos.md
│   └── exemplos_interacao.md
│
├── sprint2/
│   │
│   ├── embeddings/
│   │   ├── gerar_embeddings.py          ← divide JSON em chunks + embeddings
│   │   └── chunks.json                  ← gerado automaticamente [.gitignore]
│   │
│   ├── vetorial/
│   │   ├── indexar.py                   ← indexa chunks no ChromaDB
│   │   ├── buscar.py                    ← busca semântica (Integrante 2)
│   │   └── base_vetorial/               ← ChromaDB persistido [.gitignore]
│   │
│   ├── pipeline/
│   │   └── pipeline_completo.py         ← executa embeddings + indexação
│   │
│   ├── agente/
│   │   ├── agente_especialista.py       ← orquestrador do agente (Int. 3)
│   │   ├── config_llm.py                ← modelo e hiperparâmetros
│   │   ├── prompts.py                   ← SYSTEM_PROMPT e fallbacks
│   │   ├── guardrails.py                ← validação de segurança médica
│   │   └── testes_agente.py             ← 9 casos de teste
│   │
│   ├── testes/
│   │   └── testar_busca.py              ← valida busca semântica
│   │
│   ├── interface/
│   │   ├── app.py                       ← interface Streamlit (Int. 4)
│   │   ├── llm_connector.py             ← integração OpenAI
│   │   ├── .env.example
│   │   └── README_integrante4.md
│   │
│   └── README_sprint2.md                ← documentação técnica Sprint 2
│
└── docs/
    └── images/
        ├── logo-fiap.png
        └── arquitetura.png
```

> **Importante:** `chunks.json` e `base_vetorial/` estão no `.gitignore`. Cada membro do grupo deve rodar o pipeline localmente para gerá-los. Eles não são versionados por questões de tamanho e por conterem dados do relatório.

---

## 10. Governança, Ética e LGPD

### Limites do agente

O sistema foi projetado como **ferramenta educativa e explicativa** — não diagnóstica.

| O que o agente FAZ | O que o agente NÃO FAZ |
|---|---|
| ✅ Explica termos genéticos em linguagem simples | ❌ Emite diagnósticos médicos |
| ✅ Apresenta predisposições como tendências | ❌ Prescreve medicamentos ou tratamentos |
| ✅ Mostra as fontes de cada resposta | ❌ Responde fora do escopo do relatório |
| ✅ Admite quando não há informação suficiente | ❌ Completa lacunas com conhecimento externo |
| ✅ Redireciona para profissional quando necessário | ❌ Faz previsões médicas absolutas |

### Privacidade dos dados

- O relatório PDF é processado localmente e não é persistido no servidor
- A base vetorial é armazenada em disco local, nunca enviada para serviços externos
- Os únicos dados enviados externamente são os trechos relevantes do relatório + a pergunta, enviados à API OpenAI para geração da resposta
- Nenhuma informação pessoal é armazenada além da sessão ativa do Streamlit
- O arquivo `.env` com a API key está no `.gitignore` e nunca é versionado

### LGPD

A solução respeita os princípios da Lei Geral de Proteção de Dados (Art. 11 — dados sensíveis de saúde):
- Processamento limitado à finalidade informativa
- Dados genéticos não compartilhados com terceiros além da API OpenAI (necessário para a funcionalidade)
- Ausência de armazenamento persistente de dados pessoais

### Disclaimers obrigatórios

Exibidos em toda sessão, sem exceção:
- Banner permanente no topo da interface
- Sufixo automático em respostas sobre riscos de saúde
- Aviso na sidebar sobre natureza informativa (não diagnóstica) do assistente

---

## 11. Continuidade — da Sprint 1 para a Sprint 2

| Entregável | Sprint 1 | Sprint 2 |
|---|---|---|
| Relatório genético | PDF bruto | Indexado em base vetorial |
| Dados | JSON estruturado | 25 chunks com embeddings 384D |
| IA | Proposta conceitual | Pipeline RAG funcional |
| Busca | Inexistente | Busca semântica por cosseno |
| Agente | Inexistente | Guardrails + system prompt + LLM |
| Interface | Wireframe/conceito | Chat funcional em Streamlit |
| Governança | Descrita | Implementada (guardrails + disclaimers) |

---

## 12. Vídeo de apresentação

> 📹 **Sprint 1:** [https://youtu.be/0x63S_5DD_8](https://youtu.be/0x63S_5DD_8)

> 📹 **Sprint 2:** [https://youtu.be/z1Jqb33pSjU](https://youtu.be/z1Jqb33pSjU)

---

## 13. Sprint 3 — Personalização do RAG

> **Cientista de IA — Personalização & RAG** · `sprint3/rag_personalizacao/`

Camada que adapta as respostas ao **perfil** e ao **histórico** do usuário sem
permitir que o agente extrapole o conteúdo verificável do relatório genético.
Envolve o pipeline da Sprint 2 — **nenhum arquivo de `sprint2/` foi alterado**.

### Princípio

A personalização atua sobre a **forma** da resposta (tom, profundidade,
vocabulário, `top_k`), nunca sobre o **conteúdo** (fatos, números, marcadores,
nível de risco, veredito dos guardrails).

### Perfis

| Perfil | `modo` no agente | `top_k` | Direção |
|---|---|---|---|
| `leigo_ansioso` | `paciente` | 3 | Tom calmo, risco como tendência estatística, sem alarmismo |
| `leigo_curioso` | `paciente` | 4 | Linguagem simples + mecanismo biológico |
| `medico` | `tecnico` | 5 | Marcadores e escores como constam no relatório |

### Fluxo

```
pergunta + perfil + usuario_id
   ↓ guardrails sobre a pergunta CRUA        (bloqueio não gasta token)
   ↓ busca semântica com top_k do perfil     sprint2/vetorial/buscar.py
   ↓ pergunta personalizada (forma + continuidade)
   ↓ responder_com_llm()                     sprint2/interface/llm_connector.py
   ↓   ← sempre o caminho real GPT-4.1 Mini, nunca a resposta simulada
   ↓ validação de ancoragem no relatório
   ↓ registro no histórico
contrato estável v1.0
```

### Fidelidade ao relatório

Toda resposta passa por validação programática: números, percentuais, SNPs e
símbolos de gene presentes na resposta precisam aparecer nos trechos
recuperados. Política configurável — `sinalizar` (padrão, marca
`ancoragem.ancorado = False`) ou `bloquear` (substitui por mensagem segura).

### Uso

```python
from sprint3.rag_personalizacao import responder_personalizado

resultado = responder_personalizado(
    pergunta="Eu tenho risco de diabetes?",
    perfil="leigo_ansioso",
    usuario_id="paciente-001",
    api_key=OPENAI_API_KEY,
)
```

```bash
pytest sprint3/rag_personalizacao/ -v    # 32 testes, sem API key
pytest sprint3/integracao/ -v            # 19 testes da integração com o NLP
pytest                                   # 51 testes no total
```

### Histórico — ponto de troca

A persistência real (Integrante 1) ainda não existe. A camada usa
`HistoricoMemoria` / `HistoricoJSON` por trás da interface
`RepositorioHistorico`; quando a persistência real chegar, basta injetá-la —
nenhum arquivo da personalização muda.

### Relação com `sprint3/nlp/`

`sprint3/nlp/` é uma **integração paralela, ainda não coordenada** — não é
dependência desta camada, e o contrato acima não usa nenhuma chave daquele
módulo. Dois pontos em aberto estão documentados em
[`sprint3/rag_personalizacao/README_rag_personalizacao.md`](sprint3/rag_personalizacao/README_rag_personalizacao.md),
seção 7.

---

<p align="center">
  <sub>Projeto desenvolvido para a disciplina de Inteligência Artificial · FIAP 2026</sub><br/>
  <sub>Genera AI · Dasa · Grupo Sprint 2</sub>
</p>
