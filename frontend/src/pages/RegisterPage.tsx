import React, { useState } from 'react';
import { Button, Typography, Select, Form, Input } from 'antd';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const { Title } = Typography;
const { Option } = Select;

const RegisterPage: React.FC = () => {
  const [form] = Form.useForm();
  const [userType, setUserType] = useState<string | null>(null);

  const handleUserTypeChange = (value: string) => {
    setUserType(value);
  };

  const onFinish = (values: any) => {
    console.log('Form values:', values);
    // Redirect based on user type
    if (values.userType === 'individual') {
      window.location.href = '/register/individual';
    } else if (values.userType === 'entity') {
      window.location.href = '/register/entity';
    }
  };

  return (
    <div style={{ padding: '50px', maxWidth: '600px', margin: '0 auto' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Title level={2}>Cadastro Inicial</Title>
        <Form form={form} onFinish={onFinish} layout="vertical">
          <Form.Item
            name="fullName"
            label="Nome Completo"
            rules={[{ required: true, message: 'Por favor, insira seu nome completo' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="email"
            label="Email"
            rules={[{ required: true, type: 'email', message: 'Por favor, insira um email válido' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="password"
            label="Senha"
            rules={[{ required: true, message: 'Por favor, insira uma senha' }]}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item
            name="userType"
            label="Tipo de Solicitante"
            rules={[{ required: true, message: 'Por favor, selecione o tipo' }]}
          >
            <Select placeholder="Selecione" onChange={handleUserTypeChange}>
              <Option value="individual">Pessoa Física (Trabalhador da Cultura)</Option>
              <Option value="entity">Pessoa Jurídica (Espaço Cultural)</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Continuar Cadastro
            </Button>
          </Form.Item>
        </Form>
        <Link to="/">
          <Button>Voltar ao Início</Button>
        </Link>
      </motion.div>
    </div>
  );
};

export default RegisterPage;
