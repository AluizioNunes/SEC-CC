import React, { useMemo, useState } from 'react';
import { Card, Typography, Input, Select, List, Tag, Space, Button } from 'antd';
import { useI18n } from '../i18n/I18nContext';
import { courses } from '../mock/courses';
import type { CourseItem, CourseLevel, CourseMode } from '../types/catalog';
import { useNavigate } from 'react-router-dom';
import LinkedLayout from '../components/LinkedLayout';

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
        ? c.title.toLowerCase().includes(q.toLowerCase()) || (c.description || '').toLowerCase().includes(q.toLowerCase())
        : true;
      const matchLevel = level === 'todos' ? true : c.level === level;
      const matchMode = mode === 'todos' ? true : c.mode === mode;
      return matchQ && matchLevel && matchMode;
    });
  }, [q, level, mode]);

  const goDetail = (c: CourseItem) => navigate(`/cursos/${c.id}`);

  const sugestoes = useMemo(() => {
    // Sugestões simples: cursos com inscrições abertas e do mesmo nível
    const base = courses.filter(c => c.enrollmentOpen);
    const filtradas = level === 'todos' ? base : base.filter(c => c.level === level);
    return filtradas.slice(0, 5);
  }, [level]);

  return (
    <LinkedLayout
      title={t('page.cursos.title')}
      subtitle={t('page.cursos.subtitle')}
      left={
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input placeholder="Buscar cursos" allowClear value={q} onChange={(e) => setQ(e.target.value)} />
          <Select value={level} style={{ width: '100%' }} onChange={(v) => setLevel(v as any)}>
            <Option value="todos">Todos os níveis</Option>
            <Option value="iniciante">Iniciante</Option>
            <Option value="intermediario">Intermediário</Option>
            <Option value="avancado">Avançado</Option>
          </Select>
          <Select value={mode} style={{ width: '100%' }} onChange={(v) => setMode(v as any)}>
            <Option value="todos">Todas as modalidades</Option>
            <Option value="online">Online</Option>
            <Option value="presencial">Presencial</Option>
            <Option value="hibrido">Híbrido</Option>
          </Select>
        </Space>
      }
      right={
        <Space direction="vertical" style={{ width: '100%' }}>
          <Title level={4} style={{ marginBottom: 8 }}>Sugestões</Title>
          <List
            dataSource={sugestoes}
            renderItem={(item) => (
              <List.Item>
                <Space direction="vertical" size={4} style={{ width: '100%' }}>
                  <Text strong>{item.title}</Text>
                  <Space wrap>
                    <Tag color="geekblue">{item.level}</Tag>
                    <Tag color="cyan">{item.mode}</Tag>
                  </Space>
                  <Button type="link" onClick={() => goDetail(item)}>Ver curso</Button>
                </Space>
              </List.Item>
            )}
          />
        </Space>
      }
    >
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
    </LinkedLayout>
  );
};

export default Cursos;