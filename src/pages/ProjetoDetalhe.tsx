import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Card, Typography, Space, Tag, Button, Divider, List } from 'antd';
import { motion } from 'framer-motion';
import { projects } from '../mock/projects';
import { agents } from '../mock/agents';
import { spaces } from '../mock/spaces';

const { Title, Paragraph, Text } = Typography;

const ProjetoDetalhe: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const pr = projects.find(p => p.id === id);

  if (!pr) {
    return (
      <Card style={{ maxWidth: 900, margin: '24px auto' }}>
        <Title level={3}>Projeto não encontrado</Title>
        <Button onClick={() => navigate('/projetos')}>Voltar ao catálogo</Button>
      </Card>
    );
  }

  const prAgents = pr.agentIds.map(aid => agents.find(a => a.id === aid)).filter(Boolean);
  const prSpaces = pr.spaceIds.map(sid => spaces.find(s => s.id === sid)).filter(Boolean);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ padding: '24px' }}>
      <Card style={{ maxWidth: 1000, margin: '0 auto' }}>
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Title level={2} style={{ marginBottom: 0 }}>{pr.title}</Title>
          <Space wrap>
            <Tag color="purple">{pr.area}</Tag>
            <Tag color="green">{pr.phase}</Tag>
          </Space>

          <Divider />

          <Title level={4}>Descrição</Title>
          <Paragraph>{pr.description}</Paragraph>

          <Title level={4}>Resultados</Title>
          <List dataSource={pr.results} renderItem={(r) => (<List.Item><Text>{r}</Text></List.Item>)} />

          <Title level={4}>Agentes</Title>
          <List
            dataSource={prAgents as any[]}
            renderItem={(a: any) => (
              <List.Item>
                <Space>
                  <Text strong>{a.name}</Text>
                  <Tag>{a.role}</Tag>
                  <Button type="link" onClick={() => navigate(`/agentes/${a.id}`)}>Ver perfil</Button>
                </Space>
              </List.Item>
            )}
          />

          <Title level={4}>Espaços</Title>
          <List
            dataSource={prSpaces as any[]}
            renderItem={(s: any) => (
              <List.Item>
                <Space>
                  <Text strong>{s.name}</Text>
                  <Tag>{s.type}</Tag>
                  <Button type="link" onClick={() => navigate(`/espacos/${s.id}`)}>Ver espaço</Button>
                </Space>
              </List.Item>
            )}
          />

          <Space>
            <Button onClick={() => navigate('/projetos')}>Voltar</Button>
          </Space>
        </Space>
      </Card>
    </motion.div>
  );
};

export default ProjetoDetalhe;