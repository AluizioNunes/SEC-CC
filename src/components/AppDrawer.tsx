import React, { useState } from 'react';
import { Drawer, Menu, Divider, Button, Space, Typography } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import {
  MenuOutlined,
  AppstoreOutlined,
  CalendarOutlined,
  CompassOutlined,
  TeamOutlined,
  ProjectOutlined,
  ReadOutlined,
  DashboardOutlined,
  LoginOutlined,
  SettingOutlined,
  GlobalOutlined,
  DownOutlined,
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { useI18n } from '../i18n/I18nContext';

const { Text } = Typography;

interface AppDrawerProps {
  trigger?: React.ReactNode;
}

const AppDrawer: React.FC<AppDrawerProps> = ({ trigger }) => {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { t, locale, setLocale } = useI18n();

  const onLogout = () => {
    logout();
    navigate('/login');
    setOpen(false);
  };

  return (
    <>
      {trigger ? (
        <div onClick={() => setOpen(true)} style={{ display: 'inline-flex' }}>{trigger}</div>
      ) : (
        <Button type="text" icon={<DownOutlined />} onClick={() => setOpen(true)}>
          {t('nav.menu') || 'Menu'}
        </Button>
      )}

      <Drawer
        title={null}
        placement="top"
        height={360}
        onClose={() => setOpen(false)}
        open={open}
      >
        <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Menu
            mode="horizontal"
            items={[
              { key: 'home', icon: <AppstoreOutlined />, label: <Link to="/home" onClick={() => setOpen(false)}>{t('nav.home')}</Link> },
              { key: 'oportunidades', icon: <ProjectOutlined />, label: <Link to="/oportunidades" onClick={() => setOpen(false)}>{t('nav.oportunidades')}</Link> },
              { key: 'eventos', icon: <CalendarOutlined />, label: <Link to="/eventos" onClick={() => setOpen(false)}>{t('nav.eventos')}</Link> },
              { key: 'espacos', icon: <CompassOutlined />, label: <Link to="/espacos" onClick={() => setOpen(false)}>{t('nav.espacos')}</Link> },
              { key: 'agentes', icon: <TeamOutlined />, label: <Link to="/agentes" onClick={() => setOpen(false)}>{t('nav.agentes')}</Link> },
              { key: 'projetos', icon: <ProjectOutlined />, label: <Link to="/projetos" onClick={() => setOpen(false)}>{t('nav.projetos')}</Link> },
              { key: 'cursos', icon: <ReadOutlined />, label: <Link to="/cursos" onClick={() => setOpen(false)}>{t('nav.cursos')}</Link> },
            ]}
            style={{ border: 'none' }}
          />
          <div style={{ display: 'flex', gap: 8 }}>
            <Button type={locale === 'pt' ? 'primary' : 'default'} icon={<GlobalOutlined />} onClick={() => setLocale('pt')}>PT</Button>
            <Button type={locale === 'en' ? 'primary' : 'default'} icon={<GlobalOutlined />} onClick={() => setLocale('en')}>EN</Button>
            {user && (
              <Button danger icon={<LoginOutlined />} onClick={onLogout}>Sair</Button>
            )}
          </div>
        </div>
      </Drawer>
    </>
  );
};

export default AppDrawer;