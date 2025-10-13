import React from 'react';
import {
  Row,
  Col,
  Card,
  Typography,
  Statistic,
  Progress,
  Button,
  Space,
  Divider,
  List,
  Avatar,
  Tag,
  Alert,
  Badge
} from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  FileTextOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  PhoneOutlined,
  SettingOutlined,
  BellOutlined,
  DashboardOutlined,
  BarChartOutlined,
  PieChartOutlined,
  LineChartOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import ReactECharts from 'echarts-for-react';
import { useAuth } from '../contexts/AuthContext';

const { Title, Paragraph, Text } = Typography;

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  // Dados para os gráficos
  const statusChartData = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      top: '5%',
      left: 'center'
    },
    series: [
      {
        name: 'Status do Cadastro',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 1, name: 'Aprovado', itemStyle: { color: '#52c41a' } },
          { value: 0, name: 'Em Análise', itemStyle: { color: '#faad14' } },
          { value: 0, name: 'Pendente', itemStyle: { color: '#1890ff' } },
          { value: 0, name: 'Rejeitado', itemStyle: { color: '#ff4d4f' } }
        ]
      }
    ]
  };

  const activityChartData = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['Atividades', 'Notificações']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: 'Atividades',
        type: 'line',
        data: [5, 8, 12, 15, 10, 7, 3],
        smooth: true,
        itemStyle: { color: '#1890ff' }
      },
      {
        name: 'Notificações',
        type: 'line',
        data: [2, 4, 6, 8, 5, 3, 1],
        smooth: true,
        itemStyle: { color: '#faad14' }
      }
    ]
  };

  const mockNotifications = [
    {
      id: 1,
      title: 'Cadastro Aprovado',
      message: 'Seu cadastro foi aprovado pela comissão de análise.',
      type: 'success',
      date: 'Hoje às 14:30',
      unread: true
    },
    {
      id: 2,
      title: 'Documento Pendente',
      message: 'Falta enviar o comprovante de residência.',
      type: 'warning',
      date: 'Ontem às 16:45',
      unread: true
    },
    {
      id: 3,
      title: 'Atualização do Sistema',
      message: 'Novos recursos disponíveis na plataforma.',
      type: 'info',
      date: '2 dias atrás',
      unread: false
    }
  ];

  const mockRequests = [
    {
      id: 'REQ-001',
      type: 'Cadastro PF',
      status: 'approved',
      date: '15/12/2024',
      description: 'Cadastro de Artista Visual'
    },
    {
      id: 'REQ-002',
      type: 'Renovação',
      status: 'pending',
      date: '10/12/2024',
      description: 'Renovação de cadastro existente'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'success';
      case 'pending': return 'processing';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'approved': return 'Aprovado';
      case 'pending': return 'Em Análise';
      case 'rejected': return 'Rejeitado';
      default: return 'Pendente';
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      style={{
        padding: '24px',
        background: '#f0f2f5',
        minHeight: 'calc(100vh - 140px)'
      }}
    >
      {/* Cabeçalho do Dashboard */}
      <motion.div variants={itemVariants} style={{ marginBottom: '24px' }}>
        <Card>
          <Row gutter={[16, 16]} align="middle">
            <Col xs={24} sm={16}>
              <div>
                <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
                  Olá, {user?.name}!
                </Title>
                <Paragraph style={{ margin: '8px 0 0 0', color: '#666' }}>
                  Bem-vindo ao seu painel pessoal do Sistema de Cadastro Cultural
                </Paragraph>
              </div>
            </Col>
            <Col xs={24} sm={8} style={{ textAlign: 'right' }}>
              <Space>
                <Badge count={mockNotifications.filter(n => n.unread).length}>
                  <Button icon={<BellOutlined />} shape="circle" />
                </Badge>
                <Link to="/configuracoes">
                  <Button icon={<SettingOutlined />} shape="circle" />
                </Link>
              </Space>
            </Col>
          </Row>
        </Card>
      </motion.div>

      {/* Estatísticas Pessoais */}
      <motion.div variants={itemVariants} style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Meu Status"
                value={user?.status === 'approved' ? 'Aprovado' : 'Em Análise'}
                prefix={user?.status === 'approved' ? <CheckCircleOutlined /> : <ClockCircleOutlined />}
                valueStyle={{
                  color: user?.status === 'approved' ? '#52c41a' : '#faad14'
                }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Tipo de Cadastro"
                value={user?.type === 'PF' ? 'Pessoa Física' : 'Pessoa Jurídica'}
                prefix={<UserOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Solicitações"
                value={2}
                prefix={<FileTextOutlined />}
                suffix="ativas"
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="Progresso"
                value={75}
                prefix={<CheckCircleOutlined />}
                suffix="%"
              />
              <Progress percent={75} showInfo={false} strokeColor="#1890ff" />
            </Card>
          </Col>
        </Row>
      </motion.div>

      {/* Gráficos e Análises */}
      <motion.div variants={itemVariants} style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={8}>
            <Card
              title={
                <span>
                  <PieChartOutlined style={{ marginRight: '8px' }} />
                  Status do Meu Cadastro
                </span>
              }
              style={{ height: '400px' }}
            >
              <ReactECharts
                option={statusChartData}
                style={{ height: '300px', width: '100%' }}
              />
            </Card>
          </Col>

          <Col xs={24} lg={16}>
            <Card
              title={
                <span>
                  <LineChartOutlined style={{ marginRight: '8px' }} />
                  Atividade da Semana
                </span>
              }
              style={{ height: '400px' }}
            >
              <ReactECharts
                option={activityChartData}
                style={{ height: '300px', width: '100%' }}
              />
            </Card>
          </Col>
        </Row>
      </motion.div>

      {/* Minhas Solicitações e Notificações */}
      <motion.div variants={itemVariants} style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Card
              title={
                <span>
                  <FileTextOutlined style={{ marginRight: '8px' }} />
                  Minhas Solicitações
                </span>
              }
              extra={<Link to="/solicitacoes">Ver Todas</Link>}
            >
              <List
                dataSource={mockRequests}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={<Avatar icon={<FileTextOutlined />} />}
                      title={
                        <div>
                          <Text strong>{item.id}</Text>
                          <Tag color={getStatusColor(item.status)} style={{ marginLeft: '8px' }}>
                            {getStatusText(item.status)}
                          </Tag>
                        </div>
                      }
                      description={
                        <div>
                          <Text>{item.description}</Text>
                          <br />
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            Criado em {item.date}
                          </Text>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>

          <Col xs={24} lg={12}>
            <Card
              title={
                <span>
                  <BellOutlined style={{ marginRight: '8px' }} />
                  Notificações Recentes
                </span>
              }
              extra={<Link to="/notificacoes">Ver Todas</Link>}
            >
              <List
                dataSource={mockNotifications.slice(0, 3)}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        <Avatar
                          style={{
                            backgroundColor: item.unread ? '#1890ff' : '#d9d9d9',
                            color: 'white'
                          }}
                          icon={item.unread ? <BellOutlined /> : undefined}
                        />
                      }
                      title={
                        <div>
                          <Text strong={item.unread}>{item.title}</Text>
                          {item.unread && (
                            <Badge dot style={{ marginLeft: '8px' }} />
                          )}
                        </div>
                      }
                      description={
                        <div>
                          <Text>{item.message}</Text>
                          <br />
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {item.date}
                          </Text>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        </Row>
      </motion.div>

      {/* Ações Rápidas */}
      <motion.div variants={itemVariants} style={{ marginBottom: '24px' }}>
        <Card
          title={
            <span>
              <DashboardOutlined style={{ marginRight: '8px' }} />
              Ações Rápidas
            </span>
          }
        >
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={6}>
              <Card
                hoverable
                style={{
                  textAlign: 'center',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
                bodyStyle={{ padding: '16px' }}
                onClick={() => window.location.href = '/meu-cadastro'}
              >
                <UserOutlined style={{ fontSize: '24px', color: '#1890ff', marginBottom: '8px' }} />
                <Title level={5} style={{ margin: 0, color: '#1890ff' }}>
                  Editar Cadastro
                </Title>
              </Card>
            </Col>

            <Col xs={24} sm={6}>
              <Card
                hoverable
                style={{
                  textAlign: 'center',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
                bodyStyle={{ padding: '16px' }}
                onClick={() => window.location.href = '/solicitacoes'}
              >
                <FileTextOutlined style={{ fontSize: '24px', color: '#52c41a', marginBottom: '8px' }} />
                <Title level={5} style={{ margin: 0, color: '#52c41a' }}>
                  Minhas Solicitações
                </Title>
              </Card>
            </Col>

            <Col xs={24} sm={6}>
              <Card
                hoverable
                style={{
                  textAlign: 'center',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
                bodyStyle={{ padding: '16px' }}
                onClick={() => window.location.href = '/documentos'}
              >
                <CheckCircleOutlined style={{ fontSize: '24px', color: '#faad14', marginBottom: '8px' }} />
                <Title level={5} style={{ margin: 0, color: '#faad14' }}>
                  Documentos
                </Title>
              </Card>
            </Col>

            <Col xs={24} sm={6}>
              <Card
                hoverable
                style={{
                  textAlign: 'center',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
                bodyStyle={{ padding: '16px' }}
                onClick={() => window.location.href = '/suporte'}
              >
                <PhoneOutlined style={{ fontSize: '24px', color: '#722ed1', marginBottom: '8px' }} />
                <Title level={5} style={{ margin: 0, color: '#722ed1' }}>
                  Suporte
                </Title>
              </Card>
            </Col>
          </Row>
        </Card>
      </motion.div>

      {/* Alertas e Avisos */}
      <motion.div variants={itemVariants}>
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            {mockNotifications.some(n => n.type === 'warning') && (
              <Alert
                message="Documentação Pendente"
                description="Alguns documentos ainda precisam ser enviados para completar seu cadastro."
                type="warning"
                showIcon
                action={
                  <Button size="small" type="primary">
                    Enviar Documentos
                  </Button>
                }
                style={{ marginBottom: '16px' }}
              />
            )}

            <Card
              title={
                <span>
                  <InfoCircleOutlined style={{ marginRight: '8px' }} />
                  Próximos Passos
                </span>
              }
            >
              <div style={{ padding: '16px 0' }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                  <CheckCircleOutlined style={{ color: '#52c41a', marginRight: '8px' }} />
                  <span>Cadastro enviado para análise</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                  <ClockCircleOutlined style={{ color: '#faad14', marginRight: '8px' }} />
                  <span>Aguardando análise da documentação</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <InfoCircleOutlined style={{ color: '#1890ff', marginRight: '8px' }} />
                  <span>Resultado será enviado por e-mail</span>
                </div>
              </div>
            </Card>
          </Col>

          <Col xs={24} lg={12}>
            <Card
              title={
                <span>
                  <BarChartOutlined style={{ marginRight: '8px' }} />
                  Estatísticas Pessoais
                </span>
              }
            >
              <div style={{ padding: '16px 0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span>Tempo médio de resposta:</span>
                  <Text strong>3 dias</Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span>Documentos enviados:</span>
                  <Text strong>8/10</Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span>Última atualização:</span>
                  <Text strong>Hoje</Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Status geral:</span>
                  <Tag color="processing">Em Análise</Tag>
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      </motion.div>
    </motion.div>
  );
};

export default Dashboard;
