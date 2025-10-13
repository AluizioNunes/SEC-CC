import React from 'react';
import { Card, Typography, List, Button } from 'antd';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

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
      <Card style={{ maxWidth: '800px', margin: '0 auto' }}>
        <Title level={2}>Sobre o Cadastro Cultural</Title>
        <Paragraph>
          O Sistema de Cadastro Estadual de Cultura do Amazonas é uma plataforma criada
          para reconhecer e apoiar os trabalhadores da cultura e espaços culturais do nosso estado.
        </Paragraph>

        <div style={{ marginTop: '32px' }}>
          <Title level={3}>Objetivos</Title>
          <ul>
            <li>Mapear e reconhecer trabalhadores da cultura</li>
            <li>Identificar espaços culturais em todo o estado</li>
            <li>Facilitar o acesso a políticas públicas de cultura</li>
            <li>Promover o desenvolvimento cultural sustentável</li>
          </ul>
        </div>

        <div style={{ marginTop: '32px' }}>
          <Title level={3}>Base Legal</Title>
          <Paragraph>
            Lei nº 6.306/2023 - Institui o Cadastro Estadual de Cultura do Amazonas
          </Paragraph>
        </div>

        <div style={{ marginTop: '32px', textAlign: 'center' }}>
          <Link to="/">
            <Button type="primary">Voltar ao Início</Button>
          </Link>
        </div>
      </Card>
    </motion.div>
  );
};

export default Sobre;
