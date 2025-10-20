import React, { useMemo, useState } from 'react';
import { Card, Typography, Row, Col, Input, Select, List, Tag, Space, Button } from 'antd';
import { motion } from 'framer-motion';
import { useI18n } from '../i18n/I18nContext';
import { courses } from '../mock/courses';
import type { CourseItem, CourseLevel, CourseMode } from '../types/catalog';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

const Cursos: React.FC = () => {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const [level, setLevel] = useState<CourseLevel | 'todos'>('todos');
  const [mode, setMode] = useState<CourseMode | 'todos'>('todos');

  const data = useMemo(() => {
    return courses.filter((c) => {
      const matchQ = q
        ? c.title.toLowerCase().includes(q.toLowerCase()) ||
          (c.description || '').toLowerCase().includes(q.toLowerCase())
        : true;
      const matchLevel = level === 'todos' ? true : c.level === level;
      const matchMode = mode === 'todos' ? true : c.mode === mode;
      return matchQ && matchLevel && matchMode;
    });
  }, [q, level, mode]);

  const goDetail = (c: CourseItem) => navigate(`/cursos/${c.id}`);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ padding: '24px' }}>
      <Card style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>{t('page.cursos.title')}</Title>
        <Paragraph type="secondary">{t('page.cursos.subtitle')}</Paragraph>

        {/* Filtros */}
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} md={8}>
            <Input placeholder="Buscar cursos" allowClear value={q} onChange={(e) => setQ(e.target.value)} />
          </Col>
          <Col xs={24} md={8}>
            <Select value={level} style={{ width: '100%' }} onChange={(v) => setLevel(v as any)}>
              <Option value="todos">Todos os níveis</Option>
              <Option value="iniciante">Iniciante</Option>
              <Option value="intermediario">Intermediário</Option>
              <Option value="avancado">Avançado</Option>
            </Select>
          </Col>
          <Col xs={24} md={8}>
            <Select value={mode} style={{ width: '100%' }} onChange={(v) => setMode(v as any)}>
              <Option value="todos">Todas as modalidades</Option>
              <Option value="online">Online</Option>
              <Option value="presencial">Presencial</Option>
              <Option value="hibrido">Híbrido</Option>
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
                        <Tag color="geekblue">{item.level}</Tag>
                        <Tag color="cyan">{item.mode}</Tag>
                        {item.enrollmentOpen ? <Tag color="green">Inscrições abertas</Tag> : <Tag color="red">Fechado</Tag>}
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

export default Cursos;