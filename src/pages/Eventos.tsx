import React, { useMemo, useState } from 'react';
import { Card, Typography, Input, DatePicker, Select, List, Space, Button } from 'antd';
import { useI18n } from '../i18n/I18nContext';
import { events } from '../mock/events';
import type { EventItem, EventType } from '../types/catalog';
import { useNavigate } from 'react-router-dom';
import MapEmbed from '../components/MapEmbed';
import LinkedLayout from '../components/LinkedLayout';

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
    <LinkedLayout
      title={t('page.eventos.title')}
      subtitle={t('page.eventos.subtitle')}
      left={
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input placeholder="Buscar eventos" allowClear value={q} onChange={e => setQ(e.target.value)} />
          <RangePicker style={{ width: '100%' }} onChange={vals => setRange(vals as any)} />
          <Select value={type} style={{ width: '100%' }} onChange={v => setType(v as any)}>
            <Option value="todos">Todos os tipos</Option>
            <Option value="show">Show</Option>
            <Option value="exposicao">Exposição</Option>
            <Option value="teatro">Teatro</Option>
            <Option value="workshop">Workshop</Option>
          </Select>
        </Space>
      }
      right={
        <Card>
          <Title level={4} style={{ marginBottom: 16 }}>Mapa</Title>
          {selected ? (
            <MapEmbed lat={selected.location.lat} lng={selected.location.lng} height={360} />
          ) : (
            <Paragraph type="secondary">Selecione um evento para visualizar no mapa.</Paragraph>
          )}
        </Card>
      }
    >
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
    </LinkedLayout>
  );
};

export default Eventos;