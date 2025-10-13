import React, { useState } from 'react';
import { Layout as AntLayout, Drawer, Button, Row, Col } from 'antd';
import { motion } from 'framer-motion';
import {
  DashboardOutlined,
  UserOutlined,
  FileTextOutlined,
  MessageOutlined,
  SettingOutlined,
  QuestionCircleOutlined,
  MenuOutlined,
  CloseOutlined,
  TeamOutlined,
  BarChartOutlined,
  DatabaseOutlined,
  SyncOutlined,
  FilePdfOutlined,
  BookOutlined,
  CustomerServiceOutlined
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';
import { useAuth } from '../contexts/AuthContext';

const { Header, Content } = AntLayout;

interface LayoutProps {
  children: React.ReactNode;
}

// Componente para menu móvel em formato horizontal
const MobileMenuHorizontal: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const { user } = useAuth();
  const location = useLocation();

  const getMenuItems = () => {
    if (!user) {
      return [
        { key: 'sobre', icon: <BookOutlined />, label: 'Sobre', path: '/sobre' },
        { key: 'contato', icon: <MessageOutlined />, label: 'Contato', path: '/contato' },
        { key: 'resultados', icon: <BarChartOutlined />, label: 'Resultados', path: '/resultados' },
      ];
    }

    switch (user.profile) {
      case 'admin':
        return [
          { key: 'admin-dashboard', icon: <BarChartOutlined />, label: 'Dashboard', path: '/admin/dashboard' },
          { key: 'cadastros', icon: <TeamOutlined />, label: 'Cadastros', path: '/admin/cadastros' },
          { key: 'analises', icon: <DatabaseOutlined />, label: 'Análises', path: '/admin/analises' },
          { key: 'relatorios', icon: <FilePdfOutlined />, label: 'Relatórios', path: '/admin/relatorios' },
          { key: 'config', icon: <SettingOutlined />, label: 'Configurações', path: '/admin/configuracoes' },
          { key: 'suporte', icon: <CustomerServiceOutlined />, label: 'Suporte', path: '/admin/chamados' },
        ];
      case 'user':
      default:
        return [
          { key: 'dashboard', icon: <DashboardOutlined />, label: 'Dashboard', path: '/dashboard' },
          { key: 'cadastro', icon: <UserOutlined />, label: 'Meu Cadastro', path: '/meu-cadastro' },
          { key: 'solicitacoes', icon: <FileTextOutlined />, label: 'Solicitações', path: '/solicitacoes' },
          { key: 'notificacoes', icon: <MessageOutlined />, label: 'Notificações', path: '/notificacoes' },
          { key: 'configuracoes', icon: <SettingOutlined />, label: 'Configurações', path: '/configuracoes' },
          { key: 'ajuda', icon: <QuestionCircleOutlined />, label: 'Ajuda', path: '/faq' },
        ];
    }
  };

  const menuItems = getMenuItems();

  return (
    <div style={{ padding: '20px', background: '#fff' }}>
      <div style={{ textAlign: 'right', marginBottom: '20px' }}>
        <Button
          type="text"
          icon={<CloseOutlined />}
          onClick={onClose}
          style={{ border: 'none', fontSize: '18px' }}
        />
      </div>

      <Row gutter={[16, 16]}>
        {menuItems.map((item) => (
          <Col xs={12} sm={8} md={6} lg={4} key={item.key}>
            <Link to={item.path} onClick={onClose}>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '16px 8px',
                  borderRadius: '8px',
                  background: location.pathname === item.path ? '#e6f7ff' : '#fafafa',
                  border: location.pathname === item.path ? '2px solid #1890ff' : '1px solid #d9d9d9',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  minHeight: '80px',
                  textAlign: 'center',
                }}
              >
                <div style={{
                  fontSize: '24px',
                  color: location.pathname === item.path ? '#1890ff' : '#666',
                  marginBottom: '8px'
                }}>
                  {item.icon}
                </div>
                <div style={{
                  fontSize: '12px',
                  fontWeight: 'bold',
                  color: location.pathname === item.path ? '#1890ff' : '#333',
                  textTransform: 'uppercase',
                }}>
                  {item.label}
                </div>
              </motion.div>
            </Link>
          </Col>
        ))}
      </Row>
    </div>
  );
};

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [mobileMenuVisible, setMobileMenuVisible] = useState(false);

  const toggleMobileMenu = () => {
    setMobileMenuVisible(!mobileMenuVisible);
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      {/* Header/Navbar - Fixo no topo */}
      <Header style={{
        background: '#fff',
        padding: 0,
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
        position: 'sticky',
        top: 0,
        zIndex: 1000,
        height: '64px',
      }}>
        <Navbar
          onMobileMenuToggle={toggleMobileMenu}
          onSidebarToggle={() => {}} // Função vazia já que não temos mais sidebar
          sidebarCollapsed={true} // Sempre colapsado já que removemos o sidebar
        />
      </Header>

      <AntLayout>
        {/* Drawer SUPERIOR - abre de cima para baixo com menu HORIZONTAL */}
        <Drawer
          title={
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <MenuOutlined />
              <span>MENU DE NAVEGAÇÃO</span>
            </div>
          }
          placement="top" // Abre de cima para baixo
          onClose={toggleMobileMenu}
          visible={mobileMenuVisible}
          bodyStyle={{ padding: 0 }}
          height={320} // Altura reduzida para melhor visualização
          style={{
            zIndex: 1001,
            borderRadius: '0 0 8px 8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
          }}
        >
          <MobileMenuHorizontal onClose={toggleMobileMenu} />
        </Drawer>

        {/* Conteúdo Principal - Começa da coluna 0 (borda esquerda) */}
        <Content
          style={{
            background: '#f5f5f5',
            minHeight: 'calc(100vh - 64px)',
            width: '100%',
            maxWidth: 'none',
            padding: 0,
            margin: 0,
            position: 'relative',
            left: 0,
          }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="content-wrapper"
            style={{
              width: '100%',
              maxWidth: 'none',
              margin: 0,
              padding: 0,
            }}
          >
            {children}
          </motion.div>
        </Content>
      </AntLayout>

      {/* Footer - Altura reduzida */}
      <Footer />
    </AntLayout>
  );
};

export default Layout;
