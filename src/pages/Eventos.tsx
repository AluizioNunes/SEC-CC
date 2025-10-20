import React, { useMemo, useState } from 'react';
import { Card, Typography, Row, Col, Input, DatePicker, Select, List, Space, Button } from 'antd';
import { motion } from 'framer-motion';
import { useI18n } from '../i18n/I18nContext';
import { events } from '../mock/events';
import type { EventItem, EventType } from '../types/catalog';
import { useNavigate } from 'react-router-dom';
import MapEmbed from '../components/MapEmbed';

const { Title, Paragraph, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

const Eventos: React.FC = () => {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const [type, setType] = useState<EventType | 'todos'>('todos');
  const [range, setRange] = useState<[any, any] | null>(null);
  const [selected, setSelected] = useState<EventItem | null>(null);

  const data = useMemo(() => {
    return events.filter(ev => {
      const matchQ = q ? (ev.title.toLowerCase().includes(q.toLowerCase()) || ev.description.toLowerCase().includes(q.toLowerCase())) : true;
      const matchType = type === 'todos' ? true : ev.type === type;
      const matchRange = range ? (new Date(ev.dateRange.start) >= new Date(range[0]?.toDate()) && new Date(ev.dateRange.end) <= new Date(range[1]?.toDate())) : true;
      return matchQ && matchType && matchRange;
    });
  }, [q, type, range]);

  const goDetail = (ev: EventItem) => navigate(`/eventos/${ev.id}`);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ padding: '24px' }}>
      <Card style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>{t('page.eventos.title')}</Title>
        <Paragraph type="secondary">{t('page.eventos.subtitle')}</Paragraph>

        {/* Filtros */}
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} md={8}>
            <Input placeholder="Buscar eventos" allowClear value={q} onChange={e => setQ(e.target.value)} />
          </Col>
          <Col xs={24} md={8}>
            <RangePicker style={{ width: '100%' }} onChange={vals => setRange(vals as any)} />
          </Col>
          <Col xs={24} md={8}>
            <Select value={type} style={{ width: '100%' }} onChange={v => setType(v as any)}>
              <Option value="todos">Todos os tipos</Option>
              <Option value="show">Show</Option>
              <Option value="exposicao">Exposição</Option>
              <Option value="teatro">Teatro</Option>
              <Option value="workshop">Workshop</Option>
            </Select>
          </Col>
        </Row>

        {/* Lista e mapa */}
        <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
          <Col xs={24} md={14}>
            <List
              dataSource={data}
              renderItem={(item) => (
                <List.Item>
                  <Card hoverable onClick={() => { setSelected(item); }} actions={[<Button type="link" onClick={() => goDetail(item)}>Ver detalhes</Button>] }>
                    <Space direction="vertical" size={8}>
                      <Title level={4} style={{ margin: 0 }}>{item.title}</Title>
                      <Text type="secondary">{item.description}</Text>
                      <Space wrap>
                        <Text>Local: {item.location.city}, {item.location.country}</Text>
                      </Space>
                      <Text>Período: {item.dateRange.start} a {item.dateRange.end}</Text>
                      <Space wrap>
                        {item.tags.map(tag => <Button key={tag} size="small">{tag}</Button>)}
                      </Space>
                    </Space>
                  </Card>
                </List.Item>
              )}
            />
          </Col>
          <Col xs={24} md={10}>
            <Card>
              <Title level={4} style={{ marginBottom: 16 }}>Mapa</Title>
              {selected ? (
                <MapEmbed lat={selected.location.lat} lng={selected.location.lng} height={360} />
              ) : (
                <Paragraph type="secondary">Selecione um evento para visualizar no mapa.</Paragraph>
              )}
            </Card>
          </Col>
        </Row>
      </Card>
    </motion.div>
  );
};

export default Eventos;