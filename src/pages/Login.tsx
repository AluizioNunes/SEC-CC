import React, { useState } from 'react';
import { Form, Input, Button, Typography, Alert, Row, Col, Divider } from 'antd';
import {
  UserOutlined,
  LockOutlined,
  LoginOutlined,
  EyeInvisibleOutlined,
  EyeOutlined,
  QuestionCircleOutlined,
  BugOutlined,
  GoogleOutlined,
  MailOutlined,
  LinkedinOutlined,
  InstagramOutlined,
  ArrowRightOutlined
} from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useI18n } from '../i18n/I18nContext';
import SECGovLogo from '../Images/SEC_GOV-LogoOficial.png';

const { Title, Paragraph, Text } = Typography;

interface LoginFormValues {
  usuario: string;
  password: string;
  remember: boolean;
}

const Login: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login, loginGuest } = useAuth();
  const navigate = useNavigate();
  const { t } = useI18n();

  const routeAfterLogin = () => {
    try {
      const raw = localStorage.getItem('sec-user');
      const parsed = raw ? JSON.parse(raw) : null;
      const profile = (parsed?.profile ?? 'user') as string;
      if (profile === 'admin') {
        navigate('/admin');
      } else if (profile === 'colaborador') {
        navigate('/home');
      } else if (profile === 'artista') {
        navigate('/dashboard');
      } else if (profile === 'visitante') {
        navigate('/eventos');
      } else {
        // Perfil default (user) vai para /home
        navigate('/home');
      }
    } catch {
      navigate('/home');
    }
  };

  const handleDeveloperLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      const success = await login('admin', 'changeme123');
      if (success) {
        routeAfterLogin();
      } else {
        setError('Erro no login de desenvolvedor.');
      }
    } catch (err) {
      setError('Erro interno do servidor. Tente novamente em alguns minutos.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values: LoginFormValues) => {
    setLoading(true);
    setError(null);

    try {
      const success = await login(values.usuario, values.password);
      if (success) {
        routeAfterLogin();
      } else {
        setError('Credenciais inválidas. Verifique seu usuário/e-mail e senha.');
      }
    } catch (err) {
      setError('Erro interno do servidor. Tente novamente em alguns minutos.');
    } finally {
      setLoading(false);
    }
  };

  const handleGuestLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const success = await loginGuest();
      if (success) {
        navigate('/eventos'); // encaminhar visitante para conteúdo público
      } else {
        setError('Não foi possível entrar como visitante.');
      }
    } catch (err) {
      setError('Erro interno do servidor. Tente novamente em alguns minutos.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f6f8fa' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', padding: '16px' }}>
        <img src={SECGovLogo} alt="SEC Amazonas" style={{ height: '56px' }} />
        <Title level={4} style={{ marginTop: '12px', marginBottom: '6px' }}>SEC - Cadastro Cultural</Title>
        <Text type="secondary" style={{ fontSize: '12px' }}>Acesso seguro à plataforma</Text>
      </div>

      {/* Conteúdo */}
      <div style={{ maxWidth: 980, margin: '0 auto', padding: '16px' }}>
        <Row gutter={24}>
          {/* Coluna de login */}
          <Col xs={24} md={14}>
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              style={{ background: '#fff', borderRadius: '0', padding: '16px', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}
            >
              <Title level={5} style={{ marginBottom: '12px' }}>Entrar</Title>
              <Paragraph type="secondary" style={{ marginBottom: '16px', fontSize: '13px' }}>
                Insira suas credenciais para acessar o sistema.
              </Paragraph>

              <Form
                form={form}
                layout="vertical"
                onFinish={handleSubmit}
                initialValues={{ remember: true }}
              >
                {error && (
                  <Alert
                    message={error}
                    type="error"
                    showIcon
                    style={{ marginBottom: '16px', fontSize: '12px' }}
                  />
                )}

                <Form.Item
                  label="Usuário ou E-mail"
                  name="usuario"
                  rules={[
                    { required: true, message: 'Por favor, digite seu usuário ou e-mail!' },
                    {
                      validator: (_, value) => {
                        if (!value || typeof value !== 'string') {
                          return Promise.reject(new Error('Por favor, digite seu usuário ou e-mail!'));
                        }
                        const isEmail = /\S+@\S+\.\S+/.test(value);
                        const isUsername = /^[a-zA-Z0-9_.-]{3,}$/.test(value);
                        return isEmail || isUsername
                          ? Promise.resolve()
                          : Promise.reject(new Error('Digite um e-mail válido ou um usuário (mín. 3 caracteres).'));
                      }
                    }
                  ]}
                >
                  <Input
                    prefix={<UserOutlined />}
                    placeholder="usuario ou email"
                    size="large"
                    autoComplete="username"
                    style={{ borderRadius: '0', height: '36px' }}
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
                    style={{ borderRadius: '0', height: '36px' }}
                  />
                </Form.Item>

                <Row justify="space-between" align="middle" style={{ marginBottom: '16px' }}>
                  <Col>
                    <Form.Item name="remember" valuePropName="checked" noStyle>
                      <label style={{ cursor: 'pointer', fontSize: '12px' }}>
                        <input type="checkbox" style={{ marginRight: '6px' }} />
                        Lembrar de mim
                      </label>
                    </Form.Item>
                  </Col>
                  <Col>
                    <Link to="/esqueci-senha" style={{ color: '#1890ff', fontSize: '12px' }}>
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
                    style={{
                      height: '40px',
                      borderRadius: '0',
                      background: '#1890ff',
                      border: 'none',
                      fontSize: '14px'
                    }}
                  >
                    {loading ? 'Entrando...' : 'Entrar'}
                  </Button>
                </Form.Item>
              </Form>

              {/* Diagnóstico e suporte */}
              <Divider style={{ margin: '16px 0' }} />
              <Row gutter={12}>
                <Col span={8}>
                  <Button
                    onClick={handleDeveloperLogin}
                    icon={<BugOutlined />}
                    block
                    style={{
                      height: '40px',
                      borderRadius: '0',
                      fontSize: '13px'
                    }}
                  >
                    Login de Dev
                  </Button>
                </Col>
                <Col span={8}>
                  <Button
                    onClick={handleGuestLogin}
                    icon={<ArrowRightOutlined />}
                    block
                    style={{ height: '40px', borderRadius: '0', fontSize: '13px' }}
                  >
                    Login como Visitante
                  </Button>
                </Col>
                <Col span={8}>
                  <Button
                    block
                    icon={<QuestionCircleOutlined />}
                    style={{ height: '40px', borderRadius: '0', fontSize: '13px' }}
                  >
                    Precisa de ajuda?
                  </Button>
                </Col>
              </Row>
            </motion.div>
          </Col>

          {/* Coluna lateral */}
          <Col xs={24} md={10}>
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              style={{ background: '#fff', borderRadius: '0', padding: '16px', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}
            >
              <Title level={5} style={{ marginBottom: '12px' }}>Acesso Rápido</Title>
              <Paragraph type="secondary" style={{ marginBottom: '16px', fontSize: '13px' }}>
                Use um dos provedores abaixo para entrar rapidamente.
              </Paragraph>

              <Row gutter={12}>
                <Col span={6}>
                  <Button
                    size="large"
                    block
                    icon={<GoogleOutlined />}
                    style={{
                      borderRadius: '50%',
                      border: '1px solid #d9d9d9',
                      height: '40px',
                      width: '40px',
                      padding: 0
                    }}
                  />
                </Col>
                <Col span={6}>
                  <Button
                    size="large"
                    block
                    icon={<MailOutlined />}
                    style={{
                      borderRadius: '50%',
                      border: '1px solid #d9d9d9',
                      height: '40px',
                      width: '40px',
                      padding: 0
                    }}
                  />
                </Col>
                <Col span={6}>
                  <Button
                    size="large"
                    block
                    icon={<LinkedinOutlined />}
                    style={{
                      borderRadius: '50%',
                      border: '1px solid #d9d9d9',
                      height: '40px',
                      width: '40px',
                      padding: 0
                    }}
                  />
                </Col>
                <Col span={6}>
                  <Button
                    size="large"
                    block
                    icon={<InstagramOutlined />}
                    style={{
                      borderRadius: '50%',
                      border: '1px solid #d9d9d9',
                      height: '40px',
                      width: '40px',
                      padding: 0
                    }}
                  />
                </Col>
              </Row>

              <Divider style={{ margin: '16px 0' }} />

              {/* CTA */}
              <div>
                <Paragraph style={{ color: '#666', marginBottom: '12px', fontSize: '13px' }}>
                  Ainda não tem cadastro?
                </Paragraph>
                <Link to="/Cadastros">
                  <Button
                    type="default"
                    size="large"
                    block
                    icon={<ArrowRightOutlined />}
                    style={{
                      borderRadius: '0',
                      height: '40px',
                      fontSize: '14px'
                    }}
                  >
                    Criar Nova Conta
                  </Button>
                </Link>
              </div>

              {/* Informações de suporte */}
              <div style={{
                marginTop: '24px',
                padding: '12px',
                background: '#f6f8fa',
                borderRadius: '0',
                textAlign: 'center'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '6px' }}>
                  <QuestionCircleOutlined style={{ marginRight: '6px', color: '#1890ff', fontSize: '14px' }} />
                  <Text strong style={{ color: '#1890ff', fontSize: '12px' }}>Precisa de ajuda?</Text>
                </div>
                <Paragraph style={{ margin: 0, fontSize: '11px', color: '#666' }}>
                  Entre em contato conosco através do e-mail:{' '}
                  <a href="mailto:suporte@cadastrocultural.am.gov.br" style={{ fontSize: '11px' }}>
                    suporte@cadastrocultural.am.gov.br
                  </a>
                </Paragraph>
              </div>

              {/* Referência Legal e LGPD */}
              <div style={{ textAlign: 'center', marginTop: '12px' }}>
                <Paragraph style={{ color: '#888', fontSize: '11px', marginBottom: '4px' }}>
                  Plataforma construída com base na Lei Estadual nº 6.306, de 19 de julho de 2023 — Cadastro Estadual,
                  respeitando as melhores práticas da LGPD.
                </Paragraph>
                <Text type="secondary" style={{ fontSize: '10px' }}>
                  Referência: d:\PROJETOS\SEC\src\databases\LEI N.º 6.306, DE 19 DE JULHO DE 2023 - CADASTRO ESTADUAL.pdf
                </Text>
              </div>
            </motion.div>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default Login;
