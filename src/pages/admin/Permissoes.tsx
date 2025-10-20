import React, { useEffect, useMemo, useState } from 'react';
import { Card, Col, Row, Select, Table, Checkbox, Button, message, Alert } from 'antd';
import { useAdmin } from '../../contexts/AdminContext';
import type { Profile } from '../../contexts/AdminContext';
import { useAuth } from '../../contexts/AuthContext';
import LogsModal from '../../components/modals/LogsModal';

// Tipos locais para evitar erros de importação
type ScreenKey = 'usuarios' | 'perfil' | 'permissoes';
interface ActionsPermission { view: boolean; create: boolean; edit: boolean; delete: boolean; }

const Permissoes: React.FC = () => {
  const { profiles, getPermissionsForProfile, setPermissionsForProfile } = useAdmin();
  // Lista estática de telas suportadas pelo AdminContext atual
  const screensList: ScreenKey[] = ['usuarios', 'perfil', 'permissoes'];
  const { user } = useAuth();
  const [selectedProfileId, setSelectedProfileId] = useState<string | null>((profiles as Profile[])[0]?.id || null);
  const [matrix, setMatrix] = useState<Record<ScreenKey, ActionsPermission>>({} as any);
  const [logsOpen, setLogsOpen] = useState(false);
  const currentProfileId = user?.profile === 'admin' ? 'p-admin' : 'p-usuario';
  const perms = getPermissionsForProfile(currentProfileId)?.screens?.permissoes || { view: true, create: true, edit: true, delete: true };

  useEffect(() => {
    if (!selectedProfileId && profiles.length) {
      setSelectedProfileId(profiles[0].id);
    }
  }, [profiles, selectedProfileId]);

  useEffect(() => {
    if (selectedProfileId) {
      const current = getPermissionsForProfile(selectedProfileId);
      if (current) setMatrix(current.screens);
    }
  }, [selectedProfileId, getPermissionsForProfile]);

  const columns = [
    { title: 'Tela', dataIndex: 'screen', key: 'screen' },
    { title: 'Ver', dataIndex: 'view', key: 'view', render: (_: any, r: any) => (
      <Checkbox checked={!!r.view} onChange={(e) => toggle(r.key, 'view', e.target.checked)} disabled={!perms.edit} />
    ) },
    { title: 'Cadastrar', dataIndex: 'create', key: 'create', render: (_: any, r: any) => (
      <Checkbox checked={!!r.create} onChange={(e) => toggle(r.key, 'create', e.target.checked)} disabled={!perms.edit} />
    ) },
    { title: 'Editar', dataIndex: 'edit', key: 'edit', render: (_: any, r: any) => (
      <Checkbox checked={!!r.edit} onChange={(e) => toggle(r.key, 'edit', e.target.checked)} disabled={!perms.edit} />
    ) },
    { title: 'Excluir', dataIndex: 'delete', key: 'delete', render: (_: any, r: any) => (
      <Checkbox checked={!!r.delete} onChange={(e) => toggle(r.key, 'delete', e.target.checked)} disabled={!perms.edit} />
    ) },
  ];

  const dataSource = useMemo(() => screensList.map((k) => ({
    key: k,
    screen: labelForScreen(k),
    view: matrix?.[k]?.view,
    create: matrix?.[k]?.create,
    edit: matrix?.[k]?.edit,
    delete: matrix?.[k]?.delete,
  })), [screensList, matrix]);

  const toggle = (screen: ScreenKey, action: keyof ActionsPermission, checked: boolean) => {
    setMatrix(prev => ({ ...prev, [screen]: { ...prev[screen], [action]: checked } }));
  };

  function labelForScreen(k: ScreenKey): string {
    const map: Record<ScreenKey, string> = {
      usuarios: 'Usuários',
      perfil: 'Perfil',
      permissoes: 'Permissões',
    };
    return map[k];
  }

  const save = () => {
    if (!selectedProfileId) return;
    setPermissionsForProfile(selectedProfileId, matrix, user ? { id: user.id, name: user.name } : undefined);
    message.success('Permissões salvas');
  };
  if (!perms.view) {
    return (
      <Alert type="warning" message="Você não tem permissão para visualizar Permissões" showIcon style={{ margin: 16 }} />
    );
  }

  return (
    <div style={{ padding: 16 }}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card>
            <Select
              style={{ width: 320 }}
              placeholder="Selecione o perfil"
              value={selectedProfileId || undefined}
              options={(profiles as Profile[]).map(p => ({ value: p.id, label: p.name }))}
              onChange={(v) => setSelectedProfileId(v)}
            />
            <div style={{ marginTop: 16 }}>
              <Table columns={columns} dataSource={dataSource} pagination={false} />
            </div>
            <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
              <Button onClick={() => setLogsOpen(true)}>Ver Auditoria</Button>
              <Button type="primary" onClick={save} disabled={!perms.edit}>Salvar Permissões</Button>
            <LogsModal open={logsOpen} onClose={() => setLogsOpen(false)} entityFilter={["permission"]} />
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Permissoes;