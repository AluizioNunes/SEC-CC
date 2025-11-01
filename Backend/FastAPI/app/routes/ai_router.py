from __future__ import annotations
import os
from typing import Any, Dict, Optional
import json
import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Ensure Backend package is importable when running standalone
import sys
import os as _os
sys.path.append(_os.path.join(_os.path.dirname(__file__), '..', '..'))

try:
    from Backend.AI.ai_service import ultra_ai_service, PredictionRequest, AIProvider
except Exception as e:
    raise RuntimeError(f"Falha ao importar serviços de IA: {e}")

# Redis client e broker híbrido
try:
    from app.redis import get_redis_client
    from app.redis import hybrid_broker
except Exception:
    get_redis_client = None
    hybrid_broker = None


ai_router = APIRouter(prefix="/ai", tags=["ai"])


class ChatRequest(BaseModel):
    role: str
    message: str
    model_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None


class AssistRequest(BaseModel):
    role: str
    topic: Optional[str] = None
    message: str
    model_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None


@ai_router.get("/providers")
def providers_status():
    """Retorna status de provedores de IA disponíveis."""
    try:
        return ultra_ai_service.get_provider_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.get("/models")
def available_models():
    """Lista de modelos disponíveis no serviço de IA."""
    try:
        return ultra_ai_service.get_available_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _role_instructions(role: str) -> str:
    role_upper = (role or "GERAL").strip().upper()
    base = (
        "Você é um assistente da plataforma SEC. Forneça respostas em português, "
        "claras, educadas, objetivas e úteis. Mantenha a comunicação coerente, correta, "
        "automatizada, eficiente e eficaz. Estruture em tópicos curtos quando apropriado."
    )

    if role_upper in {"ARTISTA", "ARTISTAS"}:
        return base + (
            " Foque em: submissões, edital, inscrições, prazos, requisitos técnicos, "
            "direitos autorais, agenda de exposições, montagem e logística. Evite jargões e seja prático."
        )
    if role_upper in {"COLABORADOR", "COLABORADORES"}:
        return base + (
            " Foque em: operações, suporte, cronogramas, responsabilidades, contatos de equipe, "
            "procedimentos, segurança e boas práticas de atendimento."
        )
    if role_upper in {"VISITANTE", "VISITANTES"}:
        return base + (
            " Foque em: programação, horários, ingressos, acessibilidade, localização, regras de visita, "
            "eventos em destaque e canais de contato."
        )
    return base + " Adapte conforme o contexto fornecido."


def _conv_key(user_id: Optional[str], session_id: Optional[str], conversation_id: Optional[str]) -> str:
    """Gera chave de conversa para memória em Redis."""
    base = conversation_id or user_id or session_id or "anon"
    return f"sec:ai:conversation:{base}"


async def _save_event(conv_key: str, entry: Dict[str, Any]):
    """Salva um evento de conversa no Redis (lista cronológica)."""
    if not get_redis_client:
        return
    try:
        client = get_redis_client()
        entry["ts"] = int(asyncio.get_event_loop().time() * 1000)
        await client.rpush(conv_key, json.dumps(entry, default=str))
        # Expira conversas inativas em 7 dias
        await client.expire(conv_key, 7 * 24 * 3600)
    except Exception:
        # Não interrompe fluxo em caso de erro de cache
        pass


