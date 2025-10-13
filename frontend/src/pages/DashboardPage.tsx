import React from 'react';
import { Typography } from 'antd';

const { Title } = Typography;

const DashboardPage: React.FC = () => {
  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <Title level={2}>Dashboard do Usuário</Title>
      <p>Acompanhe o status do seu cadastro</p>
    </div>
  );
};

export default DashboardPage;
