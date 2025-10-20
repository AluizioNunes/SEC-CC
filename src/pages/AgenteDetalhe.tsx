import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Typography, Space, Tag, Button, Divider, List, Avatar, Image } from 'antd';
import { motion } from 'framer-motion';
import { agents } from '../mock/agents';
import { projects } from '../mock/projects';

const { Title, Paragraph, Text } = Typography;

const AgenteDetalhe: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const ag = agents.find(a => a.id === id);

  if (!ag) {
    return (
      <Card style={{ maxWidth: 900, margin: '24px auto' }}>
        <Title level={3}>Agente não encontrado</Title>
        <Button onClick={() => navigate('/agentes')}>Voltar ao catálogo</Button>
      </Card>
    );
  }

  const linkedProjects = ag.projectIds.map(pid => projects.find(p => p.id === pid)).filter(Boolean);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ padding: '24px' }}>
      <Card style={{ maxWidth: 1000, margin: '0 auto' }}>
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Space size={16} align="center">
            <Avatar size={80} src={ag.avatar} />
            <Space direction="vertical">
              <Title level={2} style={{ marginBottom: 0 }}>{ag.name}</Title>
              <Space wrap>
                <Tag color="blue">{ag.role}</Tag>
                <Tag>{ag.location.city}</Tag>
                <Tag>{ag.location.country}</Tag>
              </Space>
            </Space>
          </Space>

          <Divider />

          <Title level={4}>Bio</Title>
          <Paragraph>{ag.bio}</Paragraph>

          <Title level={4}>Portfólio</Title>
          <Image.PreviewGroup>
            <Space wrap>
              {ag.portfolio.map(src => (
                <Image key={src} src={src} width={240} />
              ))}
            </Space>
          </Image.PreviewGroup>

          <Title level={4}>Projetos associados</Title>
          <List
            dataSource={linkedProjects as any[]}
            renderItem={(p: any) => (
              <List.Item>
                <Space direction="vertical">
                  <Text strong>{p.title}</Text>
                  <Space>
                    <Tag color="purple">{p.area}</Tag>
                    <Tag color="green">{p.phase}</Tag>
                  </Space>
                  <Text type="secondary">{p.description}</Text>
                </Space>
              </List.Item>
            )}
          />

          <Space>
            <Button onClick={() => navigate('/agentes')}>Voltar</Button>
          </Space>
        </Space>
      </Card>
    </motion.div>
  );
};

export default AgenteDetalhe;