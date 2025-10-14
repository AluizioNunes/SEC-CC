import React from 'react';
import { Card, Typography, Row, Col, Button, Space } from 'antd';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FileTextOutlined,
  DownloadOutlined,
  InfoCircleOutlined,
  SafetyOutlined
} from '@ant-design/icons';

const { Title, Paragraph } = Typography;

const Sobre: React.FC = () => {
  return (
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
      <Card style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <Title level={2} style={{ color: '#1890ff' }}>
            Sobre o Sistema de Cadastro Cultural
          </Title>
          <Paragraph style={{ fontSize: '16px', color: '#666' }}>
            Informações detalhadas sobre o SEC - Sistema Estadual de Cultura do Amazonas
          </Paragraph>
        </div>

        {/* Sobre o Sistema */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card
            title={
              <span>
                <InfoCircleOutlined style={{ marginRight: '8px' }} />
                Sobre o Sistema SEC
              </span>
            }
            style={{ marginBottom: '24px' }}
          >
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={16}>
                <div>
                  <Title level={4} style={{ marginBottom: '16px' }}>
                    Sobre o Sistema SEC
                  </Title>
                  <Paragraph>
                    O Sistema de Cadastro Estadual de Cultura (SEC) é uma plataforma desenvolvida
                    para facilitar o cadastro e gestão de trabalhadores da cultura e espaços culturais
                    no Estado do Amazonas, conforme estabelecido pela Lei nº 6.306/2023.
                  </Paragraph>
                  <Paragraph>
                    Nossa missão é promover a cultura amazonense através de um sistema transparente,
                    eficiente e acessível a todos os cidadãos que contribuem para o desenvolvimento
                    cultural do nosso estado.
                  </Paragraph>
                </div>
              </Col>

              <Col xs={24} lg={8}>
                <div style={{ textAlign: 'center' }}>
                  <Title level={4} style={{ marginBottom: '16px' }}>
                    Links Importantes
                  </Title>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Link to="/">
                      <Button type="link" icon={<InfoCircleOutlined />}>
                        Página Inicial
                      </Button>
                    </Link>
                    <Link to="/contato">
                      <Button type="link" icon={<SafetyOutlined />}>
                        Fale Conosco
                      </Button>
                    </Link>
                  </Space>
                </div>
              </Col>
            </Row>
          </Card>
        </motion.div>

        {/* Sobre a Lei do Cadastro Cultural */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card
            title={
              <span>
                <FileTextOutlined style={{ marginRight: '8px' }} />
                Sobre a Lei do Cadastro Cultural
              </span>
            }
          >
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={16}>
                <div>
                  <Title level={4} style={{ marginBottom: '16px' }}>
                    Lei Nº 6.306, de 19 de julho de 2023
                  </Title>
                  <Paragraph>
                    Institui o Sistema Estadual de Cultura (SEC) do Amazonas e estabelece diretrizes
                    para o cadastro de trabalhadores da cultura, espaços culturais e organizações
                    culturais no âmbito do Estado do Amazonas.
                  </Paragraph>
                  <Paragraph>
                    <strong>Objetivos principais:</strong>
                  </Paragraph>
                  <ul style={{ paddingLeft: '20px' }}>
                    <li>Promover o mapeamento e reconhecimento dos trabalhadores da cultura</li>
                    <li>Facilitar o acesso a políticas públicas culturais</li>
                    <li>Fomentar a economia criativa no estado</li>
                    <li>Garantir transparência nos processos de cadastro e homologação</li>
                  </ul>
                </div>
              </Col>

              <Col xs={24} lg={8}>
                <div style={{ textAlign: 'center' }}>
                  <Title level={4} style={{ marginBottom: '16px' }}>
                    Documentação
                  </Title>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Button
                      type="primary"
                      icon={<DownloadOutlined />}
                      block
                      href="/databases/LEI N.º 6.306, DE 19 DE JULHO DE 2023 - CADASTRO ESTADUAL.pdf"
                      target="_blank"
                    >
                      Ver Lei Completa
                    </Button>
                    <Button
                      type="default"
                      icon={<FileTextOutlined />}
                      block
                    >
                      Manual do Cadastro
                    </Button>
                  </Space>
                </div>
              </Col>
            </Row>
          </Card>
        </motion.div>

        {/* Navegação */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          style={{ textAlign: 'center', marginTop: '32px' }}
        >
          <Space>
            <Link to="/">
              <Button type="primary">Voltar ao Início</Button>
            </Link>
            <Link to="/login">
              <Button>Acessar Sistema</Button>
            </Link>
          </Space>
        </motion.div>
      </Card>
    </motion.div>
  );
};

export default Sobre;
