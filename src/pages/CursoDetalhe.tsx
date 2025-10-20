import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Typography, Space, Tag, Button, Divider, List } from 'antd';
import { motion } from 'framer-motion';
import { courses } from '../mock/courses';

const { Title, Paragraph, Text } = Typography;

const CursoDetalhe: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const course = courses.find(c => c.id === id);

  if (!course) {
    return (
      <Card style={{ maxWidth: 900, margin: '24px auto' }}>
        <Title level={3}>Curso não encontrado</Title>
        <Button onClick={() => navigate('/cursos')}>Voltar ao catálogo</Button>
      </Card>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ padding: '24px' }}>
      <Card style={{ maxWidth: 1000, margin: '0 auto' }}>
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Title level={2} style={{ marginBottom: 0 }}>{course.title}</Title>
          <Space wrap>
            <Tag color="geekblue">{course.level}</Tag>
            <Tag color="cyan">{course.mode}</Tag>
            {course.enrollmentOpen ? <Tag color="green">Inscrições abertas</Tag> : <Tag color="red">Fechado</Tag>}
          </Space>

          <Divider />

          <Title level={4}>Descrição</Title>
          <Paragraph>{course.description}</Paragraph>

          <Title level={4}>Conteúdo programático</Title>
          <List dataSource={course.syllabus} renderItem={(item) => (<List.Item><Text>{item}</Text></List.Item>)} />

          <Space>
            <Button type="primary" size="large" disabled={!course.enrollmentOpen}>Inscrever-se</Button>
            <Button onClick={() => navigate('/cursos')}>Voltar</Button>
          </Space>
        </Space>
      </Card>
    </motion.div>
  );
};

export default CursoDetalhe;