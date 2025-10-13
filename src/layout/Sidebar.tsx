import React from 'react';
import { Menu, Typography } from 'antd';
import {
  DashboardOutlined,
  UserOutlined,
  FileTextOutlined,
  SyncOutlined,
  MessageOutlined,
  SettingOutlined,
  QuestionCircleOutlined,
  PhoneOutlined,
  TeamOutlined,
  BarChartOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  AuditOutlined,
  FilePdfOutlined,
  BookOutlined,
  CustomerServiceOutlined
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';

const { SubMenu } = Menu;
const { Title } = Typography;

interface SidebarProps {
  collapsed?: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed = false }) => {
  const { user } = useAuth();
  const location = useLocation();

  // Menu para usuário público (não logado)
  const publicMenuItems = [
    {
      key: 'institucional',
      icon: <BookOutlined />,
      label: 'INSTITUCIONAL',
      children: [
        { key: 'sobre', label: <Link to="/sobre">SOBRE O CADASTRO</Link> },
        { key: 'contato', label: <Link to="/contato">CONTATO</Link> },
        { key: 'resultados', label: <Link to="/resultados">RESULTADOS</Link> },
      ],
    },
  ];

  // Menu para usuário logado (PF/PJ) - APENAS ÍCONES quando colapsado
  const userMenuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: collapsed ? null : <Link to="/dashboard">DASHBOARD</Link>,
      tooltip: 'Dashboard',
    },
    {
      key: 'cadastro',
      icon: <UserOutlined />,
      label: collapsed ? null : 'MEU CADASTRO',
      tooltip: 'Meu Cadastro',
      children: collapsed ? null : [
        { key: 'meu-cadastro', label: <Link to="/meu-cadastro">VISUALIZAR/EDITAR</Link> },
        { key: 'documentos', label: <Link to="/documentos">DOCUMENTOS</Link> },
      ],
    },
    {
      key: 'processos',
      icon: <FileTextOutlined />,
      label: collapsed ? null : 'PROCESSOS',
      tooltip: 'Processos',
      children: collapsed ? null : [
        { key: 'solicitacoes', label: <Link to="/solicitacoes">MINHAS SOLICITAÇÕES</Link> },
        { key: 'renovacao', label: <Link to="/renovacao">RENOVAÇÃO</Link> },
        { key: 'recurso', label: <Link to="/recurso">RECURSO</Link> },
        { key: 'diligencias', label: <Link to="/diligencias">DILIGÊNCIAS</Link> },
      ],
    },
    {
      key: 'comunicacao',
      icon: <MessageOutlined />,
      label: collapsed ? null : <Link to="/notificacoes">NOTIFICAÇÕES</Link>,
      tooltip: 'Notificações',
    },
    {
      key: 'configuracoes',
      icon: <SettingOutlined />,
      label: collapsed ? null : 'CONFIGURAÇÕES',
      tooltip: 'Configurações',
      children: collapsed ? null : [
        { key: 'perfil', label: <Link to="/perfil">MEU PERFIL</Link> },
        { key: 'lgpd', label: <Link to="/lgpd">LGPD</Link> },
      ],
    },
    {
      key: 'ajuda',
      icon: <QuestionCircleOutlined />,
      label: collapsed ? null : 'AJUDA',
      tooltip: 'Ajuda',
      children: collapsed ? null : [
        { key: 'faq', label: <Link to="/faq">FAQ</Link> },
        { key: 'suporte', label: <Link to="/suporte">SUPORTE</Link> },
      ],
    },
  ];

  // Menu para administração (comissão SEC)
  const adminMenuItems = [
    {
      key: 'admin-dashboard',
      icon: <BarChartOutlined />,
      label: collapsed ? null : <Link to="/admin/dashboard">DASHBOARD</Link>,
      tooltip: 'Dashboard Admin',
    },
    {
      key: 'monitoramento',
      icon: <DatabaseOutlined />,
      label: collapsed ? null : 'MONITORAMENTO',
      tooltip: 'Monitoramento',
      children: collapsed ? null : [
        { key: 'grafana', label: 'GRAFANA' },
      ],
    },
    {
      key: 'gestao-cadastros',
      icon: <TeamOutlined />,
      label: collapsed ? null : 'CADASTROS',
      tooltip: 'Cadastros',
      children: collapsed ? null : [
        { key: 'todos-cadastros', label: <Link to="/admin/cadastros">TODOS OS CADASTROS</Link> },
        { key: 'novas-solicitacoes', label: <Link to="/admin/novas">NOVAS SOLICITAÇÕES</Link> },
        { key: 'em-diligencia', label: <Link to="/admin/diligencias">EM DILIGÊNCIA</Link> },
        { key: 'recursos', label: <Link to="/admin/recursos">RECURSOS</Link> },
        { key: 'homologados', label: <Link to="/admin/homologados">HOMOLOGADOS</Link> },
        { key: 'indeferidos', label: <Link to="/admin/indeferidos">INDEFERIDOS</Link> },
      ],
    },
    {
      key: 'fluxos',
      icon: <SyncOutlined />,
      label: collapsed ? null : 'FLUXOS',
      tooltip: 'Fluxos',
      children: collapsed ? null : [
        { key: 'minhas-analises', label: <Link to="/admin/analises">MINHAS ANÁLISES</Link> },
        { key: 'distribuicao', label: <Link to="/admin/distribuicao">DISTRIBUIÇÃO</Link> },
        { key: 'automacoes', label: 'AUTOMAÇÕES' },
      ],
    },
    {
      key: 'administracao',
      icon: <SettingOutlined />,
      label: collapsed ? null : 'ADMINISTRAÇÃO',
      tooltip: 'Administração',
      children: collapsed ? null : [
        { key: 'usuarios', label: <Link to="/admin/usuarios">USUÁRIOS</Link> },
        { key: 'configuracoes', label: <Link to="/admin/configuracoes">CONFIGURAÇÕES</Link> },
        { key: 'auditoria', label: <Link to="/admin/auditoria">AUDITORIA</Link> },
      ],
    },
    {
      key: 'relatorios',
      icon: <FilePdfOutlined />,
      label: collapsed ? null : 'RELATÓRIOS',
      tooltip: 'Relatórios',
      children: collapsed ? null : [
        { key: 'gerar-relatorios', label: <Link to="/admin/relatorios">GERAR</Link> },
        { key: 'bi', label: 'BUSINESS INTELLIGENCE' },
      ],
    },
    {
      key: 'documentacao',
      icon: <BookOutlined />,
      label: collapsed ? null : 'DOCUMENTAÇÃO',
      tooltip: 'Documentação',
      children: collapsed ? null : [
        { key: 'legislacao', label: 'LEGISLAÇÃO' },
        { key: 'manuais', label: 'MANUAIS' },
      ],
    },
    {
      key: 'suporte-admin',
      icon: <CustomerServiceOutlined />,
      label: collapsed ? null : 'SUPORTE',
      tooltip: 'Suporte',
      children: collapsed ? null : [
        { key: 'chamados', label: <Link to="/admin/chamados">CHAMADOS</Link> },
      ],
    },
  ];

  const getMenuItems = () => {
    if (!user) {
      return publicMenuItems;
    }

    switch (user.profile) {
      case 'admin':
        return adminMenuItems;
      case 'user':
      default:
        return userMenuItems;
    }
  };

  const renderMenuItems = (items: any[]) => {
    return items.map((item) => {
      if (item.children && !collapsed) {
        return (
          <SubMenu key={item.key} icon={item.icon} title={item.label}>
            {renderMenuItems(item.children)}
          </SubMenu>
        );
      }

      return (
        <Menu.Item
          key={item.key}
          icon={item.icon}
          title={collapsed ? item.tooltip : undefined}
        >
          {item.label}
        </Menu.Item>
      );
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {!collapsed && user && (
        <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
          <Title level={5} style={{ margin: 0, color: '#1890ff', textTransform: 'uppercase' }}>
            {user.profile === 'admin' ? 'ADMINISTRAÇÃO SEC' : `OLÁ, ${user.name.toUpperCase()}`}
          </Title>
          {user.profile === 'admin' && (
            <div style={{ fontSize: '12px', color: '#666', textTransform: 'uppercase' }}>
              Comissão de Análise
            </div>
          )}
        </div>
      )}

      <Menu
        mode={collapsed ? "vertical" : "inline"}
        selectedKeys={[location.pathname]}
        defaultOpenKeys={collapsed ? [] : ['cadastro', 'processos', 'configuracoes', 'ajuda']}
        style={{
          height: '100%',
          borderRight: 0,
          background: '#fafafa',
        }}
        theme="light"
      >
        {renderMenuItems(getMenuItems())}
      </Menu>
    </motion.div>
  );
};

export default Sidebar;
