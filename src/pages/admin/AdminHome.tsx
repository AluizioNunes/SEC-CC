import React from 'react';
import { Row, Col, Card, Typography, Button, Space } from 'antd';
import { UserOutlined, SafetyCertificateOutlined, LockOutlined, FileSearchOutlined, DashboardOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const { Title, Paragraph, Text } = Typography;

const AdminHome: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const go = (path: string) => navigate(path);

  return (
    <div style={{ padding: 16 }}>
      <Card style={{ marginBottom: 16, borderRadius: 0 }}>
        <Space direction="vertical" size={4} style={{ width: '100%' }}>
          <Title level={4} style={{ margin: 0 }}>Área Administrativa</Title>
          <Text type="secondary">Bem-vindo{user?.name ? `, ${user.name}` : ''}. Perfil: {(user?.rawProfile || user?.profile?.toUpperCase() || 'USER')}</Text>
          <Paragraph style={{ marginTop: 8 }}>
            Esta é a tela principal para administração do sistema. Acesse os módulos abaixo para gerenciar usuários, perfis,
            permissões e visualizar registros de auditoria.
          </Paragraph>
          <Button type="primary" icon={<DashboardOutlined />} onClick={() => go('/dashboard')} style={{ width: 240 }}>Ir para Dashboard</Button>
        </Space>
      </Card>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={12} lg={6}>
          <Card hoverable style={{ borderRadius: 0 }} onClick={() => go('/admin/usuarios')}>
            <Space direction="vertical" size={8}>
              <UserOutlined style={{ fontSize: 22 }} />
              <Title level={5} style={{ margin: 0 }}>Usuários</Title>
              <Text type="secondary">Gerencie contas, alterações e status.</Text>
              <Button type="link" onClick={() => go('/admin/usuarios')}>Abrir usuários</Button>
            </Space>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card hoverable style={{ borderRadius: 0 }} onClick={() => go('/admin/perfil')}>
            <Space direction="vertical" size={8}>
              <SafetyCertificateOutlined style={{ fontSize: 22 }} />
              <Title level={5} style={{ margin: 0 }}>Perfis</Title>
              <Text type="secondary">Crie, edite e organize perfis de acesso.</Text>
              <Button type="link" onClick={() => go('/admin/perfil')}>Abrir perfis</Button>
            </Space>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card hoverable style={{ borderRadius: 0 }} onClick={() => go('/admin/permissoes')}>
            <Space direction="vertical" size={8}>
              <LockOutlined style={{ fontSize: 22 }} />
              <Title level={5} style={{ margin: 0 }}>Permissões</Title>
              <Text type="secondary">Defina regras e acessos por perfil.</Text>
              <Button type="link" onClick={() => go('/admin/permissoes')}>Abrir permissões</Button>
            </Space>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card hoverable style={{ borderRadius: 0 }} onClick={() => go('/admin/auditoria')}>
            <Space direction="vertical" size={8}>
              <FileSearchOutlined style={{ fontSize: 22 }} />
              <Title level={5} style={{ margin: 0 }}>Auditoria</Title>
              <Text type="secondary">Acompanhe operações e histórico do sistema.</Text>
              <Button type="link" onClick={() => go('/admin/auditoria')}>Abrir auditoria</Button>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AdminHome;