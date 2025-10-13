import React from 'react';
import { Typography } from 'antd';

const { Title } = Typography;

const AdminPage: React.FC = () => {
  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <Title level={2}>Área Administrativa</Title>
      <p>Interface para a Comissão de Análise</p>
    </div>
  );
};

export default AdminPage;
