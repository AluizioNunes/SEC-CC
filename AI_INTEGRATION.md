# Integração de IA (Gemini) – SEC

Este guia explica como ativar e usar a IA embarcada (Google Gemini) na aplicação SEC, incluindo endpoints de atendimento automatizado para ARTISTAS, COLABORADORES e VISITANTES.

## Visão Geral
- Backend FastAPI expõe endpoints em `/ai` via `ai_router.py`.
- Serviço de IA unificado (`UltraAIService`) integra Gemini, OpenAI e Claude.
- Frontend possui cliente `src/services/aiApi.ts` para consumo dos endpoints.

## Variáveis de Ambiente
Configure no `.env` (Portainer/Compose):
- `GEMINI_API_KEY` – chave da API do Google Gemini.
- `GOOGLE_API_KEY` – alternativa suportada pelo serviço (fallback).
- `OPENAI_API_KEY` – opcional, para OpenAI.
- `ANTHROPIC_API_KEY` – opcional, para Claude.

O serviço tenta usar: `GEMINI_API_KEY` ou `GOOGLE_API_KEY` (fallback).

No `docker-compose.yml`, as chaves já são repassadas para o serviço FastAPI:
```
fastapi:
  environment:
    - GEMINI_API_KEY=${GEMINI_API_KEY}
    - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

## Endpoints (FastAPI)
- `GET /ai/providers` – status dos provedores (gemini/openai/claude).
- `GET /ai/models` – lista de modelos disponíveis.
- `POST /ai/chat` – chat geral com papel (role).
  - Body: `{ role, message, model_id?, context? }`
- `POST /ai/assist` – assistente por tópico (agenda, programação, ingressos, etc.).
  - Body: `{ role, topic?, message, model_id?, context? }`

Roles suportados: `ARTISTA(S)`, `COLABORADOR(ES)`, `VISITANTE(S)`, `GERAL`.

## Cliente Frontend
Use o cliente em `src/services/aiApi.ts`:
```ts
import { AIApi } from '@/services/aiApi';

const resp = await AIApi.chat({ role: 'VISITANTE', message: 'Quais horários de visita?' });
console.log(resp.text);
```

## Boas Práticas de Comunicação
- Respostas objetivas, educadas e em português.
- Estruturar em tópicos quando aplicável.
- Adaptar instruções segundo o papel (artista/colaborador/visitante).
- Evitar dados sensíveis; seguir políticas de privacidade.

## Troubleshooting
- `providers.gemini = false`: verifique `GEMINI_API_KEY`/`GOOGLE_API_KEY` e conectividade.
- Erros 500 nos endpoints `/ai`: inspecione logs do FastAPI (`docker logs CC-FASTAPI`).
- Latência alta: confirme rede externa e limites da API do provedor.

## Próximos Passos (Opcional)
- Adicionar memória de conversa por usuário via Redis.
- Habilitar streaming de respostas (SSE/WebSocket).
- Criar widget de chat no frontend e fluxos guiados por papel.