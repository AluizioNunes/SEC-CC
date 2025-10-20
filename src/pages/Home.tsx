import React, { useState } from 'react';
import {
  Row,
  Col,
  Card,
  Typography,
  Statistic,
  Button,
  Space,
  Divider,
  Select,
  DatePicker,
  Radio,
  Tabs
} from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  BarChartOutlined,
  PieChartOutlined,
  LineChartOutlined,
  CalendarOutlined,
  DownloadOutlined,
  FileTextOutlined,
  SafetyOutlined,
  TrophyOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import ReactECharts from 'echarts-for-react';

const { Title, Paragraph } = Typography;
const { TabPane } = Tabs;
const { RangePicker } = DatePicker;
const { Option } = Select;

const Home: React.FC = () => {
  const [timeRange, setTimeRange] = useState('month');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Dados mockados baseados na Lei do Cadastro
  const statsData = {
    pessoasFisicas: {
      total: 1847,
      hoje: 12,
      semana: 89,
      mes: 342,
      ano: 1847,
      tendencia: '+12%'
    },
    pessoasJuridicas: {
      total: 423,
      hoje: 3,
      semana: 18,
      mes: 67,
      ano: 423,
      tendencia: '+8%'
    }
  };

  // Gráfico de distribuição por categoria (baseado na Lei)
  const categoriaChartData = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: '20%'
    },
    series: [
      {
        name: 'Categorias Culturais',
        type: 'pie',
        radius: ['30%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        data: [
          { value: 847, name: 'Artes Visuais', itemStyle: { color: '#1890ff' } },
          { value: 623, name: 'Música', itemStyle: { color: '#52c41a' } },
          { value: 423, name: 'Teatro/Cinema', itemStyle: { color: '#faad14' } },
          { value: 234, name: 'Dança', itemStyle: { color: '#722ed1' } },
          { value: 143, name: 'Literatura', itemStyle: { color: '#eb2f96' } }
        ]
      }
    ]
  };

  // Gráfico de evolução temporal
  const evolutionChartData = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['Pessoa Física', 'Pessoa Jurídica', 'Total']
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
      type: 'value',
      name: 'Número de Cadastros'
    },
    series: [
      {
        name: 'Pessoa Física',
        type: 'line',
        stack: 'Total',
        data: [120, 132, 101, 134, 90, 230, 210, 220, 240, 250, 260, 280],
        itemStyle: { color: '#1890ff' }
      },
      {
        name: 'Pessoa Jurídica',
        type: 'line',
        stack: 'Total',
        data: [220, 182, 191, 234, 290, 330, 310, 320, 340, 360, 380, 400],
        itemStyle: { color: '#52c41a' }
      },
      {
        name: 'Total',
        type: 'line',
        data: [340, 314, 292, 368, 380, 560, 520, 540, 580, 610, 640, 680],
        itemStyle: { color: '#722ed1' }
      }
    ]
  };

  // Gráfico de distribuição regional (baseado na Lei)
  const regionalChartData = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: 'Cadastros por Região',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 1200, name: 'Manaus', itemStyle: { color: '#1890ff' } },
          { value: 450, name: 'Interior', itemStyle: { color: '#52c41a' } },
          { value: 320, name: 'Outros Estados', itemStyle: { color: '#faad14' } },
          { value: 280, name: 'Não Informado', itemStyle: { color: '#722ed1' } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };

  // Gráfico de status dos cadastros (baseado na Lei)
  const statusChartData = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [
      {
        name: 'Status dos Cadastros',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '50%'],
        data: [
          { value: 1560, name: 'Homologados', itemStyle: { color: '#52c41a' } },
          { value: 423, name: 'Em Análise', itemStyle: { color: '#1890ff' } },
          { value: 187, name: 'Pendentes', itemStyle: { color: '#faad14' } },
          { value: 100, name: 'Indeferidos', itemStyle: { color: '#ff4d4f' } }
        ]
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
        minHeight: '100vh'
      }}
    >
      {/* Cards de Estatísticas - Pessoas Físicas e Jurídicas */}
      <motion.div variants={itemVariants} style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card
              style={{
                textAlign: 'center',
                borderLeft: '4px solid #1890ff',
                background: 'linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%)'
              }}
            >
              <Statistic
                title={
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    <UserOutlined style={{ color: '#1890ff' }} />
                    <span>Pessoas Físicas</span>
                  </div>
                }
                value={statsData.pessoasFisicas.total}
                suffix="cadastradas"
                valueStyle={{ color: '#1890ff', fontSize: '24px' }}
              />
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                <span style={{ color: '#52c41a', fontWeight: 'bold' }}>
                  {statsData.pessoasFisicas.tendencia}
                </span>
                {' '}vs mês anterior
              </div>
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card
              style={{
                textAlign: 'center',
                borderLeft: '4px solid #52c41a',
                background: 'linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%)'
              }}
            >
              <Statistic
                title={
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    <TeamOutlined style={{ color: '#52c41a' }} />
                    <span>Pessoas Jurídicas</span>
                  </div>
                }
                value={statsData.pessoasJuridicas.total}
                suffix="cadastradas"
                valueStyle={{ color: '#52c41a', fontSize: '24px' }}
              />
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                <span style={{ color: '#52c41a', fontWeight: 'bold' }}>
                  {statsData.pessoasJuridicas.tendencia}
                </span>
                {' '}vs mês anterior
              </div>
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card
              style={{
                textAlign: 'center',
                borderLeft: '4px solid #faad14',
                background: 'linear-gradient(135deg, #fffbe6 0%, #ffe58f 100%)'
              }}
            >
              <Statistic
                title="Total de Cadastros"
                value={statsData.pessoasFisicas.total + statsData.pessoasJuridicas.total}
                valueStyle={{ color: '#faad14', fontSize: '24px' }}
              />
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                Sistema ativo desde 2023
              </div>
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card
              style={{
                textAlign: 'center',
                borderLeft: '4px solid #722ed1',
                background: 'linear-gradient(135deg, #f9f0ff 0%, #efdbff 100%)'
              }}
            >
              <Statistic
                title="Taxa de Homologação"
                value={87}
                suffix="%"
                valueStyle={{ color: '#722ed1', fontSize: '24px' }}
              />
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                <span style={{ color: '#52c41a', fontWeight: 'bold' }}>+5%</span> vs mês anterior
              </div>
            </Card>
          </Col>
        </Row>
      </motion.div>

      {/* Gráficos Principais */}
      <motion.div variants={itemVariants} style={{ marginBottom: '24px' }}>
        <Tabs defaultActiveKey="evolution" type="card">
          <TabPane
            tab={
              <span>
                <LineChartOutlined />
                Evolução Temporal
              </span>
            }
            key="evolution"
          >
            <Card
              title={
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>Evolução de Cadastros por Período</span>
                  <Select
                    defaultValue="month"
                    style={{ width: 120 }}
                    onChange={setTimeRange}
                  >
                    <Option value="day">Por Dia</Option>
                    <Option value="week">Por Semana</Option>
                    <Option value="month">Por Mês</Option>
                    <Option value="year">Por Ano</Option>
                  </Select>
                </div>
              }
            >
              <ReactECharts
                option={evolutionChartData}
                style={{ height: '400px', width: '100%' }}
              />
            </Card>
          </TabPane>

          <TabPane
            tab={
              <span>
                <PieChartOutlined />
                Por Categoria
              </span>
            }
            key="categories"
          >
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={12}>
                <Card title="Categorias Culturais (Lei 6.306/2023)">
                  <ReactECharts
                    option={categoriaChartData}
                    style={{ height: '350px', width: '100%' }}
                  />
                </Card>
              </Col>
              <Col xs={24} lg={12}>
                <Card title="Distribuição Regional">
                  <ReactECharts
                    option={regionalChartData}
                    style={{ height: '350px', width: '100%' }}
                  />
                </Card>
              </Col>
            </Row>
          </TabPane>

          <TabPane
            tab={
              <span>
                <BarChartOutlined />
                Status dos Cadastros
              </span>
            }
            key="status"
          >
            <Card title="Status dos Cadastros (Conforme Lei 6.306/2023)">
              <ReactECharts
                option={statusChartData}
                style={{ height: '400px', width: '100%' }}
              />
            </Card>
          </TabPane>
        </Tabs>
      </motion.div>
    </motion.div>
  );
};

export default Home;
