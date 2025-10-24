import React, { useMemo, useState } from 'react';
import { Card, Typography, Input, Select, List, Tag, Space, Button } from 'antd';
import { useI18n } from '../i18n/I18nContext';
import { projects } from '../mock/projects';
import type { ProjectItem, ProjectArea, ProjectPhase } from '../types/catalog';
import { useNavigate } from 'react-router-dom';
import LinkedLayout from '../components/LinkedLayout';

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
        ? p.title.toLowerCase().includes(q.toLowerCase()) || (p.description || '').toLowerCase().includes(q.toLowerCase())
        : true;
      const matchArea = area === 'todos' ? true : p.area === area;
      const matchPhase = phase === 'todos' ? true : p.phase === phase;
      return matchQ && matchArea && matchPhase;
    });
  }, [q, area, phase]);

  const goDetail = (p: ProjectItem) => navigate(`/projetos/${p.id}`);

  const sugestoes = useMemo(() => {
    // Sugestões simples: os 5 projetos mais recentes ou por área
    const base = projects.slice(0, 10);
    const filtradas = area === 'todos' ? base : base.filter(p => p.area === area);
    return filtradas.slice(0, 5);
  }, [area]);

  return (
    <LinkedLayout
      title={t('page.projetos.title')}
      subtitle={t('page.projetos.subtitle')}
      left={
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input placeholder="Buscar projetos" allowClear value={q} onChange={(e) => setQ(e.target.value)} />
          <Select value={area} style={{ width: '100%' }} onChange={(v) => setArea(v as any)}>
            <Option value="todos">Todas as áreas</Option>
            <Option value="musica">Música</Option>
            <Option value="artes">Artes Visuais</Option>
            <Option value="literatura">Literatura</Option>
          </Select>
          <Select value={phase} style={{ width: '100%' }} onChange={(v) => setPhase(v as any)}>
            <Option value="todos">Todas as fases</Option>
            <Option value="ideacao">Ideação</Option>
            <Option value="planejamento">Planejamento</Option>
            <Option value="execucao">Execução</Option>
            <Option value="finalizado">Finalizado</Option>
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
                    <Tag color="purple">{item.area}</Tag>
                    <Tag color="green">{item.phase}</Tag>
                  </Space>
                  <Button type="link" onClick={() => goDetail(item)}>Ver projeto</Button>
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
                  <Tag color="purple">{item.area}</Tag>
                  <Tag color="green">{item.phase}</Tag>
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

export default Projetos;