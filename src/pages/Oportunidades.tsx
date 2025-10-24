import React, { useMemo, useState } from 'react';
import { Card, Typography, Input, Select, Tag, DatePicker, List, Space, Button } from 'antd';
import { useI18n } from '../i18n/I18nContext';
import { opportunities } from '../mock/opportunities';
import type { Opportunity, OpportunityCategory, OpportunityStatus } from '../types/catalog';
import { useNavigate } from 'react-router-dom';
import LinkedLayout from '../components/LinkedLayout';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

const Oportunidades: React.FC = () => {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const [category, setCategory] = useState<OpportunityCategory | 'todas'>('todas');
  const [status, setStatus] = useState<OpportunityStatus | 'todos'>('todos');
  const [range, setRange] = useState<[any, any] | null>(null);

  const data = useMemo(() => {
    return opportunities.filter(op => {
      const matchQ = q ? (op.title.toLowerCase().includes(q.toLowerCase()) || op.description.toLowerCase().includes(q.toLowerCase())) : true;
      const matchCat = category === 'todas' ? true : op.category === category;
      const matchStatus = status === 'todos' ? true : op.status === status;
      const matchRange = range ? (new Date(op.period.start) >= new Date(range[0]?.toDate()) && new Date(op.period.end) <= new Date(range[1]?.toDate())) : true;
      return matchQ && matchCat && matchStatus && matchRange;
    });
  }, [q, category, status, range]);

  const destaque = data.find(op => op.highlight);
  const list = data.filter(op => !op.highlight);

  const goDetail = (op: Opportunity) => navigate(`/oportunidades/${op.id}`);

  return (
    <LinkedLayout
      title={t('page.oportunidades.title')}
      subtitle={t('page.oportunidades.subtitle')}
      left={
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input placeholder="Buscar por palavra-chave" allowClear value={q} onChange={e => setQ(e.target.value)} />
          <Select value={category} style={{ width: '100%' }} onChange={v => setCategory(v as any)}>
            <Option value="todas">Todas as categorias</Option>
            <Option value="edital">Editais</Option>
            <Option value="premio">Prêmios</Option>
            <Option value="oficina">Oficinas</Option>
          </Select>
          <Space style={{ width: '100%' }}>
            <Select value={status} style={{ minWidth: 160 }} onChange={v => setStatus(v as any)}>
              <Option value="todos">Todos os status</Option>
              <Option value="aberto">Aberto</Option>
              <Option value="inscricoes">Inscrições</Option>
              <Option value="breve">Breve</Option>
              <Option value="encerrado">Encerrado</Option>
            </Select>
            <RangePicker onChange={vals => setRange(vals as any)} />
          </Space>
        </Space>
      }
      right={
        <Space direction="vertical" style={{ width: '100%' }}>
          {destaque && (
            <Card title="Destaque editorial" size="small" style={{ background: '#fafafa' }}>
              <Space direction="vertical" size={8}>
                <Tag color="gold">Destaque</Tag>
                <Title level={4} style={{ margin: 0 }}>{destaque.title}</Title>
                <Text type="secondary">{destaque.description}</Text>
                <Space wrap>
                  {destaque.tags.map(tag => <Tag key={tag}>{tag}</Tag>)}
                </Space>
                <Text>Período: {destaque.period.start} a {destaque.period.end}</Text>
                <Space>
                  <Button type="primary" onClick={() => goDetail(destaque)}>Inscrever-se</Button>
                  <Button onClick={() => goDetail(destaque)}>Ver detalhes</Button>
                </Space>
              </Space>
            </Card>
          )}
          <Card title="Tópicos em alta" size="small">
            <Space wrap>
              {['Editais', 'Prêmios', 'Formação', 'Fomento'].map(t => <Tag key={t}>{t}</Tag>)}
            </Space>
          </Card>
        </Space>
      }
    >
      <List
        grid={{ gutter: 16, xs: 1, sm: 2, md: 3 }}
        dataSource={list}
        renderItem={(item) => (
          <List.Item>
            <Card hoverable onClick={() => goDetail(item)}>
              <Space direction="vertical" size={8}>
                <Title level={4} style={{ margin: 0 }}>{item.title}</Title>
                <Text type="secondary">{item.description}</Text>
                <Space wrap>
                  <Tag>{item.category}</Tag>
                  <Tag color="processing">{item.status}</Tag>
                  {item.tags.map(tag => <Tag key={tag}>{tag}</Tag>)}
                </Space>
                <Text>Período: {item.period.start} a {item.period.end}</Text>
              </Space>
            </Card>
          </List.Item>
        )}
      />
    </LinkedLayout>
  );
};

export default Oportunidades;