import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, Alert, Row, Col, Divider } from 'antd';
import {
  UserOutlined,
  LockOutlined,
  LoginOutlined,
  EyeInvisibleOutlined,
  EyeOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';

const { Title, Paragraph } = Typography;

interface LoginFormValues {
  email: string;
  password: string;
  remember: boolean;
}

const Login: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (values: LoginFormValues) => {
    setLoading(true);
    setError(null);

    try {
      const success = await login(values.email, values.password);

      if (success) {
        navigate('/dashboard');
      } else {
        setError('Credenciais inválidas. Verifique seu e-mail e senha.');
      }
    } catch (err) {
      setError('Erro interno do servidor. Tente novamente em alguns minutos.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px'
    }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{ width: '100%', maxWidth: '500px' }}
      >
        <Card
          style={{
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
            borderRadius: '12px',
            overflow: 'hidden'
          }}
        >
          {/* Cabeçalho */}
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <div style={{
              fontSize: '48px',
              color: '#1890ff',
              marginBottom: '16px'
            }}>
              🚀
            </div>
            <Title level={2} style={{ margin: 0, color: '#1890ff' }}>
              SEC - Cadastro Cultural
            </Title>
            <Paragraph style={{ color: '#666', marginTop: '8px' }}>
              Entre na sua conta para continuar
            </Paragraph>
          </div>

          {/* Formulário */}
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            disabled={loading}
          >
            {error && (
              <Alert
                message={error}
                type="error"
                showIcon
                style={{ marginBottom: '24px' }}
              />
            )}

            <Form.Item
              label="E-mail"
              name="email"
              rules={[
                { required: true, message: 'Por favor, digite seu e-mail!' },
                { type: 'email', message: 'Digite um e-mail válido!' }
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="seu@email.com"
                size="large"
                autoComplete="email"
              />
            </Form.Item>

            <Form.Item
              label="Senha"
              name="password"
              rules={[
                { required: true, message: 'Por favor, digite sua senha!' },
                { min: 6, message: 'A senha deve ter pelo menos 6 caracteres!' }
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Digite sua senha"
                size="large"
                iconRender={(visible) =>
                  visible ? <EyeOutlined /> : <EyeInvisibleOutlined />
                }
              />
            </Form.Item>

            <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
              <Col>
                <Form.Item name="remember" valuePropName="checked" noStyle>
                  <label style={{ cursor: 'pointer' }}>
                    <input type="checkbox" style={{ marginRight: '8px' }} />
                    Lembrar de mim
                  </label>
                </Form.Item>
              </Col>
              <Col>
                <Link to="/esqueci-senha" style={{ color: '#1890ff' }}>
                  Esqueci minha senha
                </Link>
              </Col>
            </Row>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                icon={<LoginOutlined />}
                size="large"
                block
              >
                {loading ? 'Entrando...' : 'Entrar'}
              </Button>
            </Form.Item>
          </Form>

          <Divider>ou</Divider>

          {/* Links adicionais */}
          <div style={{ textAlign: 'center', marginTop: '24px' }}>
            <Paragraph style={{ color: '#666' }}>
              Ainda não tem cadastro?
            </Paragraph>
            <Link to="/cadastro">
              <Button type="default" size="large" block>
                Criar Nova Conta
              </Button>
            </Link>
          </div>

          {/* Informações de suporte */}
          <div style={{
            marginTop: '32px',
            padding: '16px',
            background: '#f6f8fa',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '8px' }}>
              <QuestionCircleOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
              <span style={{ fontWeight: 'bold', color: '#1890ff' }}>Precisa de ajuda?</span>
            </div>
            <Paragraph style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              Entre em contato conosco através do e-mail:{' '}
              <a href="mailto:suporte@cadastrocultural.am.gov.br">
                suporte@cadastrocultural.am.gov.br
              </a>
            </Paragraph>
          </div>
        </Card>
      </motion.div>
    </div>
  );
};

export default Login;
