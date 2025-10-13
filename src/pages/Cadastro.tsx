import React from 'react';
import { Row, Col, Card, Button, Typography, Space } from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  ArrowRightOutlined
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const { Title, Paragraph } = Typography;

const Cadastro: React.FC = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <div style={{
      padding: '24px',
      maxWidth: '100%',
      margin: '0 auto',
      background: '#fff',
      minHeight: 'calc(100vh - 140px)'
    }}>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Cabeçalho */}
        <motion.div
          variants={cardVariants}
          style={{ textAlign: 'center', marginBottom: '60px' }}
        >
          <Title level={1} style={{ color: '#1890ff', marginBottom: '16px' }}>
            Cadastre-se no Sistema
          </Title>
          <Paragraph style={{
            fontSize: '18px',
            color: '#666',
            maxWidth: '600px',
            margin: '0 auto'
          }}>
            Escolha o tipo de cadastro que melhor se adequa ao seu perfil.
            Cada categoria possui requisitos específicos conforme a Lei nº 6.306/2023.
          </Paragraph>
        </motion.div>

        {/* Cards de seleção */}
        <Row gutter={[32, 32]}>
          <Col xs={24} lg={12}>
            <motion.div variants={cardVariants}>
              <Card
                hoverable
                style={{
                  height: '100%',
                  border: '2px solid #f0f0f0',
                  transition: 'all 0.3s ease',
                }}
                bodyStyle={{
                  padding: '32px',
                  textAlign: 'center',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column'
                }}
              >
                <div style={{
                  fontSize: '64px',
                  color: '#1890ff',
                  marginBottom: '24px'
                }}>
                  <UserOutlined />
                </div>

                <Title level={2} style={{ color: '#1890ff', marginBottom: '16px' }}>
                  Pessoa Física
                </Title>

                <Paragraph style={{
                  fontSize: '16px',
                  lineHeight: 1.6,
                  flex: 1,
                  marginBottom: '24px'
                }}>
                  Para trabalhadores individuais da cultura, artistas, produtores,
                  técnicos e gestores culturais que atuam de forma independente.
                </Paragraph>

                <div style={{ marginBottom: '32px' }}>
                  <Title level={4} style={{ color: '#1890ff', marginBottom: '16px' }}>
                    Requisitos:
                  </Title>
                  <ul style={{
                    textAlign: 'left',
                    paddingLeft: '20px',
                    lineHeight: 2
                  }}>
                    <li>Residência no Amazonas</li>
                    <li>Comprovação de 2 anos de atuação</li>
                    <li>Documentação pessoal</li>
                    <li>Portfólio artístico</li>
                  </ul>
                </div>

                <div style={{ marginTop: 'auto' }}>
                  <Link to="/cadastro/pf">
                    <Button
                      type="primary"
                      size="large"
                      block
                      icon={<ArrowRightOutlined />}
                    >
                      Continuar Cadastro PF
                    </Button>
                  </Link>
                </div>
              </Card>
            </motion.div>
          </Col>

          <Col xs={24} lg={12}>
            <motion.div variants={cardVariants}>
              <Card
                hoverable
                style={{
                  height: '100%',
                  border: '2px solid #f0f0f0',
                  transition: 'all 0.3s ease',
                }}
                bodyStyle={{
                  padding: '32px',
                  textAlign: 'center',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column'
                }}
              >
                <div style={{
                  fontSize: '64px',
                  color: '#52c41a',
                  marginBottom: '24px'
                }}>
                  <TeamOutlined />
                </div>

                <Title level={2} style={{ color: '#52c41a', marginBottom: '16px' }}>
                  Pessoa Jurídica
                </Title>

                <Paragraph style={{
                  fontSize: '16px',
                  lineHeight: 1.6,
                  flex: 1,
                  marginBottom: '24px'
                }}>
                  Para espaços culturais, empresas, organizações e instituições
                  que desenvolvem atividades culturais no Amazonas.
                </Paragraph>

                <div style={{ marginBottom: '32px' }}>
                  <Title level={4} style={{ color: '#52c41a', marginBottom: '16px' }}>
                    Requisitos:
                  </Title>
                  <ul style={{
                    textAlign: 'left',
                    paddingLeft: '20px',
                    lineHeight: 2
                  }}>
                    <li>CNPJ ativo e regular</li>
                    <li>Estabelecimento no Amazonas</li>
                    <li>Documentação jurídica</li>
                    <li>Comprovação de espaço cultural</li>
                  </ul>
                </div>

                <div style={{ marginTop: 'auto' }}>
                  <Link to="/cadastro/pj">
                    <Button
                      type="primary"
                      size="large"
                      block
                      icon={<ArrowRightOutlined />}
                      style={{ background: '#52c41a', borderColor: '#52c41a' }}
                    >
                      Continuar Cadastro PJ
                    </Button>
                  </Link>
                </div>
              </Card>
            </motion.div>
          </Col>
        </Row>

        {/* Informações adicionais */}
        <motion.div variants={cardVariants}>
          <Card
            style={{
              marginTop: '40px',
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              color: 'white'
            }}
          >
            <Row gutter={[24, 24]} align="middle">
              <Col xs={24} lg={16}>
                <Title level={3} style={{ color: 'white', marginBottom: '16px' }}>
                  Documentação Necessária
                </Title>

                <Row gutter={[16, 16]}>
                  <Col xs={24} sm={12}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                      <CheckCircleOutlined style={{ marginRight: '8px', color: '#4ade80' }} />
                      <span>Documento oficial com foto</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                      <CheckCircleOutlined style={{ marginRight: '8px', color: '#4ade80' }} />
                      <span>Comprovante de residência</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                      <CheckCircleOutlined style={{ marginRight: '8px', color: '#4ade80' }} />
                      <span>Comprovantes de atuação cultural</span>
                    </div>
                  </Col>

                  <Col xs={24} sm={12}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                      <CheckCircleOutlined style={{ marginRight: '8px', color: '#4ade80' }} />
                      <span>Para PJ: CNPJ e estatuto social</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                      <CheckCircleOutlined style={{ marginRight: '8px', color: '#4ade80' }} />
                      <span>Para PJ: Documentos do representante</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                      <CheckCircleOutlined style={{ marginRight: '8px', color: '#4ade80' }} />
                      <span>Fotos e portfólio (se aplicável)</span>
                    </div>
                  </Col>
                </Row>
              </Col>

              <Col xs={24} lg={8}>
                <div style={{ textAlign: 'center' }}>
                  <Title level={4} style={{ color: 'white', marginBottom: '16px' }}>
                    Dúvidas?
                  </Title>
                  <Paragraph style={{ color: 'rgba(255,255,255,0.9)' }}>
                    Nossa equipe está pronta para ajudar você no processo de cadastro.
                  </Paragraph>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Link to="/sobre">
                      <Button type="link" style={{ color: 'white' }}>
                        Sobre o Cadastro
                      </Button>
                    </Link>
                    <Link to="/contato">
                      <Button type="link" style={{ color: 'white' }}>
                        Fale Conosco
                      </Button>
                    </Link>
                  </Space>
                </div>
              </Col>
            </Row>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Cadastro;
