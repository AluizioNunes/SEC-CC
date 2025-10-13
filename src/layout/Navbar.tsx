import React from 'react';
import { Button, Menu, Dropdown, Avatar, Row, Col } from 'antd';
import {
  MenuOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  HomeOutlined,
  InfoCircleOutlined,
  PhoneOutlined,
  FileTextOutlined,
  LoginOutlined,
  UserAddOutlined,
  DownOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';

interface NavbarProps {
  onMobileMenuToggle?: () => void;
  onSidebarToggle?: () => void;
  sidebarCollapsed?: boolean;
  mobile?: boolean;
}

const Navbar: React.FC<NavbarProps> = ({ onMobileMenuToggle, onSidebarToggle, sidebarCollapsed = false, mobile = false }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const publicMenuItems = [
    {
      key: 'home',
      icon: <HomeOutlined />,
      label: 'INÍCIO',
    },
    {
      key: 'sobre',
      icon: <InfoCircleOutlined />,
      label: 'SOBRE',
    },
    {
      key: 'resultados',
      icon: <FileTextOutlined />,
      label: 'RESULTADOS',
    },
    {
      key: 'contato',
      icon: <PhoneOutlined />,
      label: 'CONTATO',
    },
  ];

  const userMenuItems = [
    {
      key: 'dashboard',
      icon: <HomeOutlined />,
      label: 'DASHBOARD',
    },
    {
      key: 'cadastro',
      icon: <UserOutlined />,
      label: 'MEU CADASTRO',
    },
    {
      key: 'solicitacoes',
      icon: <FileTextOutlined />,
      label: 'SOLICITAÇÕES',
    },
    {
      key: 'configuracoes',
      icon: <SettingOutlined />,
      label: 'CONFIGURAÇÕES',
    },
  ];

  const adminMenuItems = [
    {
      key: 'admin-dashboard',
      icon: <HomeOutlined />,
      label: 'DASHBOARD',
    },
    {
      key: 'cadastros',
      icon: <UserOutlined />,
      label: 'GERENCIAR CADASTROS',
    },
    {
      key: 'relatorios',
      icon: <FileTextOutlined />,
      label: 'RELATÓRIOS',
    },
    {
      key: 'configuracoes',
      icon: <SettingOutlined />,
      label: 'CONFIGURAÇÕES',
    },
  ];

  const getMenuItems = () => {
    if (!user) return publicMenuItems;
    return user.profile === 'admin' ? adminMenuItems : userMenuItems;
  };

  const userMenu = (
    <Menu>
      <Menu.Item key="profile" icon={<UserOutlined />}>
        <Link to="/perfil">MEU PERFIL</Link>
      </Menu.Item>
      <Menu.Item key="settings" icon={<SettingOutlined />}>
        <Link to="/configuracoes">CONFIGURAÇÕES</Link>
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
        SAIR
      </Menu.Item>
    </Menu>
  );

  if (mobile) {
    return (
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        style={{
          background: '#fff',
          borderBottom: '1px solid #e8e8e8',
          padding: '16px 24px'
        }}
      >
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <Menu
            mode="vertical"
            items={getMenuItems().map(item => ({
              key: item.key,
              icon: item.icon,
              label: <Link to={`/${item.key}`} style={{ textDecoration: 'none' }}>{item.label}</Link>,
            }))}
            style={{
              border: 'none',
              background: 'transparent',
            }}
            theme="light"
          />

          {!user && (
            <div style={{ padding: '16px 0', borderTop: '1px solid #f0f0f0' }}>
              <div style={{ display: 'flex', gap: '8px', flexDirection: 'column' }}>
                <Button type="text" icon={<LoginOutlined />} block>
                  <Link to="/login">ENTRAR</Link>
                </Button>
                <Button type="primary" icon={<UserAddOutlined />} block>
                  <Link to="/cadastro">CADASTRAR</Link>
                </Button>
              </div>
            </div>
          )}

          {user && (
            <div style={{ padding: '16px 0', borderTop: '1px solid #f0f0f0' }}>
              <Dropdown overlay={userMenu} trigger={['click']}>
                <div style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', padding: '8px' }}>
                  <Avatar icon={<UserOutlined />} style={{ marginRight: 8 }} />
                  <span>{user.name.toUpperCase()}</span>
                  <DownOutlined style={{ marginLeft: 'auto' }} />
                </div>
              </Dropdown>
            </div>
          )}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        background: '#fff',
        borderBottom: '1px solid #e8e8e8',
        padding: '0 24px'
      }}
    >
      <Row align="middle" style={{ height: '64px' }}>
        {/* Logo e Título */}
        <Col xs={24} sm={8} md={6} lg={4}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            {/* Botões de controle lado a lado */}
            <div style={{ display: 'flex', gap: '8px', marginRight: '16px' }}>
              {onMobileMenuToggle && (
                <Button
                  type="text"
                  icon={<DownOutlined />}
                  onClick={onMobileMenuToggle}
                  style={{
                    fontSize: '16px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '6px'
                  }}
                />
              )}

              {onSidebarToggle && onSidebarToggle.toString() !== '() => {}' && (
                <Button
                  type="text"
                  icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                  onClick={onSidebarToggle}
                  style={{
                    fontSize: '16px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '6px'
                  }}
                />
              )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                width: '40px',
                height: '40px',
                background: 'linear-gradient(135deg, #1e3c72, #2a5298)',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '12px',
                fontSize: '18px',
                fontWeight: 'bold',
                color: 'white'
              }}>
                SEC
              </div>
              <div>
                <div style={{
                  fontSize: '16px',
                  fontWeight: 'bold',
                  color: '#1e3c72',
                  lineHeight: 1.2
                }}>
                  CADASTRO CULTURAL
                </div>
                <div style={{
                  fontSize: '11px',
                  color: '#666',
                  lineHeight: 1
                }}>
                  GOVERNO DO AMAZONAS
                </div>
              </div>
            </div>
          </div>
        </Col>

        {/* Menu Principal */}
        <Col xs={0} sm={16} md={18} lg={20}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
            {/* Menu de Navegação */}
            <Menu
              mode="horizontal"
              items={getMenuItems().map(item => ({
                key: item.key,
                icon: item.icon,
                label: <Link to={`/${item.key}`}>{item.label}</Link>,
              }))}
              style={{
                border: 'none',
                background: 'transparent',
                marginRight: '24px'
              }}
              theme="light"
            />

            {/* Área de Autenticação */}
            {user ? (
              <Dropdown overlay={userMenu} trigger={['click']}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  cursor: 'pointer',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  transition: 'background 0.3s'
                }}>
                  <Avatar
                    icon={<UserOutlined />}
                    style={{
                      marginRight: 8,
                      backgroundColor: user.profile === 'admin' ? '#722ed1' : '#1e3c72'
                    }}
                  />
                  <span style={{ marginRight: 8 }}>{user.name.toUpperCase()}</span>
                  <DownOutlined />
                </div>
              </Dropdown>
            ) : (
              <div style={{ display: 'flex', gap: '8px' }}>
                <Button type="text" icon={<LoginOutlined />}>
                  <Link to="/login">ENTRAR</Link>
                </Button>
                <Button type="primary" icon={<UserAddOutlined />}>
                  <Link to="/cadastro">CADASTRAR</Link>
                </Button>
              </div>
            )}
          </div>
        </Col>
      </Row>
    </motion.div>
  );
};

export default Navbar;
