import React, { useState } from 'react';
import { Layout as AntLayout } from 'antd';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../contexts/AuthContext';

const { Content } = AntLayout;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user } = useAuth();
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(true);
  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      {/* Navbar */}
      <Navbar sidebarCollapsed={sidebarCollapsed} onToggleSidebar={() => setSidebarCollapsed(prev => !prev)} />


      <AntLayout>
        {/* Sidebar Administrativo (apenas para admin) */}
        {user?.profile === 'admin' && <Sidebar collapsed={sidebarCollapsed} />}
        {/* Conteúdo Principal */}
        <Content
          style={{
            background: '#f5f5f5',
            minHeight: 'calc(100vh - 268px)',
            width: '100%',
            maxWidth: 'none',
            padding: 0,
            margin: 0,
            position: 'relative',
            left: 0,
          }}
        >
          <div
            className="content-wrapper"
            style={{
              width: '100%',
              maxWidth: 'none',
              margin: 0,
              padding: 0,
            }}
          >
            {children}
          </div>
        </Content>
      </AntLayout>

      {/* Footer */}
      <Footer />
    </AntLayout>
  );
};

export default Layout;
