import React from 'react';
import { Avatar, Dropdown, Menu, Button } from 'antd';
import { UserOutlined, LogoutOutlined, SettingOutlined, DownOutlined, LoginOutlined, UserAddOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import logoImage from '../Images/SEC_GOV-LogoOficial.png';

interface NavbarCompactProps {
  variant?: 'modalHeader' | 'inline';
}

const NavbarCompact: React.FC<NavbarCompactProps> = ({ variant = 'inline' }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
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

  const containerStyle = variant === 'modalHeader'
    ? { background: 'transparent', borderBottom: 'none', padding: 0, borderRadius: 0 }
    : { background: '#fff', borderBottom: '1px solid #e8e8e8', padding: '8px 12px', borderRadius: 6 };

  return (
    <div style={containerStyle}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Link to="/home" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center' }}>
          <img
            src={logoImage}
            alt="SEC"
            style={{ height: 28, width: 'auto', display: 'block' }}
          />
        </Link>

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
          {!user ? (
            <>
              <Button type="text" size="small" icon={<LoginOutlined />}> 
                <Link to="/login">LOGIN</Link>
              </Button>
              <Button type="primary" size="small" icon={<UserAddOutlined />}> 
                <Link to="/Cadastros">CADASTRAR</Link>
              </Button>
            </>
          ) : (
            <Dropdown overlay={userMenu} trigger={["click"]}>
              <div style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', padding: '4px 8px' }}>
                <Avatar icon={<UserOutlined />} size={24} style={{ marginRight: 6 }} />
                <span style={{ fontSize: 13, fontWeight: 500 }}>{user.name}</span>
                <DownOutlined style={{ marginLeft: 8, fontSize: 10 }} />
              </div>
            </Dropdown>
          )}
        </div>
      </div>
    </div>
  );
};

export default NavbarCompact;