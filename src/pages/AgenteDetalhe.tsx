import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Typography, Space, Tag, Button, Divider, List, Avatar, Image, Grid } from 'antd';
import { motion } from 'framer-motion';
import { agents } from '../mock/agents';
import { projects } from '../mock/projects';

const { Title, Paragraph, Text } = Typography;

const AgenteDetalhe: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const ag = agents.find(a => a.id === id);
  const screens = Grid.useBreakpoint();

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
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ padding: screens.xs ? '12px' : '24px' }}>
      <Card style={{ width: '100%', maxWidth: 1100, margin: '0 auto' }}>
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            <Space size={16} align="center" wrap>
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
          </motion.div>

          <Divider />

          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            <Title level={4}>Bio</Title>
            <Paragraph>{ag.bio}</Paragraph>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            <Title level={4}>Portfólio</Title>
            <Image.PreviewGroup>
              <Space wrap>
                {ag.portfolio.map(src => (
                  <Image key={src} src={src} style={{ width: screens.xs ? '100%' : undefined }} width={screens.sm ? 240 : 320} />
                ))}
              </Space>
            </Image.PreviewGroup>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            <Title level={4}>Projetos associados</Title>
            <List
              dataSource={linkedProjects as any[]}
              renderItem={(p: any) => (
                <List.Item>
                  <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} style={{ width: '100%' }}>
                    <Space direction="vertical">
                      <Text strong>{p.title}</Text>
                      <Space wrap>
                        <Tag color="purple">{p.area}</Tag>
                        <Tag color="green">{p.phase}</Tag>
                      </Space>
                      <Text type="secondary">{p.description}</Text>
                    </Space>
                  </motion.div>
                </List.Item>
              )}
            />
          </motion.div>

          <Space>
            <Button onClick={() => navigate('/agentes')}>Voltar</Button>
          </Space>
        </Space>
      </Card>
    </motion.div>
  );
};

export default AgenteDetalhe;