@ai_router.post("/chat")
async def chat(req: ChatRequest):
    """Atendimento geral por chat com contexto de papel (role)."""
    try:
        model_id = req.model_id or "gemini-pro"
        instructions = _role_instructions(req.role)
        input_data: Dict[str, Any] = {
            "system_instructions": instructions,
            "user_message": req.message,
            "role": req.role,
            "context": req.context or {},
        }

        pred = await ultra_ai_service.make_prediction(
            PredictionRequest(
                model_id=model_id,
                input_data=input_data,
                context={"source": "fastapi.ai_router", "feature": "chat"},
                provider=AIProvider.GEMINI,
            )
        )
        # Memória de conversa
        conv_key = _conv_key(req.user_id, req.session_id, req.conversation_id)
        await _save_event(conv_key, {"type": "user", "role": req.role, "message": req.message})
        await _save_event(conv_key, {
            "type": "assistant",
            "role": req.role,
            "text": pred.result,
            "provider": pred.provider.value,
            "model_id": pred.model_id
        })

        return {
            "text": pred.result,
            "provider": pred.provider.value,
            "model_id": pred.model_id,
            "confidence": pred.confidence,
            "latency": pred.processing_time,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.post("/assist")
async def assist(req: AssistRequest):
    """Assistente especializado por tópico (agenda, programação, ingressos, etc.)."""
    try:
        model_id = req.model_id or "gemini-pro"
        role_instr = _role_instructions(req.role)
        topic = (req.topic or "geral").strip().lower()

        topic_instr = {
            "agenda": "Explique agenda, horários e disponibilidade com precisão e objetividade.",
            "programacao": "Mostre eventos em destaque, trilhas e recomendações conforme perfil informado.",
            "ingressos": "Detalhe valores, gratuidades, meia-entrada, políticas de devolução e canais de compra.",
            "acessibilidade": "Informe recursos de acessibilidade disponíveis e como solicitar apoio.",
            "localizacao": "Oriente quanto a endereço, transporte, estacionamento e pontos de referência.",
            "inscricoes": "Guie sobre prazos, requisitos, documentação e critérios de avaliação.",
            "submissoes": "Esclareça formatos aceitos, diretrizes técnicas e direitos autorais.",
        }.get(topic, "Responda de forma prática e direcionada ao tópico solicitado.")

        instructions = f"{role_instr} {topic_instr}"
        input_data: Dict[str, Any] = {
            "system_instructions": instructions,
            "user_message": req.message,
            "role": req.role,
            "topic": topic,
            "context": req.context or {},
        }

        pred = await ultra_ai_service.make_prediction(
            PredictionRequest(
                model_id=model_id,
                input_data=input_data,
                context={"source": "fastapi.ai_router", "feature": "assist", "topic": topic},
                provider=AIProvider.GEMINI,
            )
        )
        # Memória de conversa
        conv_key = _conv_key(req.user_id, req.session_id, req.conversation_id)
        await _save_event(conv_key, {"type": "user", "role": req.role, "topic": topic, "message": req.message})
        await _save_event(conv_key, {
            "type": "assistant",
            "role": req.role,
            "topic": topic,
            "text": pred.result,
            "provider": pred.provider.value,
            "model_id": pred.model_id
        })

        return {
            "text": pred.result,
            "provider": pred.provider.value,
            "model_id": pred.model_id,
            "confidence": pred.confidence,
            "latency": pred.processing_time,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.get("/ping")
def ping():
    """Verificação rápida do router de IA."""
    # Exibe se Gemini está configurado
    gemini_ready = ultra_ai_service.get_provider_status().get("gemini", False)
    return {"status": "ok", "gemini": gemini_ready}


@ai_router.get("/chat/stream")
async def chat_stream(
    role: str,
    message: str,
    model_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    conversation_id: Optional[str] = None
):
    """Streaming via SSE para respostas em tempo real."""
    try:
        model_id = model_id or "gemini-pro"
        instructions = _role_instructions(role)
        input_data: Dict[str, Any] = {
            "system_instructions": instructions,
            "user_message": message,
            "role": role,
            "context": {},
        }

        pred = await ultra_ai_service.make_prediction(
            PredictionRequest(
                model_id=model_id,
                input_data=input_data,
                context={"source": "fastapi.ai_router", "feature": "chat_stream"},
                provider=AIProvider.GEMINI,
            )
        )

        # Memória do usuário
        conv_key = _conv_key(user_id, session_id, conversation_id)
        await _save_event(conv_key, {"type": "user", "role": role, "message": message})

        async def event_generator(text: str):
            # Simples fatiamento em palavras para simular streaming incremental
            buffer = []
            for token in text.split(" "):
                buffer.append(token)
                chunk = " ".join(buffer)
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.03)

            # Evento final com metadados
            meta = {
                "provider": pred.provider.value,
                "model_id": pred.model_id
            }
            await _save_event(conv_key, {"type": "assistant", "role": role, "text": text, **meta})
            yield f"event: end\ndata: {json.dumps(meta, default=str)}\n\n"

        return StreamingResponse(event_generator(pred.result), media_type="text/event-stream")
    except Exception as e:
        # SSE: erros devem ser serializados
        return StreamingResponse((f"event: error\ndata: {str(e)}\n\n" for _ in range(1)), media_type="text/event-stream")


@ai_router.post("/chat/queue")
async def chat_queue(req: ChatRequest):
    """Enfileira requisição de chat no broker híbrido (RabbitMQ/Redis)."""
    try:
        message = {
            "type": "chat_request",
            "role": req.role,
            "message": req.message,
            "model_id": req.model_id or "gemini-pro",
            "context": req.context or {},
            "user_id": req.user_id,
            "session_id": req.session_id,
            "conversation_id": req.conversation_id
        }

        if hybrid_broker is None:
            raise HTTPException(status_code=503, detail="Message broker indisponível")

        # Prioridade normal; publica em modo híbrido
        msg_id = await hybrid_broker.publish_message(
            message,
            routing_key="ai.chat",
            stream_name="ai_chat_requests"
        )

        return {"status": "queued", "message_id": msg_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.post("/assist/queue")
async def assist_queue(req: AssistRequest):
    """Enfileira requisição de assistente no broker híbrido (RabbitMQ/Redis)."""
    try:
        message = {
            "type": "assist_request",
            "role": req.role,
            "topic": (req.topic or "geral").strip().lower(),
            "message": req.message,
            "model_id": req.model_id or "gemini-pro",
            "context": req.context or {},
            "user_id": req.user_id,
            "session_id": req.session_id,
            "conversation_id": req.conversation_id
        }

        if hybrid_broker is None:
            raise HTTPException(status_code=503, detail="Message broker indisponível")

        msg_id = await hybrid_broker.publish_message(
            message,
            routing_key="ai.assist",
            stream_name="ai_assist_requests"
        )
        return {"status": "queued", "message_id": msg_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))