import React from 'react';
import { Layout, Row, Col, Divider, Space } from 'antd';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FacebookOutlined,
  TwitterOutlined,
  InstagramOutlined,
  YoutubeOutlined,
  PhoneOutlined,
  MailOutlined,
  EnvironmentOutlined,
  CopyrightOutlined
} from '@ant-design/icons';

const { Footer: AntFooter } = Layout;

const Footer: React.FC = () => {
  return (
    <AntFooter style={{
      background: 'linear-gradient(135deg, #001529 0%, #000000 100%)',
      color: '#fff',
      padding: '20px 0 10px', // Reduzido pela metade (era 40px 0 20px)
    }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px' }}>
          <Row gutter={[24, 16]}> {/* Reduzido de 32, 32 para 24, 16 */}
            {/* Informações Institucionais */}
            <Col xs={24} lg={8}>
              <div>
                <div style={{
                  fontSize: '20px', // Reduzido de 24px
                  fontWeight: 'bold',
                  color: '#1890ff',
                  marginBottom: '12px' // Reduzido de 16px
                }}>
                  SEC - Cadastro Cultural
                </div>
                <p style={{
                  color: '#ccc',
                  lineHeight: 1.4, // Reduzido de 1.6
                  marginBottom: '12px' // Reduzido de 16px
                }}>
                  Sistema de Cadastro Estadual de Cultura do Amazonas,
                  conforme Lei nº 6.306/2023.
                </p>
                <p style={{
                  color: '#ccc',
                  lineHeight: 1.4, // Reduzido de 1.6
                  marginBottom: '12px' // Reduzido de 16px
                }}>
                  Promovendo a cultura amazonense através de um sistema
                  transparente e acessível a todos os cidadãos.
                </p>
              </div>
            </Col>

            {/* Links Rápidos */}
            <Col xs={24} lg={8}>
              <div>
                <h4 style={{
                  color: '#1890ff',
                  marginBottom: '12px', // Reduzido de 16px
                  fontSize: '14px' // Reduzido de 16px
                }}>
                  Links Rápidos
                </h4>
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  <Link to="/" style={{
                    color: '#ccc',
                    textDecoration: 'none',
                    display: 'block',
                    padding: '3px 0' // Reduzido de 4px 0
                  }}>
                    Página Inicial
                  </Link>
                  <Link to="/sobre" style={{
                    color: '#ccc',
                    textDecoration: 'none',
                    display: 'block',
                    padding: '3px 0'
                  }}>
                    Sobre o Cadastro
                  </Link>
                  <Link to="/resultados" style={{
                    color: '#ccc',
                    textDecoration: 'none',
                    display: 'block',
                    padding: '3px 0'
                  }}>
                    Resultados Oficiais
                  </Link>
                  <Link to="/contato" style={{
                    color: '#ccc',
                    textDecoration: 'none',
                    display: 'block',
                    padding: '3px 0'
                  }}>
                    Fale Conosco
                  </Link>
                </Space>
              </div>
            </Col>

            {/* Contato e Redes Sociais */}
            <Col xs={24} lg={8}>
              <div>
                <h4 style={{
                  color: '#1890ff',
                  marginBottom: '12px', // Reduzido de 16px
                  fontSize: '14px' // Reduzido de 16px
                }}>
                  Entre em Contato
                </h4>

                <div style={{ marginBottom: '12px' }}> {/* Reduzido de 16px */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    marginBottom: '6px', // Reduzido de 8px
                    color: '#ccc'
                  }}>
                    <EnvironmentOutlined style={{ marginRight: '8px' }} />
                    <span>Av. Eduardo Ribeiro, 901 - Centro, Manaus/AM</span>
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    marginBottom: '6px',
                    color: '#ccc'
                  }}>
                    <PhoneOutlined style={{ marginRight: '8px' }} />
                    <span>(92) 3232-3232</span>
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    color: '#ccc'
                  }}>
                    <MailOutlined style={{ marginRight: '8px' }} />
                    <span>suporte@cadastrocultural.am.gov.br</span>
                  </div>
                </div>

                <div>
                  <h5 style={{
                    color: '#1890ff',
                    marginBottom: '8px', // Reduzido de 12px
                    fontSize: '13px' // Reduzido de 14px
                  }}>
                    Redes Sociais
                  </h5>
                  <Space size="middle">
                    <a href="#" style={{ color: '#ccc' }}>
                      <FacebookOutlined style={{ fontSize: '18px' }} />
                    </a>
                    <a href="#" style={{ color: '#ccc' }}>
                      <TwitterOutlined style={{ fontSize: '18px' }} />
                    </a>
                    <a href="#" style={{ color: '#ccc' }}>
                      <InstagramOutlined style={{ fontSize: '18px' }} />
                    </a>
                    <a href="#" style={{ color: '#ccc' }}>
                      <YoutubeOutlined style={{ fontSize: '18px' }} />
                    </a>
                  </Space>
                </div>
              </div>
            </Col>
          </Row>

          <Divider style={{
            borderColor: 'rgba(255,255,255,0.2)',
            margin: '20px 0 8px' // Reduzido de 32px 0 16px
          }} />

          <Row justify="space-between" align="middle">
            <Col xs={24} sm={12}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                color: '#999',
                fontSize: '12px' // Reduzido de 14px
              }}>
                <CopyrightOutlined style={{ marginRight: '8px' }} />
                <span>
                  2024 Governo do Estado do Amazonas.
                  Todos os direitos reservados.
                </span>
              </div>
            </Col>

            <Col xs={24} sm={12} style={{ textAlign: 'right' }}>
              <Space size="large">
                <Link to="/privacidade" style={{
                  color: '#999',
                  textDecoration: 'none',
                  fontSize: '12px' // Reduzido de 14px
                }}>
                  Política de Privacidade
                </Link>
                <Link to="/termos" style={{
                  color: '#999',
                  textDecoration: 'none',
                  fontSize: '12px' // Reduzido de 14px
                }}>
                  Termos de Uso
                </Link>
              </Space>
            </Col>
          </Row>

          {/* Rodapé Institucional */}
          <div style={{
            marginTop: '8px', // Reduzido de 16px
            padding: '8px 0', // Reduzido de 16px 0
            borderTop: '1px solid rgba(255,255,255,0.1)',
            textAlign: 'center'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '12px', // Reduzido de 16px
              flexWrap: 'wrap'
            }}>
              <span style={{ color: '#999', fontSize: '11px' }}> {/* Reduzido de 12px */}
                Desenvolvido pela Secretaria de Cultura e Economia Criativa
              </span>
              <span style={{ color: '#999', fontSize: '11px' }}> {/* Reduzido de 12px */}
                |
              </span>
              <span style={{ color: '#999', fontSize: '11px' }}> {/* Reduzido de 12px */}
                Tecnologia da Informação - Governo Digital
              </span>
            </div>
          </div>
        </div>
      </motion.div>
    </AntFooter>
  );
};

export default Footer;
