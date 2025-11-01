import axios from 'axios';

export interface ChatPayload {
  role: string;
  message: string;
  model_id?: string;
  context?: Record<string, any>;
  user_id?: string;
  session_id?: string;
  conversation_id?: string;
}

export interface AssistPayload extends ChatPayload {
  topic?: string;
}

const isDev = typeof import.meta !== 'undefined' && (import.meta as any).env && (import.meta as any).env.DEV;
const port = typeof window !== 'undefined' ? window.location.port : '';
const isViteDevPort = port.startsWith('517');
const baseURL = (isDev || isViteDevPort) ? '/api' : '/api/v1';

export const aiApi = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
});

export const AIApi = {
  async providers(): Promise<Record<string, boolean>> {
    const { data } = await aiApi.get('/ai/providers');
    return data;
  },

  async models(): Promise<any[]> {
    const { data } = await aiApi.get('/ai/models');
    return data;
  },

  async chat(payload: ChatPayload): Promise<{ text: string; provider: string; model_id: string; confidence: number; latency: number; }>{
    const { data } = await aiApi.post('/ai/chat', payload);
    return data;
  },

  async assist(payload: AssistPayload): Promise<{ text: string; provider: string; model_id: string; confidence: number; latency: number; }>{
    const { data } = await aiApi.post('/ai/assist', payload);
    return data;
  },

  streamChat(params: ChatPayload): EventSource {
    const q = new URLSearchParams({
      role: params.role,
      message: params.message,
      model_id: params.model_id || 'gemini-pro',
      user_id: params.user_id || '',
      session_id: params.session_id || '',
      conversation_id: params.conversation_id || '',
    });
    const url = `${baseURL}/ai/chat/stream?${q.toString()}`;
    return new EventSource(url);
  },

  async queueChat(payload: ChatPayload): Promise<{ status: string; message_id: string }>{
    const { data } = await aiApi.post('/ai/chat/queue', payload);
    return data;
  },

  async queueAssist(payload: AssistPayload): Promise<{ status: string; message_id: string }>{
    const { data } = await aiApi.post('/ai/assist/queue', payload);
    return data;
  }
};