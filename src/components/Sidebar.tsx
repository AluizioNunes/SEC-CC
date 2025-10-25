import React from 'react';
import { Layout, Menu, Typography } from 'antd';
import {
  FormOutlined,
  DollarOutlined,
  AuditOutlined,
  MonitorOutlined,
  SettingOutlined,
  UserOutlined,
  SafetyOutlined,
  IdcardOutlined,
  FileSearchOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Sider } = Layout;
const { Text } = Typography;

const Sidebar: React.FC<{ collapsed: boolean }> = ({ collapsed }) => {
  const navigate = useNavigate();

  const items = [
    { key: 'cadastros', icon: <FormOutlined />, label: 'CADASTROS' },
    { key: 'financeiro', icon: <DollarOutlined />, label: 'FINANCEIRO' },
    { key: 'juridico', icon: <AuditOutlined />, label: 'JURÍDICO' },
    { key: 'monitoramento', icon: <MonitorOutlined />, label: 'MONITORAMENTO' },
    {
      key: 'sistema',
      icon: <SettingOutlined />,
      label: 'SISTEMA',
      children: [
        { key: 'sistema-usuarios', icon: <UserOutlined />, label: 'USUÁRIOS' },
        { key: 'sistema-permissoes', icon: <SafetyOutlined />, label: 'PERMISSÕES' },
        { key: 'sistema-perfil', icon: <IdcardOutlined />, label: 'PERFIL' },
        { key: 'sistema-auditoria', icon: <FileSearchOutlined />, label: 'AUDITORIA' },
      ],
    },
  ];

  const onClick = ({ key }: { key: string }) => {
    const map: Record<string, string> = {
      cadastros: '/admin/cadastros',
      financeiro: '/admin/financeiro',
      juridico: '/admin/juridico',
      monitoramento: '/admin/monitoramento',
      'sistema-usuarios': '/admin/usuarios',
      'sistema-permissoes': '/admin/permissoes',
      'sistema-perfil': '/admin/perfil',
      'sistema-auditoria': '/admin/auditoria',
    };
    navigate(map[key] || `/admin/${key}`);
  };

  return (
    <Sider width={256} collapsedWidth={64} collapsible collapsed={collapsed} trigger={null} theme="light" style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}>
      {!collapsed && (
        <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
          <Text strong>ADMINISTRAÇÃO</Text>
        </div>
      )}
      <Menu mode="inline" items={items} onClick={onClick} style={{ border: 'none' }} />
    </Sider>
  );
};

export default Sidebar;