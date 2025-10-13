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
  Timeline
} from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  InfoCircleOutlined,
  PhoneOutlined,
  FileTextOutlined,
  ArrowRightOutlined,
  TrophyOutlined,
  SafetyOutlined,
  ClockCircleOutlined,
  BarChartOutlined,
  PieChartOutlined,
  LineChartOutlined
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import ReactECharts from 'echarts-for-react';

const { Title, Paragraph, Text } = Typography;
const { Countdown } = Statistic;

const Home: React.FC = () => {
  // Dados para os gráficos
  const chartData = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      top: '5%',
      left: 'center'
    },
    series: [
      {
        name: 'Cadastro por Categoria',
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
          { value: 1250, name: 'Pessoa Física' },
          { value: 750, name: 'Pessoa Jurídica' },
          { value: 300, name: 'Em Análise' },
          { value: 200, name: 'Pendente' }
        ]
      }
    ]
  };

  const lineChartData = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['Cadastros PF', 'Cadastros PJ', 'Total']
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
      data: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: 'Cadastros PF',
        type: 'line',
        stack: 'Total',
        data: [120, 132, 101, 134, 90, 230, 210, 220, 240, 250, 260, 280]
      },
      {
        name: 'Cadastros PJ',
        type: 'line',
        stack: 'Total',
        data: [220, 182, 191, 234, 290, 330, 310, 320, 340, 360, 380, 400]
      },
      {
        name: 'Total',
        type: 'line',
        stack: 'Total',
        data: [340, 314, 292, 368, 380, 560, 520, 540, 580, 610, 640, 680]
      }
    ]
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
      {/* Estatísticas e Gráficos em linha */}
      <motion.div variants={itemVariants} style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          {/* Estatísticas do Sistema */}
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="Total de Cadastros"
                value={2500}
                prefix={<UserOutlined />}
                suffix="cadastros"
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="Em Análise"
                value={320}
                prefix={<ClockCircleOutlined />}
                suffix="pendentes"
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="Taxa de Aprovação"
                value={87}
                prefix={<CheckCircleOutlined />}
                suffix="%"
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
        </Row>
      </motion.div>

      {/* Gráficos e Timeline em linha */}
      <motion.div variants={itemVariants} style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          {/* Gráfico Principal */}
          <Col xs={24} lg={8}>
            <Card
              title={
                <span>
                  <BarChartOutlined style={{ marginRight: '8px' }} />
                  Estatísticas de Cadastro
                </span>
              }
              style={{ height: '350px' }}
            >
              <ReactECharts
                option={chartData}
                style={{ height: '280px', width: '100%' }}
              />
            </Card>
          </Col>

          {/* Evolução Mensal */}
          <Col xs={24} lg={8}>
            <Card
              title={
                <span>
                  <PieChartOutlined style={{ marginRight: '8px' }} />
                  Evolução Mensal
                </span>
              }
              style={{ height: '350px' }}
            >
              <ReactECharts
                option={lineChartData}
                style={{ height: '280px', width: '100%' }}
              />
            </Card>
          </Col>

          {/* Últimas Conquistas */}
          <Col xs={24} lg={8}>
            <Card
              title={
                <span>
                  <TrophyOutlined style={{ marginRight: '8px' }} />
                  Últimas Conquistas
                </span>
              }
              style={{ height: '350px' }}
            >
              <Timeline>
                <Timeline.Item color="green">
                  <p>Meta de 2.500 cadastros atingida!</p>
                  <small>Hoje às 14:30</small>
                </Timeline.Item>
                <Timeline.Item color="blue">
                  <p>Novos recursos de análise implementados</p>
                  <small>Ontem às 16:45</small>
                </Timeline.Item>
                <Timeline.Item color="orange">
                  <p>Sistema de notificações aprimorado</p>
                  <small>2 dias atrás</small>
                </Timeline.Item>
                <Timeline.Item>
                  <p>Integração com APIs externas concluída</p>
                  <small>3 dias atrás</small>
                </Timeline.Item>
              </Timeline>
            </Card>
          </Col>
        </Row>
      </motion.div>

      {/* Cards de Ação Rápida - Mais compactos */}
      <motion.div variants={itemVariants} style={{ marginBottom: '24px' }}>
        <Card
          title={
            <span>
              <ArrowRightOutlined style={{ marginRight: '8px' }} />
              Ações Rápidas
            </span>
          }
        >
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={8}>
              <Card
                hoverable
                style={{
                  textAlign: 'center',
                  border: '2px solid #1890ff',
                  borderRadius: '8px'
                }}
                bodyStyle={{ padding: '16px' }}
              >
                <UserOutlined style={{ fontSize: '24px', color: '#1890ff', marginBottom: '12px' }} />
                <Title level={5} style={{ color: '#1890ff', marginBottom: '8px' }}>
                  Novo Cadastro PF
                </Title>
                <Paragraph style={{ marginBottom: '12px', fontSize: '13px' }}>
                  Inicie o cadastro de pessoa física para trabalhadores da cultura.
                </Paragraph>
                <Link to="/cadastro">
                  <Button type="primary" size="small" block>
                    Cadastrar PF
                  </Button>
                </Link>
              </Card>
            </Col>

            <Col xs={24} sm={8}>
              <Card
                hoverable
                style={{
                  textAlign: 'center',
                  border: '2px solid #52c41a',
                  borderRadius: '8px'
                }}
                bodyStyle={{ padding: '16px' }}
              >
                <TeamOutlined style={{ fontSize: '24px', color: '#52c41a', marginBottom: '12px' }} />
                <Title level={5} style={{ color: '#52c41a', marginBottom: '8px' }}>
                  Novo Cadastro PJ
                </Title>
                <Paragraph style={{ marginBottom: '12px', fontSize: '13px' }}>
                  Cadastre espaços culturais e organizações do Amazonas.
                </Paragraph>
                <Link to="/cadastro">
                  <Button type="primary" size="small" block style={{ background: '#52c41a', borderColor: '#52c41a' }}>
                    Cadastrar PJ
                  </Button>
                </Link>
              </Card>
            </Col>

            <Col xs={24} sm={8}>
              <Card
                hoverable
                style={{
                  textAlign: 'center',
                  border: '2px solid #faad14',
                  borderRadius: '8px'
                }}
                bodyStyle={{ padding: '16px' }}
              >
                <FileTextOutlined style={{ fontSize: '24px', color: '#faad14', marginBottom: '12px' }} />
                <Title level={5} style={{ color: '#faad14', marginBottom: '8px' }}>
                  Ver Resultados
                </Title>
                <Paragraph style={{ marginBottom: '12px', fontSize: '13px' }}>
                  Consulte a lista pública de cadastros homologados.
                </Paragraph>
                <Link to="/resultados">
                  <Button type="primary" size="small" block style={{ background: '#faad14', borderColor: '#faad14' }}>
                    Ver Resultados
                  </Button>
                </Link>
              </Card>
            </Col>
          </Row>
        </Card>
      </motion.div>

      {/* Sobre o Sistema - Sem status do sistema */}
      <motion.div variants={itemVariants}>
        <Card
          title={
            <span>
              <InfoCircleOutlined style={{ marginRight: '8px' }} />
              Sobre o Sistema SEC
            </span>
          }
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
                  <Link to="/sobre">
                    <Button type="link" icon={<InfoCircleOutlined />}>
                      Sobre o Cadastro
                    </Button>
                  </Link>
                  <Link to="/contato">
                    <Button type="link" icon={<PhoneOutlined />}>
                      Fale Conosco
                    </Button>
                  </Link>
                  <Link to="/resultados">
                    <Button type="link" icon={<FileTextOutlined />}>
                      Resultados Oficiais
                    </Button>
                  </Link>
                </Space>
              </div>
            </Col>
          </Row>
        </Card>
      </motion.div>
    </motion.div>
  );
};

export default Home;
