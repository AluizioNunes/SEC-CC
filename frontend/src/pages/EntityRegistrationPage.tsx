import React from 'react';
import { Typography } from 'antd';

const { Title } = Typography;

const EntityRegistrationPage: React.FC = () => {
  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <Title level={2}>Cadastro Pessoa Jurídica</Title>
      <p>Formulário para espaços culturais em desenvolvimento</p>
    </div>
  );
};

export default EntityRegistrationPage;
