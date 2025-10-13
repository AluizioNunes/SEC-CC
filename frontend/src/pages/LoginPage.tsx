import React from 'react';
import { Typography } from 'antd';

const { Title } = Typography;

const LoginPage: React.FC = () => {
  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <Title level={2}>Login</Title>
      <p>Página de login em desenvolvimento</p>
    </div>
  );
};

export default LoginPage;
