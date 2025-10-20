import React, { useMemo, useState } from 'react';
import { Card, Col, Row, Statistic, Table, Tag, Button, Space, message, Alert } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, TeamOutlined } from '@ant-design/icons';
import { useAdmin, type Profile } from '../../contexts/AdminContext';
import PerfilModal from '../../components/modals/PerfilModal';
import { useAuth } from '../../contexts/AuthContext';

const Perfil: React.FC = () => {
  const { profiles, deleteProfile, getPermissionsForProfile } = useAdmin();
  const { user } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const currentProfileId = user?.profile === 'admin' ? 'p-admin' : 'p-usuario';
  const perms = getPermissionsForProfile(currentProfileId)?.screens?.perfil || { view: true, create: true, edit: true, delete: true };

  const stats = useMemo(() => ({ total: profiles.length }), [profiles]);

  const columns = [
    { title: 'Nome', dataIndex: 'name', key: 'name' },
    { title: 'Descrição', dataIndex: 'description', key: 'description' },
    perms.edit || perms.delete ? { title: 'Ações', key: 'actions', render: (_: any, r: any) => (
      <Space>
        {perms.edit && <Button icon={<EditOutlined />} onClick={() => { setEditingId(r.id); setModalOpen(true); }}>Editar</Button>}
        {perms.delete && <Button danger icon={<DeleteOutlined />} onClick={() => { deleteProfile(r.id, user ? { id: user.id, name: user.name } : undefined); message.success('Perfil removido'); }}>Excluir</Button>}
      </Space>
    ) } : undefined,
  ].filter(Boolean);

  const dataSource = profiles.map((p: Profile) => ({ key: p.id, ...p }));
  const editingProfile = profiles.find((p: Profile) => p.id === editingId) || null;

  if (!perms.view) {
    return <Alert type="warning" message="Você não tem permissão para visualizar Perfis" showIcon style={{ margin: 16 }} />;
  }

  return (
    <div style={{ padding: 16 }}>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic title="Total de Perfis" value={stats.total} prefix={<TeamOutlined />} />
          </Card>
        </Col>
      </Row>

      <div style={{ marginTop: 16, marginBottom: 16 }}>
        <Space>
          {perms.create && (
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingId(null); setModalOpen(true); }}>
              Novo Perfil
            </Button>
          )}
        </Space>
      </div>

      <Card>
        <Table columns={columns as any} dataSource={dataSource} pagination={{ pageSize: 8 }} />
      </Card>

      <PerfilModal open={modalOpen} onClose={() => setModalOpen(false)} initial={editingProfile} />
    </div>
  );
};

export default Perfil;