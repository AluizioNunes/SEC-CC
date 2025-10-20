import React, { useMemo, useState } from 'react';
import { Card, Typography, Row, Col, Input, Select, Tag, DatePicker, List, Space, Button } from 'antd';
import { motion } from 'framer-motion';
import { useI18n } from '../i18n/I18nContext';
import { opportunities } from '../mock/opportunities';
import type { Opportunity, OpportunityCategory, OpportunityStatus } from '../types/catalog';
import { useNavigate } from 'react-router-dom';

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
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ padding: '24px' }}>
      <Card style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>{t('page.oportunidades.title')}</Title>
        <Paragraph type="secondary">{t('page.oportunidades.subtitle')}</Paragraph>

        {/* Filtros */}
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} md={8}>
            <Input placeholder="Buscar por palavra-chave" allowClear value={q} onChange={e => setQ(e.target.value)} />
          </Col>
          <Col xs={24} md={8}>
            <Select value={category} style={{ width: '100%' }} onChange={v => setCategory(v as any)}>
              <Option value="todas">Todas as categorias</Option>
              <Option value="edital">Editais</Option>
              <Option value="premio">Prêmios</Option>
              <Option value="oficina">Oficinas</Option>
            </Select>
          </Col>
          <Col xs={24} md={8}>
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
          </Col>
        </Row>

        {/* Destaque editorial */}
        {destaque && (
          <Card style={{ marginTop: 24, background: '#fafafa' }}>
            <Row gutter={16} align="middle">
              <Col xs={24} md={16}>
                <Space direction="vertical" size={8}>
                  <Tag color="gold">Destaque</Tag>
                  <Title level={3} style={{ margin: 0 }}>{destaque.title}</Title>
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
              </Col>
              <Col xs={24} md={8}>
                <Card cover={<div style={{ height: 160, background: '#e6f7ff', borderRadius: 8 }} />}>
                  <Card.Meta title={destaque.category.toUpperCase()} description={<span>Status: <Tag>{destaque.status}</Tag></span>} />
                </Card>
              </Col>
            </Row>
          </Card>
        )}

        {/* Lista */}
        <List
          grid={{ gutter: 16, xs: 1, sm: 2, md: 3 }}
          dataSource={list}
          style={{ marginTop: 24 }}
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
      </Card>
    </motion.div>
  );
};

export default Oportunidades;