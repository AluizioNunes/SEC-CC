import React from 'react';
import { Button, Menu, Dropdown, Avatar, Row, Col } from 'antd';
import {
  UserOutlined,
  LoginOutlined,
  UserAddOutlined,
  SettingOutlined,
  LogoutOutlined,
  DownOutlined,
  ArrowRightOutlined,
  DashboardOutlined,
  MenuOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import logoImage from '../Images/SEC_GOV-LogoOficial.png';
import { useI18n } from '../i18n/I18nContext';
import AppDrawer from './AppDrawer';

interface NavbarProps {
  mobile?: boolean;
  showBackButton?: boolean;
  backButtonText?: string;
  backButtonPath?: string;
  sidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
}

const Navbar: React.FC<NavbarProps> = ({
  mobile = false,
  showBackButton = false,
  backButtonText = "Voltar",
  backButtonPath = "/",
  sidebarCollapsed = true,
  onToggleSidebar,
}) => {
  const { user, logout, loading } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const { t, locale, setLocale } = useI18n();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const publicMenuItems = [
    {
      key: 'home',
      icon: <UserOutlined />,
      label: t('nav.home'),
    },
    {
      key: 'sobre',
      icon: <UserOutlined />,
      label: t('nav.sobre'),
    },
    {
      key: 'contato',
      icon: <UserOutlined />,
      label: 'Contato',
    },
    {
      key: 'oportunidades',
      icon: <UserOutlined />,
      label: t('nav.oportunidades'),
    },
    {
      key: 'eventos',
      icon: <UserOutlined />,
      label: t('nav.eventos'),
    },
    {
      key: 'espacos',
      icon: <UserOutlined />,
      label: t('nav.espacos'),
    },
    {
      key: 'agentes',
      icon: <UserOutlined />,
      label: t('nav.agentes'),
    },
    {
      key: 'projetos',
      icon: <UserOutlined />,
      label: t('nav.projetos'),
    },
    {
      key: 'cursos',
      icon: <UserOutlined />,
      label: t('nav.cursos'),
    },
  ];

  const userMenuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: t('nav.dashboard'),
    },
    {
      key: 'CadastroPF',
      icon: <UserOutlined />,
      label: t('nav.cadastroPF'),
    },
    {
      key: 'configuracoes',
      icon: <SettingOutlined />,
      label: 'Configurações',
    },
  ];

  const getMenuItems = () => {
    if (loading) return publicMenuItems;

    if (user) {
      return user.profile === 'admin' ? [
        {
          key: 'dashboard',
          icon: <DashboardOutlined />,
          label: 'DASHBOARD',
        },
      ] : userMenuItems;
    }
    return publicMenuItems;
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
        {t('nav.logout')}
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
                  <Link to="/login">LOGIN</Link>
                </Button>
                <Button type="primary" icon={<UserAddOutlined />} block>
                  <Link to="/Cadastros">CADASTRAR</Link>
                </Button>
              </div>
            </div>
          )}

          {user && (
            <div style={{ padding: '16px 0', borderTop: '1px solid #f0f0f0' }}>
              <Dropdown overlay={userMenu} trigger={["click"]}>
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
      <Row align="middle" style={{ height: '160px' }}>
        {/* Controles e Logo */}
         <Col xs={24} sm={8} md={6} lg={4}>
           <div style={{ display: 'flex', alignItems: 'center' }}>
            {/* Botões antes da logomarca: Sidebar (toggle) e Drawer */}
            {user?.profile === 'admin' && (
              <Button
                type="text"
                icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                onClick={onToggleSidebar}
                aria-label="Alternar sidebar"
                style={{ marginRight: 8 }}
              />
            )}
            <AppDrawer trigger={<Button type="text" icon={<DownOutlined />} aria-label="Abrir menu" />} />
            {/* Botão Voltar (quando necessário) */}
            {showBackButton && (
              <Link to={backButtonPath} style={{ marginRight: '16px' }}>
                <Button
                  type="text"
                  icon={<ArrowRightOutlined style={{ transform: 'rotate(180deg)' }} />}
                  style={{
                    fontSize: '16px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '6px'
                  }}
                >
                  {backButtonText}
                </Button>
              </Link>
            )}

            <Link to="/home" style={{ textDecoration: 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <img
                  src={logoImage}
                  alt="SEC"
                  style={{
                    width: 'auto',
                    height: '108px',
                    marginRight: '0.5rem',
                    objectFit: 'contain',
                    objectPosition: 'center',
                    display: 'block',
                    flexShrink: 0
                  }}
                />
              </div>
            </Link>
          </div>
        </Col>

        <Col xs={24} sm={16} md={18} lg={20}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
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

            <Dropdown
              overlay={
                <Menu>
                  <Menu.Item key="lang-pt" onClick={() => setLocale('pt')}>{t('common.language.pt')}</Menu.Item>
                  <Menu.Item key="lang-en" onClick={() => setLocale('en')}>{t('common.language.en')}</Menu.Item>
                </Menu>
              }
              trigger={["click"]}
            >
              <Button type="text" style={{ marginRight: '12px' }}>{t('nav.language')}: {locale.toUpperCase()}</Button>
            </Dropdown>

            {user ? (
              <Dropdown overlay={userMenu} trigger={["click"]}>
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
                  <Link to="/login">{t('nav.login')}</Link>
                </Button>
                <Button type="primary" icon={<UserAddOutlined />}>
                  <Link to="/Cadastros">{t('nav.register')}</Link>
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
