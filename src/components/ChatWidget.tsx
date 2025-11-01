import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Button, Card, Input, Segmented, Space, Switch, Tag, Typography, Select } from 'antd';
import { MessageOutlined, SendOutlined, ThunderboltOutlined, RobotOutlined, PlusOutlined } from '@ant-design/icons';
import { AIApi, type ChatPayload, type AssistPayload } from '../services/aiApi';

const { Text } = Typography;

type Role = 'Artista' | 'Colaborador' | 'Visitante' | 'Geral';

// Tipos de provedor/modelo removidos

interface ChatMessage {
  from: 'user' | 'assistant';
  role: Role;
  text: string;
}

const FloatingButton: React.FC<{ onClick: () => void }> = ({ onClick }) => (
  <Button
    type="primary"
    size="large"
    icon={<MessageOutlined />}
    onClick={onClick}
    style={{
      position: 'fixed',
      right: 24,
      bottom: 24,
      zIndex: 9999,
      borderRadius: 24,
      boxShadow: '0 8px 24px rgba(0,0,0,0.15)'
    }}
  >
    Chat SEC
  </Button>
);

export const ChatWidget: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [role, setRole] = useState<Role>('Geral');
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(true);
  const [busy, setBusy] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const [conversationId, setConversationId] = useState<string>('');
  const [conversations, setConversations] = useState<{ id: string; title: string; createdAt: number }[]>([]);

  const sessionId = useMemo(() => {
    const key = 'sec_session_id';
    const existing = localStorage.getItem(key);
    if (existing) return existing;
    const id = Math.random().toString(36).slice(2);
    localStorage.setItem(key, id);
    return id;
  }, []);

  // Inicializa conversa padrão e histórico
  useEffect(() => {
    const baseId = `web-${sessionId}`;
    const listKey = 'sec_conversations';
    try {
      const raw = localStorage.getItem(listKey);
      let list: { id: string; title: string; createdAt: number }[] = raw ? JSON.parse(raw) : [];
      if (!list.find(c => c.id === baseId)) {
        const initial = { id: baseId, title: 'Chat atual', createdAt: Date.now() };
        list = [initial, ...list];
        localStorage.setItem(listKey, JSON.stringify(list));
      }
      setConversations(list);
      setConversationId(baseId);
    } catch {
      setConversations([{ id: baseId, title: 'Chat atual', createdAt: Date.now() }]);
      setConversationId(baseId);
    }
  }, [sessionId]);

  // Removidos: provedores/modelos; sempre usamos o default do backend

  // Persistência de conversas por conversation_id
  useEffect(() => {
    const key = `sec_chat_${conversationId}`;
    try {
      const saved = localStorage.getItem(key);
      if (saved) setMessages(JSON.parse(saved));
    } catch {}
  }, [conversationId]);

  useEffect(() => {
    const key = `sec_chat_${conversationId}`;
    try {
      localStorage.setItem(key, JSON.stringify(messages));
    } catch {}
  }, [messages, conversationId]);

  const sendMessage = async () => {
    if (!message.trim() || busy) return;
    const payload: ChatPayload = {
      role,
      message: message.trim(),
      session_id: sessionId,
      conversation_id: conversationId,
    };

    setMessages(prev => [...prev, { from: 'user', role, text: payload.message! }]);
    setMessage('');
    setBusy(true);

    try {
      if (streaming) {
        // SSE streaming
        const es = AIApi.streamChat(payload);
        eventSourceRef.current = es;
        let current = '';
        es.onmessage = (evt) => {
          current = evt.data;
          // Atualiza última resposta parcialmente
          setMessages(prev => {
            const last = prev[prev.length - 1];
            const isAssistantLast = last && last.from === 'assistant';
            if (isAssistantLast) {
              const copy = [...prev];
              copy[copy.length - 1] = { ...copy[copy.length - 1], text: current };
              return copy;
            }
            return [...prev, { from: 'assistant', role, text: current }];
          });
        };
        es.addEventListener('end', () => {
          es.close();
          eventSourceRef.current = null;
          setBusy(false);
        });
        es.onerror = () => {
          es.close();
          eventSourceRef.current = null;
          setBusy(false);
        };
      } else {
        // Non-stream: chamada direta
        const res = await AIApi.chat(payload);
        setMessages(prev => [...prev, { from: 'assistant', role, text: res.text }]);
      }
    } catch (err) {
      console.error('Erro no chat', err);
    } finally {
      setBusy(false);
    }
  };

  const cancelStreaming = () => {
    try {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    } finally {
      setBusy(false);
    }
  };

  const sendAssist = async (kind: 'checklist' | 'faqs') => {
    if (busy) return;
    const payload: AssistPayload = {
      role,
      message: message.trim() || (kind === 'checklist' ? 'Gerar checklist' : 'Gerar FAQs'),
      session_id: sessionId,
      conversation_id: conversationId,
      topic: kind,
    };
    setBusy(true);
    try {
      setMessages(prev => [...prev, { from: 'user', role, text: payload.message! }]);
      const res = await AIApi.assist(payload);
      setMessages(prev => [...prev, { from: 'assistant', role, text: res.text }]);
    } catch (err) {
      console.error('Erro no assist', err);
    } finally {
      setBusy(false);
    }
  };

  const quickPrompt = (flow: 'inscricao' | 'compra' | 'agenda') => {
    const prompts: Record<string, string> = {
      inscricao: 'Quero me inscrever em um edital. Quais prazos e requisitos?',
      compra: 'Como comprar ingressos? Quais valores e políticas?',
      agenda: 'Qual a programação de hoje e eventos em destaque?'
    };
    setMessage(prompts[flow]);
  };

  useEffect(() => () => {
    if (eventSourceRef.current) eventSourceRef.current.close();
  }, []);

  if (!open) return <FloatingButton onClick={() => setOpen(true)} />;

  return (
    <Card
      style={{
        position: 'fixed', right: 24, bottom: 24, width: 420,
        height: 600, maxHeight: 'calc(100vh - 64px)',
        zIndex: 10000, boxShadow: '0 12px 28px rgba(0,0,0,0.18)'
      }}
      bodyStyle={{ display: 'flex', flexDirection: 'column', gap: 8, height: '100%' }}
      title={<span><RobotOutlined />&nbsp;Atendimento SEC</span>}
      extra={<Button onClick={() => setOpen(false)}>Fechar</Button>}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, height: '100%' }}>
        <Segmented
          value={role}
          onChange={(val) => setRole(val as Role)}
          options={[
            { label: 'Artista', value: 'Artista' },
            { label: 'Colaborador', value: 'Colaborador' },
            { label: 'Visitante', value: 'Visitante' },
            { label: 'Geral', value: 'Geral' },
          ]}
        />

        {/* Seletores de provedor/modelo removidos; Google/Gemini é padrão */}

        <Space style={{ width: '100%' }}>
          <Select
            style={{ flex: 1 }}
            value={conversationId}
            onChange={(val) => {
              setConversationId(val);
              // Carrega mensagens da conversa selecionada
              try {
                const saved = localStorage.getItem(`sec_chat_${val}`);
                setMessages(saved ? JSON.parse(saved) : []);
              } catch {
                setMessages([]);
              }
            }}
            options={conversations.map(c => ({ label: `${c.title} · ${new Date(c.createdAt).toLocaleString()}`, value: c.id }))}
            placeholder="Conversa"
          />
          <Button
            icon={<PlusOutlined />}
            onClick={() => {
              const newId = `web-${sessionId}-${Date.now().toString(36)}`;
              const newConv = { id: newId, title: `Chat ${conversations.length + 1}`, createdAt: Date.now() };
              const nextList = [newConv, ...conversations];
              setConversations(nextList);
              setConversationId(newId);
              setMessages([]);
              try {
                localStorage.setItem('sec_conversations', JSON.stringify(nextList));
              } catch {}
            }}
          >Novo chat</Button>
        </Space>

        <Space size="small" wrap>
          <Tag color="blue">Trilhas</Tag>
          <Button size="small" onClick={() => quickPrompt('inscricao')}>Inscrição</Button>
          <Button size="small" onClick={() => quickPrompt('compra')}>Compra</Button>
          <Button size="small" onClick={() => quickPrompt('agenda')}>Agenda</Button>
          <Tag color="green" style={{ marginLeft: 8 }}>Assist</Tag>
          <Button size="small" onClick={() => sendAssist('checklist')}>Checklist</Button>
          <Button size="small" onClick={() => sendAssist('faqs')}>FAQs</Button>
        </Space>

        <div style={{
          background: '#fafafa', border: '1px solid #eee', borderRadius: 8,
          padding: 8, flex: 1, minHeight: 140, overflowY: 'auto'
        }}>
          {messages.length === 0 && (
            <Text type="secondary">Envie uma pergunta e receba respostas em tempo real.</Text>
          )}
          {messages.map((m, i) => (
            <div key={i} style={{ marginBottom: 8 }}>
              <Text strong>{m.from === 'user' ? 'Você' : 'Assistente'}</Text>
              <Text type="secondary"> · {m.role}</Text>
              <div style={{ whiteSpace: 'pre-wrap' }}>{m.text}</div>
            </div>
          ))}
        </div>

        <Input.TextArea
          autoSize={{ minRows: 2, maxRows: 4 }}
          placeholder="Digite sua mensagem..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
              e.preventDefault();
              sendMessage();
            }
          }}
        />

        <Space style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Switch checked={streaming} onChange={setStreaming} />
            <Text type="secondary">Streaming</Text>
          </Space>
          <Space>
            <Button
              type="default"
              icon={<ThunderboltOutlined />}
              onClick={() => AIApi.queueChat({ role, message, session_id: sessionId, conversation_id: conversationId })}
            >
              Enfileirar
            </Button>
            {busy && streaming && (
              <Button danger onClick={cancelStreaming}>Cancelar</Button>
            )}
            <Button type="primary" icon={<SendOutlined />} loading={busy} onClick={sendMessage}>
              Enviar
            </Button>
          </Space>
        </Space>
      </div>
    </Card>
  );
};

export default ChatWidget;