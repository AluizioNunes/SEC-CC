import React, { useMemo, useState } from 'react';
import { Card, Col, Row, Statistic, Table, Tag, Button, Space, message, Input, Select, Alert } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, UserOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useAdmin, type AdminUser, type Profile } from '../../contexts/AdminContext';
import UsuarioModal from '../../components/modals/UsuarioModal';
import { useAuth } from '../../contexts/AuthContext';

const Usuarios: React.FC = () => {
  const { users, profiles, deleteUser, getPermissionsForProfile } = useAdmin();
  const { user } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string | undefined>(undefined);
  const [filterProfile, setFilterProfile] = useState<string | undefined>(undefined);
  const [pageSize, setPageSize] = useState<number>(8);

  const currentProfileId = user?.profile === 'admin' ? 'p-admin' : 'p-usuario';
  const perms = getPermissionsForProfile(currentProfileId)?.screens?.usuarios || { view: true, create: true, edit: true, delete: true };

  const stats = useMemo(() => {
    const total = users.length;
    const approved = users.filter((u: AdminUser) => u.status === 'approved' || u.status === 'active').length;
    const pending = users.filter((u: AdminUser) => u.status === 'pending').length;
    const pf = users.filter((u: AdminUser) => u.type === 'PF').length;
    const pj = users.filter((u: AdminUser) => u.type === 'PJ').length;
    return { total, approved, pending, pf, pj };
  }, [users]);

  const filtered = useMemo(() => {
    return users.filter((u: AdminUser) => {
      const q = query.trim().toLowerCase();
      const matchQuery = q ? (u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)) : true;
      const matchStatus = filterStatus ? (u.status === filterStatus) : true;
      const matchProfile = filterProfile ? (u.profileId === filterProfile) : true;
      return matchQuery && matchStatus && matchProfile;
    });
  }, [users, query, filterStatus, filterProfile]);

  const columns = [
    { title: 'Nome', dataIndex: 'name', key: 'name' },
    { title: 'Email', dataIndex: 'email', key: 'email' },
    { title: 'Tipo', dataIndex: 'type', key: 'type', render: (t: string) => <Tag color={t === 'PF' ? 'blue' : 'purple'}>{t}</Tag> },
    { title: 'Perfil', dataIndex: 'profileId', key: 'profileId', render: (id: string) => profiles.find((p: Profile) => p.id === id)?.name || id },
    { title: 'Status', dataIndex: 'status', key: 'status', render: (s: string) => {
      const color = s === 'approved' || s === 'active' ? 'green' : s === 'pending' ? 'orange' : 'red';
      return <Tag color={color}>{s}</Tag>;
    } },
    perms.edit || perms.delete ? { title: 'Ações', key: 'actions', render: (_: any, r: any) => (
      <Space>
        {perms.edit && <Button icon={<EditOutlined />} onClick={() => { setEditingUserId(r.id); setModalOpen(true); }}>Editar</Button>}
        {perms.delete && <Button danger icon={<DeleteOutlined />} onClick={async () => { await deleteUser(r.id, user ? { id: user.id, name: user.name } : undefined); message.success('Usuário removido'); }}>Excluir</Button>}
      </Space>
    ) } : undefined,
  ].filter(Boolean);

  const dataSource = filtered.map((u: AdminUser) => ({ key: u.id, ...u }));
  const editingUser = users.find((u: AdminUser) => u.id === editingUserId) || null;

  if (!perms.view) {
    return <Alert type="warning" message="Você não tem permissão para visualizar Usuários" showIcon style={{ margin: 16 }} />;
  }

  return (
    <div style={{ padding: 16 }}>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic title="Total de Usuários" value={stats.total} prefix={<UserOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Aprovados/Ativos" value={stats.approved} prefix={<CheckCircleOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Pendentes" value={stats.pending} prefix={<ClockCircleOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="PF / PJ" value={`${stats.pf} / ${stats.pj}`} />
          </Card>
        </Col>
      </Row>

      <div style={{ marginTop: 16, marginBottom: 16 }}>
        <Space wrap>
          <Input.Search allowClear style={{ width: 280 }} placeholder="Buscar por nome ou email" value={query} onChange={(e) => setQuery(e.target.value)} />
          <Select allowClear style={{ width: 200 }} placeholder="Filtrar por status" value={filterStatus} onChange={setFilterStatus} options={[
            { value: 'approved', label: 'Aprovado' },
            { value: 'pending', label: 'Pendente' },
            { value: 'active', label: 'Ativo' },
            { value: 'inactive', label: 'Inativo' },
          ]} />
          <Select allowClear style={{ width: 220 }} placeholder="Filtrar por perfil" value={filterProfile} onChange={setFilterProfile} options={profiles.map((p: Profile) => ({ value: p.id, label: p.name }))} />
          {perms.create && (
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingUserId(null); setModalOpen(true); }}>
              Novo Usuário
            </Button>
          )}
        </Space>
      </div>

      <Card>
        <Table 
          columns={columns as any} 
          dataSource={dataSource} 
          pagination={{ pageSize, showSizeChanger: true, pageSizeOptions: [5, 8, 10, 20], onChange: (_page, size) => setPageSize(size || pageSize) }}
        />
      </Card>

      <UsuarioModal open={modalOpen} onClose={() => setModalOpen(false)} initial={editingUser} />
    </div>
  );
};

export default Usuarios;