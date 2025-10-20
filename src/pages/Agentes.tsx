import React, { useMemo, useState } from 'react';
import { Card, Typography, Row, Col, Input, Select, List, Avatar, Tag, Space, Button } from 'antd';
import { motion } from 'framer-motion';
import { useI18n } from '../i18n/I18nContext';
import { agents } from '../mock/agents';
import type { AgentItem, AgentRole } from '../types/catalog';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

const Agentes: React.FC = () => {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const [role, setRole] = useState<AgentRole | 'todos'>('todos');
  const [loc, setLoc] = useState('');

  const data = useMemo(() => {
    return agents.filter((a) => {
      const matchQ = q
        ? a.name.toLowerCase().includes(q.toLowerCase()) ||
          a.bio.toLowerCase().includes(q.toLowerCase())
        : true;
      const matchRole = role === 'todos' ? true : a.role === role;
      const matchLoc = loc
        ? (a.location.city + ' ' + a.location.country)
            .toLowerCase()
            .includes(loc.toLowerCase())
        : true;
      return matchQ && matchRole && matchLoc;
    });
  }, [q, role, loc]);

  const goDetail = (ag: AgentItem) => navigate(`/agentes/${ag.id}`);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ padding: '24px' }}>
      <Card style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>{t('page.agentes.title')}</Title>
        <Paragraph type="secondary">{t('page.agentes.subtitle')}</Paragraph>

        {/* Filtros */}
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} md={8}>
            <Input placeholder="Buscar agentes" allowClear value={q} onChange={(e) => setQ(e.target.value)} />
          </Col>
          <Col xs={24} md={8}>
            <Select value={role} style={{ width: '100%' }} onChange={(v) => setRole(v as any)}>
              <Option value="todos">Todos</Option>
              <Option value="artista">Artista</Option>
              <Option value="produtor">Produtor</Option>
              <Option value="pesquisador">Pesquisador</Option>
            </Select>
          </Col>
          <Col xs={24} md={8}>
            <Input placeholder="Cidade/País" allowClear value={loc} onChange={(e) => setLoc(e.target.value)} />
          </Col>
        </Row>

        {/* Lista */}
        <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
          <Col span={24}>
            <List
              itemLayout="horizontal"
              dataSource={data}
              renderItem={(item) => (
                <List.Item actions={[<Button type="link" onClick={() => goDetail(item)}>Ver perfil</Button>] }>
                  <List.Item.Meta
                    avatar={<Avatar size={64} src={item.avatar} />}
                    title={<Title level={4} style={{ margin: 0 }}>{item.name}</Title>}
                    description={
                      <Space direction="vertical" size={4}>
                        <Space wrap>
                          <Tag color="blue">{item.role}</Tag>
                          <Tag>{item.location.city}</Tag>
                          <Tag>{item.location.country}</Tag>
                        </Space>
                        <Text type="secondary">{item.bio}</Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Col>
        </Row>
      </Card>
    </motion.div>
  );
};

export default Agentes;