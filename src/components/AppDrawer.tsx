import React, { useState } from 'react';
import { Drawer, Button, Space } from 'antd';
import { useNavigate } from 'react-router-dom';
import {
  AppstoreOutlined,
  CalendarOutlined,
  CompassOutlined,
  TeamOutlined,
  ProjectOutlined,
  ReadOutlined,
  LoginOutlined,
  GlobalOutlined,
  DownOutlined,
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { useI18n } from '../i18n/I18nContext';

interface AppDrawerProps {
  trigger?: React.ReactNode;
}

const AppDrawer: React.FC<AppDrawerProps> = ({ trigger }) => {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { t, locale, setLocale } = useI18n();

  const go = (path: string) => {
    navigate(path);
    setOpen(false);
  };

  const onLogout = () => {
    logout();
    navigate('/login');
    setOpen(false);
  };

  const options = [
    { key: 'home', icon: <AppstoreOutlined style={{ fontSize: 22 }} />, label: t('nav.home'), path: '/home' },
    { key: 'oportunidades', icon: <ProjectOutlined style={{ fontSize: 22 }} />, label: t('nav.oportunidades'), path: '/oportunidades' },
    { key: 'eventos', icon: <CalendarOutlined style={{ fontSize: 22 }} />, label: t('nav.eventos'), path: '/eventos' },
    { key: 'espacos', icon: <CompassOutlined style={{ fontSize: 22 }} />, label: t('nav.espacos'), path: '/espacos' },
    { key: 'agentes', icon: <TeamOutlined style={{ fontSize: 22 }} />, label: t('nav.agentes'), path: '/agentes' },
    { key: 'projetos', icon: <ProjectOutlined style={{ fontSize: 22 }} />, label: t('nav.projetos'), path: '/projetos' },
    { key: 'cursos', icon: <ReadOutlined style={{ fontSize: 22 }} />, label: t('nav.cursos'), path: '/cursos' },
  ];

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
        height={280}
        onClose={() => setOpen(false)}
        open={open}
        styles={{ body: { padding: 12 } }}
      >
        <div style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 12 }}>
          {/* Opções em linha com rolagem horizontal quando necessário */}
          <div style={{ flex: 1, overflowX: 'auto', whiteSpace: 'nowrap', padding: '6px 4px' }}>
            {options.map(opt => (
              <Button
                key={opt.key}
                type="text"
                size="large"
                icon={opt.icon}
                onClick={() => go(opt.path)}
                style={{ marginRight: 8 }}
              >
                {opt.label}
              </Button>
            ))}
          </div>

          {/* Ações à direita: idioma e sair */}
          <Space align="center">
            <Button type={locale === 'pt' ? 'primary' : 'default'} icon={<GlobalOutlined style={{ fontSize: 18 }} />} onClick={() => setLocale('pt')}>PT</Button>
            <Button type={locale === 'en' ? 'primary' : 'default'} icon={<GlobalOutlined style={{ fontSize: 18 }} />} onClick={() => setLocale('en')}>EN</Button>
            {user && (
              <Button danger icon={<LoginOutlined style={{ fontSize: 18 }} />} onClick={onLogout}>Sair</Button>
            )}
          </Space>
        </div>
      </Drawer>
    </>
  );
};

export default AppDrawer;