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
import Navbar from '../layout/Navbar';

const { Title, Paragraph } = Typography;

const Cadastro: React.FC = () => {
  return (
    <>
      {/* Navbar */}
      <Navbar />

      {/* Conteúdo Principal */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          padding: '24px',
          maxWidth: '100%',
          margin: '0 auto',
          background: '#fff',
          minHeight: 'calc(100vh - 140px)'
        }}
      >
        {/* Cabeçalho */}
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <Title level={1} style={{ color: '#1890ff', marginBottom: '16px' }}>
            Cadastre-se no Sistema
          </Title>
          <Paragraph style={{ fontSize: '16px', color: '#666', maxWidth: '600px', margin: '0 auto' }}>
            Escolha o tipo de cadastro que deseja realizar no Sistema Estadual de Cultura do Amazonas
          </Paragraph>
        </div>

        {/* Cards de Opções de Cadastro */}
        <Row gutter={[24, 24]} style={{ marginBottom: '40px' }}>
          {/* Pessoa Física */}
          <Col xs={24} lg={12}>
            <Card
              hoverable
              style={{
                textAlign: 'center',
                height: '100%',
                border: '2px solid #1890ff',
                borderRadius: '12px',
                transition: 'all 0.3s ease'
              }}
              bodyStyle={{ padding: '32px 24px' }}
            >
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #1890ff, #40a9ff)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 24px',
                fontSize: '32px',
                color: 'white'
              }}>
                <UserOutlined />
              </div>

              <Title level={3} style={{ color: '#1890ff', marginBottom: '16px' }}>
                Pessoa Física
              </Title>

              <Paragraph style={{ fontSize: '14px', color: '#666', marginBottom: '24px' }}>
                Para trabalhadores da cultura, artistas, produtores e demais profissionais
                individuais que atuam no setor cultural do Amazonas.
              </Paragraph>

              <Space direction="vertical" style={{ width: '100%' }}>
                <div style={{ fontSize: '12px', color: '#999', marginBottom: '16px' }}>
                  <strong>Documentos necessários:</strong><br />
                  • CPF<br />
                  • Comprovante de residência<br />
                  • Portfólio/artístico
                </div>

                <Link to="/cadastro-pf">
                  <Button
                    type="primary"
                    size="large"
                    block
                    icon={<ArrowRightOutlined />}
                    style={{
                      background: 'linear-gradient(135deg, #1890ff, #40a9ff)',
                      border: 'none',
                      height: '48px',
                      fontSize: '16px'
                    }}
                  >
                    Cadastrar como Pessoa Física
                  </Button>
                </Link>
              </Space>
            </Card>
          </Col>

          {/* Pessoa Jurídica */}
          <Col xs={24} lg={12}>
            <Card
              hoverable
              style={{
                textAlign: 'center',
                height: '100%',
                border: '2px solid #52c41a',
                borderRadius: '12px',
                transition: 'all 0.3s ease'
              }}
              bodyStyle={{ padding: '32px 24px' }}
            >
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #52c41a, #73d13d)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 24px',
                fontSize: '32px',
                color: 'white'
              }}>
                <TeamOutlined />
              </div>

              <Title level={3} style={{ color: '#52c41a', marginBottom: '16px' }}>
                Pessoa Jurídica
              </Title>

              <Paragraph style={{ fontSize: '14px', color: '#666', marginBottom: '24px' }}>
                Para espaços culturais, empresas, organizações, coletivos e instituições
                que desenvolvem atividades culturais no estado.
              </Paragraph>

              <Space direction="vertical" style={{ width: '100%' }}>
                <div style={{ fontSize: '12px', color: '#999', marginBottom: '16px' }}>
                  <strong>Documentos necessários:</strong><br />
                  • CNPJ<br />
                  • Alvará de funcionamento<br />
                  • Comprovante de endereço<br />
                  • Estatuto/contrato social
                </div>

                <Link to="/cadastro-pj">
                  <Button
                    type="primary"
                    size="large"
                    block
                    icon={<ArrowRightOutlined />}
                    style={{
                      background: 'linear-gradient(135deg, #52c41a, #73d13d)',
                      border: 'none',
                      height: '48px',
                      fontSize: '16px'
                    }}
                  >
                    Cadastrar como Pessoa Jurídica
                  </Button>
                </Link>
              </Space>
            </Card>
          </Col>
        </Row>

        {/* Informações Adicionais */}
        <Card
          style={{
            background: 'linear-gradient(135deg, #f0f2f5 0%, #e6f7ff 100%)',
            border: '1px solid #d9d9d9'
          }}
        >
          <Row gutter={[24, 24]}>
            <Col xs={24} lg={16}>
              <div>
                <Title level={4} style={{ color: '#1890ff', marginBottom: '16px' }}>
                  Sobre o Processo de Cadastro
                </Title>
                <Paragraph style={{ fontSize: '14px', marginBottom: '12px' }}>
                  <strong>1. Escolha o tipo de cadastro</strong> - Pessoa Física ou Pessoa Jurídica
                </Paragraph>
                <Paragraph style={{ fontSize: '14px', marginBottom: '12px' }}>
                  <strong>2. Preencha os dados obrigatórios</strong> - Informações pessoais e documentos
                </Paragraph>
                <Paragraph style={{ fontSize: '14px', marginBottom: '12px' }}>
                  <strong>3. Análise da documentação</strong> - Nossa equipe irá analisar sua solicitação
                </Paragraph>
                <Paragraph style={{ fontSize: '14px', marginBottom: '12px' }}>
                  <strong>4. Homologação</strong> - Após aprovação, você terá acesso completo ao sistema
                </Paragraph>
              </div>
            </Col>

            <Col xs={24} lg={8}>
              <div style={{ textAlign: 'center' }}>
                <CheckCircleOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '16px' }} />
                <Title level={4} style={{ color: '#52c41a', marginBottom: '16px' }}>
                  Processo Seguro
                </Title>
                <Paragraph style={{ fontSize: '12px', color: '#666' }}>
                  Seus dados são protegidos conforme a Lei Geral de Proteção de Dados (LGPD)
                </Paragraph>
              </div>
            </Col>
          </Row>
        </Card>
      </motion.div>
    </>
  );
};

export default Cadastro;
