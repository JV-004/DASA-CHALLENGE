# Interface Sprint 3 — Genera AI

Esta pasta contém a evolução da interface da Sprint 2 para a fase de Experiência do Usuário da Sprint 3.

## O que foi implementado

- **Dashboard refinado** com indicadores de risco e visão geral do relatório.
- **Cards de resultados genéticos** usando os dados do `dados_estruturados.json`.
- **Visualização de ancestralidade** com barras proporcionais e intervalos de confiança.
- **Resumo automático do relatório** usando `sprint3/nlp/resumos_automaticos.py`.
- **Assistente conversacional** reaproveitando RAG, guardrails e OpenAI da Sprint 2.
- **Simplificação de linguagem** usando `sprint3/nlp/nlp_simplificacao.py` no modo paciente.
- **Histórico da sessão** e resumo automático das interações.
- **Comunicação responsável** com disclaimer persistente e rótulos visuais menos alarmistas.
- **Responsividade** para desktop e telas menores.

## Como executar

A partir da raiz do repositório:

```bash
pip install -r requirements.txt
streamlit run sprint3/interface/app.py
