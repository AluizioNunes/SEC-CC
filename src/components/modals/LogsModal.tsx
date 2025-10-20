import React from 'react';
import { Modal, Table, Tag } from 'antd';
import { useAdmin, type AdminLog } from '../../contexts/AdminContext';

interface LogsModalProps {
  open: boolean;
  onClose: () => void;
  entityFilter?: Array<AdminLog['entity']>;
}

const LogsModal: React.FC<LogsModalProps> = ({ open, onClose, entityFilter }) => {
  const { logs } = useAdmin();

  const filtered: AdminLog[] = (logs || []).filter((l: AdminLog) => {
    if (!entityFilter || entityFilter.length === 0) return true;
    return entityFilter.includes(l.entity);
  });

  const columns = [
    { title: 'Quando', dataIndex: 'at', key: 'at', render: (v: number) => new Date(v).toLocaleString('pt-BR') },
    { title: 'Quem', dataIndex: ['by', 'name'], key: 'by' },
    { title: 'Entidade', dataIndex: 'entity', key: 'entity', render: (e: AdminLog['entity']) => {
        const map: Record<AdminLog['entity'], string> = { user: 'Usuário', profile: 'Perfil', permission: 'Permissão' };
        return <Tag>{map[e]}</Tag>;
      }
    },
    { title: 'Ação', dataIndex: 'action', key: 'action', render: (a: AdminLog['action']) => {
        const map: Record<AdminLog['action'], string> = { create: 'Criou', update: 'Atualizou', delete: 'Excluiu' };
        return <Tag color={a === 'delete' ? 'red' : a === 'create' ? 'green' : 'blue'}>{map[a]}</Tag>;
      }
    },
    { title: 'ID', dataIndex: 'entityId', key: 'entityId' },
    { title: 'Detalhes', dataIndex: 'details', key: 'details', render: (d: any) => d ? <code style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(d, null, 2)}</code> : '-' },
  ];

  return (
    <Modal open={open} onCancel={onClose} onOk={onClose} title="Auditoria" width={900} destroyOnClose>
      <Table columns={columns as any} dataSource={filtered.map(l => ({ ...l, key: l.id }))} pagination={{ pageSize: 8 }} />
    </Modal>
  );
};

export default LogsModal;