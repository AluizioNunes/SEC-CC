import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Typography, Space, Tag, Button, List, Divider } from 'antd';
import { motion } from 'framer-motion';
import { opportunities } from '../mock/opportunities';

const { Title, Paragraph, Text } = Typography;

const OportunidadeDetalhe: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const opp = opportunities.find(o => o.id === id);

  if (!opp) {
    return (
      <Card style={{ maxWidth: 900, margin: '24px auto' }}>
        <Title level={3}>Oportunidade não encontrada</Title>
        <Button onClick={() => navigate('/oportunidades')}>Voltar ao catálogo</Button>
      </Card>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ padding: '24px' }}>
      <Card style={{ maxWidth: 1000, margin: '0 auto' }}>
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Title level={2} style={{ marginBottom: 0 }}>{opp.title}</Title>
          <Space wrap>
            <Tag color="purple">{opp.category}</Tag>
            <Tag color={opp.status === 'aberto' ? 'green' : opp.status === 'inscricoes' ? 'geekblue' : opp.status === 'breve' ? 'orange' : 'default'}>
              {opp.status}
            </Tag>
            {opp.tags.map(t => <Tag key={t}>{t}</Tag>)}
          </Space>
          <Text type="secondary">Período: {opp.period.start} — {opp.period.end}</Text>

          <Divider />

          <Title level={4}>Descrição</Title>
          <Paragraph>{opp.description}</Paragraph>

          <Title level={4}>Requisitos</Title>
          <List dataSource={opp.requirements} renderItem={(req) => (<List.Item key={req}><Text>{req}</Text></List.Item>)} />

          <Title level={4}>Cronograma</Title>
          <List dataSource={opp.timeline} renderItem={(tl) => (<List.Item key={`${tl.date}-${tl.label}`}><Text>{tl.date}: {tl.label}</Text></List.Item>)} />

          <Title level={4}>Documentos</Title>
          <List dataSource={opp.documents} renderItem={(doc) => (<List.Item key={doc.name}><a href={doc.url} target="_blank" rel="noreferrer">{doc.name}</a></List.Item>)} />

          <Space>
            <Button type="primary" size="large">Inscrever-se</Button>
            <Button onClick={() => navigate('/oportunidades')}>Voltar</Button>
          </Space>
        </Space>
      </Card>
    </motion.div>
  );
};

export default OportunidadeDetalhe;