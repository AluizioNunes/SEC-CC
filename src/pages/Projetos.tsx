import React, { useMemo, useState } from 'react';
import { Card, Typography, Row, Col, Input, Select, List, Tag, Space, Button } from 'antd';
import { motion } from 'framer-motion';
import { useI18n } from '../i18n/I18nContext';
import { projects } from '../mock/projects';
import type { ProjectItem, ProjectArea, ProjectPhase } from '../types/catalog';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

const Projetos: React.FC = () => {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const [area, setArea] = useState<ProjectArea | 'todos'>('todos');
  const [phase, setPhase] = useState<ProjectPhase | 'todos'>('todos');

  const data = useMemo(() => {
    return projects.filter((p) => {
      const matchQ = q
        ? p.title.toLowerCase().includes(q.toLowerCase()) ||
          (p.description || '').toLowerCase().includes(q.toLowerCase())
        : true;
      const matchArea = area === 'todos' ? true : p.area === area;
      const matchPhase = phase === 'todos' ? true : p.phase === phase;
      return matchQ && matchArea && matchPhase;
    });
  }, [q, area, phase]);

  const goDetail = (p: ProjectItem) => navigate(`/projetos/${p.id}`);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ padding: '24px' }}>
      <Card style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>{t('page.projetos.title')}</Title>
        <Paragraph type="secondary">{t('page.projetos.subtitle')}</Paragraph>

        {/* Filtros */}
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} md={8}>
            <Input placeholder="Buscar projetos" allowClear value={q} onChange={(e) => setQ(e.target.value)} />
          </Col>
          <Col xs={24} md={8}>
            <Select value={area} style={{ width: '100%' }} onChange={(v) => setArea(v as any)}>
              <Option value="todos">Todas as áreas</Option>
              <Option value="musica">Música</Option>
              <Option value="artes">Artes Visuais</Option>
              <Option value="literatura">Literatura</Option>
            </Select>
          </Col>
          <Col xs={24} md={8}>
            <Select value={phase} style={{ width: '100%' }} onChange={(v) => setPhase(v as any)}>
              <Option value="todos">Todas as fases</Option>
              <Option value="ideacao">Ideação</Option>
              <Option value="planejamento">Planejamento</Option>
              <Option value="execucao">Execução</Option>
              <Option value="finalizado">Finalizado</Option>
            </Select>
          </Col>
        </Row>

        {/* Lista */}
        <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
          <Col span={24}>
            <List
              dataSource={data}
              renderItem={(item) => (
                <List.Item>
                  <Card hoverable actions={[<Button type="link" onClick={() => goDetail(item)}>Ver detalhes</Button>] }>
                    <Space direction="vertical" size={8}>
                      <Title level={4} style={{ margin: 0 }}>{item.title}</Title>
                      <Space wrap>
                        <Tag color="purple">{item.area}</Tag>
                        <Tag color="green">{item.phase}</Tag>
                      </Space>
                      {item.description && <Text type="secondary">{item.description}</Text>}
                    </Space>
                  </Card>
                </List.Item>
              )}
            />
          </Col>
        </Row>
      </Card>
    </motion.div>
  );
};

export default Projetos;