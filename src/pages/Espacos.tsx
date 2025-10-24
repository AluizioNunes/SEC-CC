import React, { useMemo, useState } from 'react';
import { Card, Typography, Input, Select, List, Space, Tag, Button } from 'antd';
import { useI18n } from '../i18n/I18nContext';
import { spaces } from '../mock/spaces';
import type { SpaceItem, SpaceType } from '../types/catalog';
import { useNavigate } from 'react-router-dom';
import MapEmbed from '../components/MapEmbed';
import LinkedLayout from '../components/LinkedLayout';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

const Espacos: React.FC = () => {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const [type, setType] = useState<SpaceType | 'todos'>('todos');
  const [selected, setSelected] = useState<SpaceItem | null>(null);

  const data = useMemo(() => {
    return spaces.filter(sp => {
      const matchQ = q ? (sp.name.toLowerCase().includes(q.toLowerCase()) || (sp.location.city + ' ' + sp.location.country).toLowerCase().includes(q.toLowerCase())) : true;
      const matchType = type === 'todos' ? true : sp.type === type;
      return matchQ && matchType;
    });
  }, [q, type]);

  const goDetail = (sp: SpaceItem) => navigate(`/espacos/${sp.id}`);

  return (
    <LinkedLayout
      title={t('page.espacos.title')}
      subtitle={t('page.espacos.subtitle')}
      left={
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input placeholder="Buscar espaços" allowClear value={q} onChange={e => setQ(e.target.value)} />
          <Select value={type} style={{ width: '100%' }} onChange={v => setType(v as any)}>
            <Option value="todos">Todos os espaços</Option>
            <Option value="teatro">Teatro</Option>
            <Option value="galeria">Galeria</Option>
            <Option value="biblioteca">Biblioteca</Option>
            <Option value="centro_cultural">Centro Cultural</Option>
          </Select>
        </Space>
      }
      right={
        <Card>
          <Title level={4} style={{ marginBottom: 16 }}>Mapa</Title>
          {selected ? (
            <MapEmbed lat={selected.location.lat} lng={selected.location.lng} height={360} />
          ) : (
            <Paragraph type="secondary">Selecione um espaço para visualizar no mapa.</Paragraph>
          )}
        </Card>
      }
    >
      <List
        dataSource={data}
        renderItem={(item) => (
          <List.Item>
            <Card hoverable onClick={() => setSelected(item)} actions={[<Button type="link" onClick={() => goDetail(item)}>Ver detalhes</Button>] }>
              <Space direction="vertical" size={8}>
                <Title level={4} style={{ margin: 0 }}>{item.name}</Title>
                <Text type="secondary">{item.type.toUpperCase()}</Text>
                <Space wrap>
                  {item.services.map(s => <Tag key={s}>{s}</Tag>)}
                </Space>
                <Text>Local: {item.location.city}, {item.location.country}</Text>
              </Space>
            </Card>
          </List.Item>
        )}
      />
    </LinkedLayout>
  );
};

export default Espacos;