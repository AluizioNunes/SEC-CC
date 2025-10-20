import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Typography, Space, Tag, Button, Divider, List, Image } from 'antd';
import { motion } from 'framer-motion';
import { spaces } from '../mock/spaces';
import { events } from '../mock/events';
import MapEmbed from '../components/MapEmbed';

const { Title, Paragraph, Text } = Typography;

const EspacoDetalhe: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const sp = spaces.find(s => s.id === id);

  if (!sp) {
    return (
      <Card style={{ maxWidth: 900, margin: '24px auto' }}>
        <Title level={3}>Espaço não encontrado</Title>
        <Button onClick={() => navigate('/espacos')}>Voltar ao diretório</Button>
      </Card>
    );
  }

  const agenda = sp.agendaEvents.map(eid => events.find(e => e.id === eid)).filter(Boolean);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ padding: '24px' }}>
      <Card style={{ maxWidth: 1000, margin: '0 auto' }}>
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Title level={2} style={{ marginBottom: 0 }}>{sp.name}</Title>
          <Space wrap>
            <Tag color="geekblue">{sp.type}</Tag>
            {sp.services.map(s => <Tag key={s}>{s}</Tag>)}
          </Space>
          <Text type="secondary">{sp.location.address} — {sp.location.city}/{sp.location.country}</Text>

          <Divider />

          <Title level={4}>Fotos</Title>
          <Image.PreviewGroup>
            <Space wrap>
              {sp.photos.map(src => (
                <Image key={src} src={src} width={240} />
              ))}
            </Space>
          </Image.PreviewGroup>

          <Title level={4}>Horários</Title>
          <List dataSource={sp.hours} renderItem={(h) => (<List.Item><Text>{h.day}: {h.open} - {h.close}</Text></List.Item>)} />

          <Title level={4}>Acessibilidade e Serviços</Title>
          <Space wrap>
            {sp.services.map(s => <Tag key={s}>{s}</Tag>)}
          </Space>

          <Title level={4}>Contato</Title>
          <Space direction="vertical">
            {sp.contact.phone && <Text>Telefone: {sp.contact.phone}</Text>}
            {sp.contact.email && <Text>Email: {sp.contact.email}</Text>}
            {sp.contact.website && <a href={sp.contact.website} target="_blank" rel="noreferrer">Website</a>}
          </Space>

          <Title level={4}>Mapa</Title>
          <MapEmbed lat={sp.location.lat} lng={sp.location.lng} height={360} />

          <Title level={4}>Agenda do Espaço</Title>
          <List dataSource={agenda as any[]} renderItem={(e: any) => (
            <List.Item>
              <Space direction="vertical">
                <Text strong>{e.title}</Text>
                <Text type="secondary">{e.startDate} — {e.endDate}</Text>
              </Space>
            </List.Item>
          )} />

          <Space>
            <Button onClick={() => navigate('/espacos')}>Voltar</Button>
          </Space>
        </Space>
      </Card>
    </motion.div>
  );
};

export default EspacoDetalhe;