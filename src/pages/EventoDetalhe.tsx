import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Typography, Space, Tag, Button, Divider } from 'antd';
import { motion } from 'framer-motion';
import { events } from '../mock/events';
import MapEmbed from '../components/MapEmbed';

const { Title, Paragraph, Text } = Typography;

const EventoDetalhe: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const ev = events.find(e => e.id === id);

  if (!ev) {
    return (
      <Card style={{ maxWidth: 900, margin: '24px auto' }}>
        <Title level={3}>Evento não encontrado</Title>
        <Button onClick={() => navigate('/eventos')}>Voltar à agenda</Button>
      </Card>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ padding: '24px' }}>
      <Card style={{ maxWidth: 1000, margin: '0 auto' }}>
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Title level={2} style={{ marginBottom: 0 }}>{ev.title}</Title>
          <Space wrap>
            <Tag color="geekblue">{ev.type}</Tag>
            {ev.tags.map(t => <Tag key={t}>{t}</Tag>)}
          </Space>
          <Text type="secondary">Data: {ev.dateRange.start} — {ev.dateRange.end}</Text>

          <Divider />

          <Title level={4}>Descrição</Title>
          <Paragraph>{ev.description}</Paragraph>

          <Title level={4}>Localização</Title>
          <Text>Latitude: {ev.location?.lat}, Longitude: {ev.location?.lng}</Text>
          {ev.location && <MapEmbed lat={ev.location.lat} lng={ev.location.lng} height={360} />}

          <Space>
            <Button type="primary" size="large">Adicionar à agenda</Button>
            <Button onClick={() => navigate('/eventos')}>Voltar</Button>
          </Space>
        </Space>
      </Card>
    </motion.div>
  );
};

export default EventoDetalhe;