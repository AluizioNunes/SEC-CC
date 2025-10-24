import React, { useMemo, useState } from 'react';
import { Card, Typography, Input, Select, List, Avatar, Tag, Space, Button, Modal } from 'antd';
import { useI18n } from '../i18n/I18nContext';
import { agents } from '../mock/agents';
import type { AgentItem, AgentRole } from '../types/catalog';
import { useNavigate } from 'react-router-dom';
import LinkedLayout from '../components/LinkedLayout';
import { motion } from 'framer-motion';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

const Agentes: React.FC = () => {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const [role, setRole] = useState<AgentRole | 'todos'>('todos');
  const [loc, setLoc] = useState('');

  const containerVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0, transition: { staggerChildren: 0.05 } }
  };
  const itemVariants = {
    hidden: { opacity: 0, y: 8 },
    visible: { opacity: 1, y: 0 }
  };

  const data = useMemo(() => {
    return agents.filter((a) => {
      const matchQ = q
        ? a.name.toLowerCase().includes(q.toLowerCase()) || a.bio.toLowerCase().includes(q.toLowerCase())
        : true;
      const matchRole = role === 'todos' ? true : a.role === role;
      const matchLoc = loc ? (a.location.city + ' ' + a.location.country).toLowerCase().includes(loc.toLowerCase()) : true;
      return matchQ && matchRole && matchLoc;
    });
  }, [q, role, loc]);

  const goDetail = (ag: AgentItem) => navigate(`/agentes/${ag.id}`);
  const [connections, setConnections] = useState<Record<string, boolean>>({});
  const [follows, setFollows] = useState<Record<string, boolean>>({});
  const [messageOpen, setMessageOpen] = useState<boolean>(false);
  const [messageTarget, setMessageTarget] = useState<AgentItem | null>(null);
  const [messageText, setMessageText] = useState<string>('');

  const toggleConnect = (id: string) => setConnections(prev => ({ ...prev, [id]: !prev[id] }));
  const toggleFollow = (id: string) => setFollows(prev => ({ ...prev, [id]: !prev[id] }));

  const openMessage = (ag: AgentItem) => { setMessageTarget(ag); setMessageOpen(true); };
  const sendMessage = () => { if (messageTarget) { /* integração futura */ } setMessageOpen(false); setMessageText(''); };

  return (
    <LinkedLayout
      title={t('page.agentes.title')}
      subtitle={t('page.agentes.subtitle')}
      left={
        <motion.div initial="hidden" animate="visible" variants={containerVariants}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Input placeholder="Buscar agentes" allowClear value={q} onChange={(e) => setQ(e.target.value)} />
            <Select value={role} style={{ width: '100%' }} onChange={(v) => setRole(v as any)}>
              <Option value="todos">Todos</Option>
              <Option value="artista">Artista</Option>
              <Option value="produtor">Produtor</Option>
              <Option value="pesquisador">Pesquisador</Option>
            </Select>
            <Input placeholder="Cidade/País" allowClear value={loc} onChange={(e) => setLoc(e.target.value)} />
          </Space>
        </motion.div>
      }
      right={
        <motion.div initial="hidden" animate="visible" variants={containerVariants}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Card title="Perfis recomendados" size="small">
              {agents.slice(0, 3).map(a => (
                <motion.div key={a.id} variants={itemVariants} style={{ marginBottom: 8 }}>
                  <Space style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }} wrap>
                    <Space>
                      <Avatar size={40} src={a.avatar} />
                      <div>
                        <Text strong>{a.name}</Text>
                        <Paragraph style={{ margin: 0 }} type="secondary">{a.role}</Paragraph>
                      </div>
                    </Space>
                    <Button size="small" type={connections[a.id] ? 'default' : 'primary'} onClick={() => toggleConnect(a.id)}>
                      {connections[a.id] ? 'Conectado' : 'Conectar'}
                    </Button>
                  </Space>
                </motion.div>
              ))}
            </Card>
            <Card title="Tópicos em alta" size="small">
              <Space wrap>
                {['Artes', 'Música', 'Teatro', 'Cinema', 'Design'].map(t => <Tag key={t}>{t}</Tag>)}
              </Space>
            </Card>
          </Space>
        </motion.div>
      }
    >
      <motion.div initial="hidden" animate="visible" variants={containerVariants}>
        <List
          itemLayout="horizontal"
          dataSource={data}
          renderItem={(item) => (
            <List.Item
              actions={[
                <Button type="link" onClick={() => toggleConnect(item.id)}>{connections[item.id] ? 'Conectado' : 'Conectar'}</Button>,
                <Button type="link" onClick={() => toggleFollow(item.id)}>{follows[item.id] ? 'Seguindo' : 'Seguir'}</Button>,
                <Button type="link" onClick={() => openMessage(item)}>Mensagem</Button>,
                <Button type="link" onClick={() => goDetail(item)}>Ver perfil</Button>
              ]}
            >
              <motion.div variants={itemVariants} style={{ width: '100%' }}>
                <List.Item.Meta
                  avatar={<Avatar size={64} src={item.avatar} />}
                  title={<Title level={4} style={{ margin: 0 }}>{item.name}</Title>}
                  description={
                    <Space direction="vertical" size={4} style={{ width: '100%' }}>
                      <Space wrap>
                        <Tag color="blue">{item.role}</Tag>
                        <Tag>{item.location.city}</Tag>
                        <Tag>{item.location.country}</Tag>
                      </Space>
                      <Text type="secondary">{item.bio}</Text>
                    </Space>
                  }
                />
              </motion.div>
            </List.Item>
          )}
        />
      </motion.div>

      <Modal open={messageOpen} onCancel={() => setMessageOpen(false)} onOk={sendMessage} title={`Mensagem para ${messageTarget?.name || ''}`}>
        <Input.TextArea value={messageText} onChange={(e) => setMessageText(e.target.value)} rows={6} placeholder="Escreva sua mensagem..." />
      </Modal>
    </LinkedLayout>
  );
};

export default Agentes;