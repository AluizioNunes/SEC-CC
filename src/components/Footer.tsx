import React from 'react';
import { Layout, Row, Col, Typography, Space } from 'antd';
import { motion } from 'framer-motion';

const { Footer: AntFooter } = Layout;
const { Text, Link } = Typography;

const Footer: React.FC = () => {
  return (
    <AntFooter
      style={{
        background: 'linear-gradient(135deg, #001529 0%, #000000 100%)',
        color: '#fff',
        padding: '40px 0 20px',
        marginTop: 'auto'
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px' }}>
          <Row gutter={[32, 32]}>
            {/* Logo e Informações Institucionais */}
            <Col xs={24} sm={8} md={6}>
              <div style={{ textAlign: 'center' }}>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  style={{
                    width: '80px',
                    height: '80px',
                    background: 'linear-gradient(135deg, #1890ff, #40a9ff)',
                    borderRadius: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 16px',
                    fontSize: '32px',
                    fontWeight: 'bold',
                    color: 'white',
                    cursor: 'pointer'
                  }}
                >
                  SEC
                </motion.div>
                <Text style={{ color: '#bae7ff', fontSize: '14px', display: 'block' }}>
                  Sistema Estadual de Cultura
                </Text>
                <Text style={{ color: '#91d5ff', fontSize: '12px', display: 'block' }}>
                  Governo do Amazonas
                </Text>
              </div>
            </Col>

            {/* Links Institucionais */}
            <Col xs={24} sm={8} md={6}>
              <div>
                <Text strong style={{ color: '#fff', fontSize: '16px', display: 'block', marginBottom: '16px' }}>
                  Institucional
                </Text>
                <Space direction="vertical" size="small">
                  <Link href="/sobre" style={{ color: '#91d5ff', fontSize: '14px' }}>
                    Sobre o SEC
                  </Link>
                  <Link href="/lgpd" style={{ color: '#91d5ff', fontSize: '14px' }}>
                    Política de Privacidade
                  </Link>
                  <Link href="/termos" style={{ color: '#91d5ff', fontSize: '14px' }}>
                    Termos de Uso
                  </Link>
                </Space>
              </div>
            </Col>

            {/* Suporte */}
            <Col xs={24} sm={8} md={6}>
              <div>
                <Text strong style={{ color: '#fff', fontSize: '16px', display: 'block', marginBottom: '16px' }}>
                  Suporte
                </Text>
                <Space direction="vertical" size="small">
                  <Link href="/suporte" style={{ color: '#91d5ff', fontSize: '14px' }}>
                    Central de Ajuda
                  </Link>
                  <Link href="/faq" style={{ color: '#91d5ff', fontSize: '14px' }}>
                    Perguntas Frequentes
                  </Link>
                  <Link href="mailto:suporte@cadastrocultural.am.gov.br" style={{ color: '#91d5ff', fontSize: '14px' }}>
                    Contato
                  </Link>
                </Space>
              </div>
            </Col>

            {/* Informações de Contato */}
            <Col xs={24} sm={24} md={6}>
              <div>
                <Text strong style={{ color: '#fff', fontSize: '16px', display: 'block', marginBottom: '16px' }}>
                  Contato
                </Text>
                <Space direction="vertical" size="small">
                  <Text style={{ color: '#91d5ff', fontSize: '14px' }}>
                    Email: suporte@cadastrocultural.am.gov.br
                  </Text>
                  <Text style={{ color: '#91d5ff', fontSize: '14px' }}>
                    Telefone: (92) 1234-5678
                  </Text>
                  <Text style={{ color: '#91d5ff', fontSize: '14px' }}>
                    Manaus - AM
                  </Text>
                </Space>
              </div>
            </Col>
          </Row>

          {/* Linha divisória */}
          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            style={{
              height: '1px',
              background: 'linear-gradient(90deg, transparent 0%, #1890ff 50%, transparent 100%)',
              margin: '32px 0',
              transformOrigin: 'center'
            }}
          />

          {/* Copyright e Informações Legais */}
          <Row justify="space-between" align="middle">
            <Col xs={24} sm={12}>
              <Text style={{ color: '#91d5ff', fontSize: '12px' }}>
                © 2024 Sistema Estadual de Cultura - Governo do Amazonas.
                Todos os direitos reservados.
              </Text>
            </Col>
            <Col xs={24} sm={12} style={{ textAlign: 'right' }}>
              <Text style={{ color: '#91d5ff', fontSize: '12px' }}>
                Lei Nº 6.306/2023 - Desenvolvido com ❤️ para a cultura amazonense
              </Text>
            </Col>
          </Row>
        </div>
      </motion.div>
    </AntFooter>
  );
};

export default Footer;
