import React, { useMemo, useState, useEffect } from 'react';
import { Card, Col, Row, Statistic, Table, Tag, Space, Input, Select, DatePicker, Button, message } from 'antd';
import { useAdmin, type AdminLog } from '../../contexts/AdminContext';
import { FileSearchOutlined, DownloadOutlined, ReloadOutlined } from '@ant-design/icons';

const { RangePicker } = DatePicker;

const mockLogs: AdminLog[] = [
  { id: 'm1', entity: 'user', entityId: 'u-101', action: 'create', at: Date.now() - 86400000 * 2, by: { id: '1', name: 'Admin Root' }, details: { name: 'João', email: 'joao@example.com' } },
  { id: 'm2', entity: 'profile', entityId: 'p-201', action: 'update', at: Date.now() - 86400000 * 1.5, by: { id: '1', name: 'Admin Root' }, details: { name: 'Usuário', description: 'Atualização de descrição' } },
  { id: 'm3', entity: 'permission', entityId: 'p-admin', action: 'update', at: Date.now() - 3600 * 1000 * 8, by: { id: '1', name: 'Admin Root' }, details: { screens: { usuarios: { view: true, create: true, edit: true, delete: false } } } },
  { id: 'm4', entity: 'user', entityId: 'u-102', action: 'delete', at: Date.now() - 3600 * 1000 * 3, by: { id: '2', name: 'Operador' }, details: { reason: 'Duplicado' } },
];

const Auditoria: React.FC = () => {
  const { logs } = useAdmin();
  const [data, setData] = useState<AdminLog[]>([]);
  const [action, setAction] = useState<'all' | AdminLog['action']>('all');
  const [entity, setEntity] = useState<'all' | AdminLog['entity']>('all');
  const [q, setQ] = useState<string>('');
  const [range, setRange] = useState<any>(null);

  useEffect(() => {
    // Carrega logs do contexto; se vazio, usa mock
    if (logs && logs.length > 0) {
      setData(logs);
    } else {
      setData(mockLogs);
    }
  }, [logs]);

  const filtered = useMemo(() => {
    return data.filter(l => {
      if (action !== 'all' && l.action !== action) return false;
      if (entity !== 'all' && l.entity !== entity) return false;
      if (q) {
        const txt = q.toLowerCase();
        const target = `${l.by?.name || ''} ${l.entityId || ''} ${JSON.stringify(l.details || {})}`.toLowerCase();
        if (!target.includes(txt)) return false;
      }
      if (range && range[0] && range[1]) {
        const start = range[0].startOf('day').valueOf();
        const end = range[1].endOf('day').valueOf();
        if (l.at < start || l.at > end) return false;
      }
      return true;
    }).map(l => ({ ...l, key: l.id }));
  }, [data, action, entity, q, range]);

  const stats = useMemo(() => ({
    total: data.length,
    creates: data.filter(l => l.action === 'create').length,
    updates: data.filter(l => l.action === 'update').length,
    deletes: data.filter(l => l.action === 'delete').length,
  }), [data]);

  const columns = [
    { title: 'Data/Hora', dataIndex: 'at', key: 'at', render: (v: number) => new Date(v).toLocaleString('pt-BR') },
    { title: 'Entidade', dataIndex: 'entity', key: 'entity', render: (e: AdminLog['entity']) => {
      const map: Record<AdminLog['entity'], string> = { user: 'Usuário', profile: 'Perfil', permission: 'Permissão' };
      return <Tag>{map[e]}</Tag>;
    } },
    { title: 'Ação', dataIndex: 'action', key: 'action', render: (a: AdminLog['action']) => {
      const map: Record<AdminLog['action'], string> = { create: 'INSERT', update: 'UPDATE', delete: 'DELETE' };
      return <Tag color={a === 'delete' ? 'red' : a === 'create' ? 'green' : 'blue'}>{map[a]}</Tag>;
    } },
    { title: 'ID', dataIndex: 'entityId', key: 'entityId' },
    { title: 'Quem', dataIndex: ['by','name'], key: 'by' },
    { title: 'Detalhes', dataIndex: 'details', key: 'details', render: (d: any) => d ? <code style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(d, null, 2)}</code> : '-' },
  ];

  const exportCSV = () => {
    const header = ['at','entity','action','entityId','by','details'];
    const rows = filtered.map(l => [
      new Date(l.at).toISOString(),
      l.entity,
      l.action,
      l.entityId,
      l.by?.name || '',
      JSON.stringify(l.details || {})
    ]);
    const csv = [header.join(','), ...rows.map(r => r.map(v => `"${String(v).replace(/"/g,'\"')}"`).join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `auditoria-${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    message.success('Exportado CSV');
  };

  const loadMock = () => {
    setData(mockLogs);
    message.info('Dados mock carregados');
  };

  const refresh = () => {
    setData(logs && logs.length ? logs : mockLogs);
    message.success('Atualizado');
  };

  return (
    <div style={{ padding: 16 }}>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic title="Total de Eventos" value={stats.total} prefix={<FileSearchOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="INSERT" value={stats.creates} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="UPDATE" value={stats.updates} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="DELETE" value={stats.deletes} />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }}>
        <Space style={{ marginBottom: 12 }} wrap>
          <Select
            value={action}
            onChange={(v) => setAction(v)}
            style={{ width: 160 }}
            options={[
              { value: 'all', label: 'Todas as Ações' },
              { value: 'create', label: 'INSERT' },
              { value: 'update', label: 'UPDATE' },
              { value: 'delete', label: 'DELETE' },
            ]}
          />
          <Select
            value={entity}
            onChange={(v) => setEntity(v)}
            style={{ width: 200 }}
            options={[
              { value: 'all', label: 'Todas as Entidades' },
              { value: 'user', label: 'Usuário' },
              { value: 'profile', label: 'Perfil' },
              { value: 'permission', label: 'Permissão' },
            ]}
          />
          <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar por nome, ID ou detalhes" style={{ width: 280 }} />
          <RangePicker value={range as any} onChange={(v) => setRange(v as any)} />
          <Button icon={<ReloadOutlined />} onClick={refresh}>Atualizar</Button>
          <Button icon={<DownloadOutlined />} type="primary" onClick={exportCSV}>Exportar CSV</Button>
          <Button onClick={loadMock}>Carregar Mock</Button>
        </Space>
        <Table columns={columns as any} dataSource={filtered} pagination={{ pageSize: 10 }} />
      </Card>
    </div>
  );
};

export default Auditoria;