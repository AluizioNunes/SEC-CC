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
  email: string;
  password: string;
  remember: boolean;
}

const Login: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();
  const { t } = useI18n();

  const handleDeveloperLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      const success = await login('admin@sec.am.gov.br', 'admin123');
      if (success) {
        navigate('/dashboard');
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

  // Array de imagens culturais do Amazonas
  const culturalImages = [
    'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=600&h=800&fit=crop&crop=center',
    'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=800&fit=crop&crop=center',
    'https://images.unsplash.com/photo-1533460004989-cef01064af7e?w=600&h=800&fit=crop&crop=center',
    'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=600&h=800&fit=crop&crop=center',
  ];

  const currentImage = React.useMemo(() => culturalImages[Math.floor(Math.random() * culturalImages.length)], []);

  return (
    <div style={{
      minHeight: '100vh',
      background: '#fff',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '10px',
      width: '100%',
      overflowX: 'hidden'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '100%',
        height: '100vh',
        background: '#fff',
        display: 'flex',
        overflow: 'hidden'
      }}>
        <Row style={{ height: '100%', width: '100%' }}>
          {/* Lado Esquerdo - Imagem Cultural (65%) */}
          <Col xs={0} lg={15} xl={16} style={{
            backgroundImage: `url(${currentImage})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            minHeight: '100vh'
          }}>
            <div style={{
              textAlign: 'center',
              color: 'white',
              zIndex: 2,
              padding: '30px',
              maxWidth: '90%'
            }}>
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
              >
                <div style={{
                  fontSize: '50px',
                  marginBottom: '12px',
                  opacity: 0.9
                }}>
                  🎭
                </div>
                <Title level={4} style={{
                  color: 'white',
                  marginBottom: '8px',
                  textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
                  fontSize: '16px'
                }}>
-                 Cultura Amazonense
+                 {t('hero.title')}
                </Title>
                <Paragraph style={{
                  color: 'rgba(255,255,255,0.9)',
                  fontSize: '12px',
                  lineHeight: 1.3,
                  maxWidth: '200px',
                  margin: '0 auto'
                }}>
-                 Conecte-se ao Sistema Estadual de Cultura
+                 {t('hero.subtitle')}
                </Paragraph>
              </motion.div>
            </div>

            {/* Sobreposição gradiente */}
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'linear-gradient(135deg, rgba(30,60,114,0.4) 0%, rgba(42,82,152,0.2) 100%)',
              zIndex: 1
            }} />
          </Col>

          {/* Lado Direito - Formulário de Login (35%) */}
          <Col xs={24} lg={9} xl={8} style={{
            padding: '30px 20px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            background: '#fff',
            overflowY: 'auto',
            overflowX: 'hidden'
          }}>
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              {/* Cabeçalho com logo */}
              <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                <img
                  src={SECGovLogo}
                  alt="Logo SEC"
                  style={{ width: 'auto', height: '108px', objectFit: 'contain' }}
                />
                <Paragraph style={{ color: '#666', marginTop: '8px', fontSize: '13px' }}>
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
                    style={{ marginBottom: '16px', fontSize: '12px' }}
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

              <Divider style={{ margin: '20px 0' }}>
                <Text type="secondary">ou continue com</Text>
              </Divider>

              {/* Integrações Sociais - Apenas ícones */}
              <div style={{ marginBottom: '20px' }}>
                <Row gutter={[8, 8]}>
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
              </div>

              <Divider style={{ margin: '20px 0' }} />

              {/* Botão para desenvolvedor - Ícone pequeno */}
              <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                <Button
                  type="dashed"
                  icon={<BugOutlined />}
                  onClick={handleDeveloperLogin}
                  loading={loading}
                  size="large"
                  style={{
                    borderRadius: '0',
                    borderColor: '#1890ff',
                    color: '#1890ff',
                    backgroundColor: 'rgba(24, 144, 255, 0.05)',
                    height: '40px',
                    fontSize: '13px'
                  }}
                >
                  Desenvolvedor
                </Button>
              </div>

              <Divider style={{ margin: '20px 0' }} />

              {/* Links adicionais */}
              <div style={{ textAlign: 'center' }}>
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
