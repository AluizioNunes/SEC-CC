import React, { useState } from 'react';
import {
  Row,
  Col,
  Card,
  Button,
  Typography,
  Space,
  Divider,
  Tag,
  Alert,
  Collapse,
  List,
  Avatar,
  Badge
} from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  ArrowRightOutlined,
  FileTextOutlined,
  SafetyOutlined,
  TrophyOutlined,
  BookOutlined,
  DollarOutlined,
  GlobalOutlined,
  CrownOutlined,
  HeartOutlined,
  StarOutlined
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import CadastroPFModal from '../components/CadastroPFModal';

const { Title, Paragraph, Text } = Typography;
const { Panel } = Collapse;

const Cadastros: React.FC = () => {
  const [activeCard, setActiveCard] = useState<string | null>(null);
  const [pfModalOpen, setPfModalOpen] = useState<boolean>(false);
  const openPFModal = () => setPfModalOpen(true);
  const closePFModal = () => setPfModalOpen(false);

  const beneficiosPessoaFisica = [
    'Acesso a editais e chamadas públicas de cultura',
    'Participação em programas de capacitação',
    'Certificação profissional reconhecida pelo Estado',
    'Acesso a espaços públicos para apresentações',
    'Inclusão no mapeamento cultural do Amazonas',
    'Prioridade em eventos e festivais oficiais'
  ];

  const beneficiosPessoaJuridica = [
    'Habilitação para receber recursos públicos',
    'Participação em licitações culturais',
    'Certificação como espaço/equipamento cultural',
    'Acesso a linhas de crédito específicas',
    'Inclusão na rede de equipamentos culturais',
    'Prioridade em parcerias público-privadas'
  ];

  const requisitosPessoaFisica = [
    {
      titulo: 'Documentação Básica',
      itens: ['CPF ativo', 'Comprovante de residência no Amazonas', 'Documento de identidade com foto']
    },
    {
      titulo: 'Comprovação de Atividade Cultural',
      itens: ['Portfólio artístico ou curricular', 'Certificados de cursos/workshops', 'Comprovantes de participação em eventos culturais']
    },
    {
      titulo: 'Documentação Complementar',
      itens: ['Comprovante de renda (para programas sociais)', 'Declaração de não possuir débitos com o Estado']
    }
  ];

  const requisitosPessoaJuridica = [
    {
      titulo: 'Documentação Legal',
      itens: ['CNPJ ativo', 'Contrato social ou estatuto', 'Alvará de funcionamento']
    },
    {
      titulo: 'Comprovação de Atividade Cultural',
      itens: ['Plano de trabalho cultural', 'Comprovantes de eventos realizados', 'Certificações ou registros profissionais']
    },
    {
      titulo: 'Documentação Fiscal',
      itens: ['Certidão negativa de débitos estaduais', 'Comprovante de endereço comercial', 'Cadastro no SICAF (quando aplicável)']
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={{
        padding: '24px',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f0f2f5 0%, #e6f7ff 100%)'
      }}
    >

      {/* Cards de Opções de Cadastro */}
      <Row gutter={[32, 32]} style={{ marginBottom: '48px' }}>
        {/* Pessoa Física */}
        <Col xs={24} lg={12}>
          <motion.div
            whileHover={{ y: -8 }}
            onHoverStart={() => setActiveCard('pf')}
            onHoverEnd={() => setActiveCard(null)}
          >
            <Card
              hoverable
              style={{
                textAlign: 'center',
                minHeight: '600px',
                border: activeCard === 'pf' ? '3px solid #1890ff' : '2px solid #1890ff',
                borderRadius: '16px',
                transition: 'all 0.3s ease',
                background: activeCard === 'pf'
                  ? 'linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%)'
                  : 'white',
                boxShadow: activeCard === 'pf'
                  ? '0 20px 40px rgba(24, 144, 255, 0.3)'
                  : '0 8px 24px rgba(0, 0, 0, 0.1)'
              }}
              bodyStyle={{ padding: '32px 24px' }}
            >
              <div style={{
                width: '100px',
                height: '100px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #1890ff, #40a9ff)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 24px',
                fontSize: '40px',
                color: 'white',
                boxShadow: '0 8px 24px rgba(24, 144, 255, 0.3)'
              }}>
                <UserOutlined />
              </div>

              <div style={{ marginBottom: '24px' }}>
                <Badge.Ribbon text="Individual" color="blue">
                  <Title level={2} style={{ color: '#1890ff', marginBottom: '8px' }}>
                    Pessoa Física
                  </Title>
                </Badge.Ribbon>
                <Tag color="blue" style={{ fontSize: '14px', padding: '4px 12px' }}>
                  Trabalhadores da Cultura
                </Tag>
              </div>

              <Paragraph style={{
                fontSize: '16px',
                color: '#555',
                marginBottom: '24px',
                lineHeight: 1.6
              }}>
                Destinado a <strong>artistas, produtores culturais, técnicos, professores de arte</strong>
                e demais profissionais individuais que atuam no setor cultural do Amazonas.
              </Paragraph>

              {/* Benefícios */}
              <div style={{ marginBottom: '24px' }}>
                <Title level={5} style={{ color: '#52c41a', marginBottom: '16px' }}>
                  <TrophyOutlined /> Benefícios
                </Title>
                <div style={{ textAlign: 'left' }}>
                  {beneficiosPessoaFisica.slice(0, 3).map((beneficio, index) => (
                    <div key={index} style={{
                      display: 'flex',
                      alignItems: 'center',
                      marginBottom: '8px',
                      padding: '8px',
                      background: '#f6ffed',
                      borderRadius: '6px'
                    }}>
                      <CheckCircleOutlined style={{ color: '#52c41a', marginRight: '8px' }} />
                      <Text style={{ fontSize: '13px' }}>{beneficio}</Text>
                    </div>
                  ))}
                </div>
              </div>

              {/* Requisitos */}
              <div style={{ marginBottom: '24px' }}>
                <Title level={5} style={{ color: '#faad14', marginBottom: '16px' }}>
                  <FileTextOutlined /> Principais Requisitos
                </Title>
                <div style={{ textAlign: 'left' }}>
                  {requisitosPessoaFisica.slice(0, 2).map((categoria, index) => (
                    <div key={index} style={{ marginBottom: '12px' }}>
                      <Text strong style={{ fontSize: '13px', color: '#faad14' }}>
                        {categoria.titulo}:
                      </Text>
                      <div style={{ marginLeft: '16px', marginTop: '4px' }}>
                        {categoria.itens.slice(0, 2).map((item, itemIndex) => (
                          <div key={itemIndex} style={{
                            display: 'flex',
                            alignItems: 'center',
                            marginBottom: '4px'
                          }}>
                            <div style={{
                              width: '4px',
                              height: '4px',
                              background: '#faad14',
                              borderRadius: '50%',
                              marginRight: '8px'
                            }} />
                            <Text style={{ fontSize: '12px', color: '#666' }}>{item}</Text>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <Button
                type="primary"
                size="large"
                block
                icon={<ArrowRightOutlined />}
                onClick={openPFModal}
                style={{
                  background: 'linear-gradient(135deg, #1890ff, #40a9ff)',
                  border: 'none',
                  height: '52px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  borderRadius: '8px'
                }}
              >
                Cadastrar como Pessoa Física
              </Button>
              
            </Card>
          </motion.div>
        </Col>

        {/* Pessoa Jurídica */}
        <Col xs={24} lg={12}>
          <motion.div
            whileHover={{ y: -8 }}
            onHoverStart={() => setActiveCard('pj')}
            onHoverEnd={() => setActiveCard(null)}
          >
            <Card
              hoverable
              style={{
                textAlign: 'center',
                minHeight: '600px',
                border: activeCard === 'pj' ? '3px solid #52c41a' : '2px solid #52c41a',
                borderRadius: '16px',
                transition: 'all 0.3s ease',
                background: activeCard === 'pj'
                  ? 'linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%)'
                  : 'white',
                boxShadow: activeCard === 'pj'
                  ? '0 20px 40px rgba(82, 196, 26, 0.3)'
                  : '0 8px 24px rgba(0, 0, 0, 0.1)'
              }}
              bodyStyle={{ padding: '32px 24px' }}
            >
              <div style={{
                width: '100px',
                height: '100px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #52c41a, #73d13d)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 24px',
                fontSize: '40px',
                color: 'white',
                boxShadow: '0 8px 24px rgba(82, 196, 26, 0.3)'
              }}>
                <TeamOutlined />
              </div>

              <div style={{ marginBottom: '24px' }}>
                <Badge.Ribbon text="Organizacional" color="green">
                  <Title level={2} style={{ color: '#52c41a', marginBottom: '8px' }}>
                    Pessoa Jurídica
                  </Title>
                </Badge.Ribbon>
                <Tag color="green" style={{ fontSize: '14px', padding: '4px 12px' }}>
                  Espaços e Organizações Culturais
                </Tag>
              </div>

              <Paragraph style={{
                fontSize: '16px',
                color: '#555',
                marginBottom: '24px',
                lineHeight: 1.6
              }}>
                Destinado a <strong>espaços culturais, empresas, organizações, coletivos, instituições</strong>
                e demais entidades que desenvolvem atividades culturais no estado do Amazonas.
              </Paragraph>

              {/* Benefícios */}
              <div style={{ marginBottom: '24px' }}>
                <Title level={5} style={{ color: '#52c41a', marginBottom: '16px' }}>
                  <TrophyOutlined /> Benefícios
                </Title>
                <div style={{ textAlign: 'left' }}>
                  {beneficiosPessoaJuridica.slice(0, 3).map((beneficio, index) => (
                    <div key={index} style={{
                      display: 'flex',
                      alignItems: 'center',
                      marginBottom: '8px',
                      padding: '8px',
                      background: '#f6ffed',
                      borderRadius: '6px'
                    }}>
                      <CheckCircleOutlined style={{ color: '#52c41a', marginRight: '8px' }} />
                      <Text style={{ fontSize: '13px' }}>{beneficio}</Text>
                    </div>
                  ))}
                </div>
              </div>

              {/* Requisitos */}
              <div style={{ marginBottom: '24px' }}>
                <Title level={5} style={{ color: '#faad14', marginBottom: '16px' }}>
                  <FileTextOutlined /> Principais Requisitos
                </Title>
                <div style={{ textAlign: 'left' }}>
                  {requisitosPessoaJuridica.slice(0, 2).map((categoria, index) => (
                    <div key={index} style={{ marginBottom: '12px' }}>
                      <Text strong style={{ fontSize: '13px', color: '#faad14' }}>
                        {categoria.titulo}:
                      </Text>
                      <div style={{ marginLeft: '16px', marginTop: '4px' }}>
                        {categoria.itens.slice(0, 2).map((item, itemIndex) => (
                          <div key={itemIndex} style={{
                            display: 'flex',
                            alignItems: 'center',
                            marginBottom: '4px'
                          }}>
                            <div style={{
                              width: '4px',
                              height: '4px',
                              background: '#faad14',
                              borderRadius: '50%',
                              marginRight: '8px'
                            }} />
                            <Text style={{ fontSize: '12px', color: '#666' }}>{item}</Text>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
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
                    height: '52px',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    borderRadius: '8px'
                  }}
                >
                  Cadastrar como Pessoa Jurídica
                </Button>
              </Link>
            </Card>
          </motion.div>
        </Col>
      </Row>
      <CadastroPFModal visible={pfModalOpen} pessoa={null} onClose={closePFModal} />
    </motion.div>
  );
}

export default Cadastros;
