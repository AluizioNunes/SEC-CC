import React from 'react';
import { Button, Typography, Layout, Card, Row, Col } from 'antd';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { UserOutlined, ShopOutlined, DashboardOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { Content } = Layout;

const HomePage: React.FC = () => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Content style={{ padding: '50px' }}>
        <motion.div
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          <div style={{ textAlign: 'center', marginBottom: '50px' }}>
            <Title level={1}>SEC - Cadastro Cultural</Title>
            <Paragraph>
              Sistema de Cadastro Estadual de Cultura do Amazonas, conforme Lei N.º 6.306/2023
            </Paragraph>
          </div>
          
          <Row gutter={[16, 16]} justify="center">
            <Col xs={24} sm={12} md={8}>
              <motion.div whileHover={{ scale: 1.05 }}>
                <Card
                  hoverable
                  style={{ height: '100%' }}
                  actions={[
                    <Link to="/register">
                      <Button type="primary" icon={<UserOutlined />}>
                        Cadastrar como Pessoa Física
                      </Button>
                    </Link>
                  ]}
                >
                  <Card.Meta
                    title="Pessoa Física"
                    description="Trabalhadores e Trabalhadoras da Cultura"
                  />
                </Card>
              </motion.div>
            </Col>
            
            <Col xs={24} sm={12} md={8}>
              <motion.div whileHover={{ scale: 1.05 }}>
                <Card
                  hoverable
                  style={{ height: '100%' }}
                  actions={[
                    <Link to="/register">
                      <Button type="primary" icon={<ShopOutlined />}>
                        Cadastrar como Pessoa Jurídica
                      </Button>
                    </Link>
                  ]}
                >
                  <Card.Meta
                    title="Pessoa Jurídica"
                    description="Espaços Culturais e Entidades"
                  />
                </Card>
              </motion.div>
            </Col>
            
            <Col xs={24} sm={12} md={8}>
              <motion.div whileHover={{ scale: 1.05 }}>
                <Card
                  hoverable
                  style={{ height: '100%' }}
                  actions={[
                    <Link to="/login">
                      <Button icon={<DashboardOutlined />}>
                        Área Administrativa
                      </Button>
                    </Link>
                  ]}
                >
                  <Card.Meta
                    title="Administração"
                    description="Acesso para Comissão de Análise"
                  />
                </Card>
              </motion.div>
            </Col>
          </Row>
        </motion.div>
      </Content>
    </Layout>
  );
};

export default HomePage;
