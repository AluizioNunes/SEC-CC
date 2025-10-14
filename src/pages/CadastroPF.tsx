import React, { useState } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Row,
  Col,
  Statistic,
  Typography,
  Tag,
  Space,
  Avatar,
  Tooltip,
  Select,
  DatePicker,
  Modal,
  Form,
  message
} from 'antd';
import {
  UserOutlined,
  PlusOutlined,
  SearchOutlined,
  FilterOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  DownloadOutlined,
  ReloadOutlined,
  IdcardOutlined,
  MailOutlined,
  PhoneOutlined,
  EnvironmentOutlined,
  TeamOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { usePessoaFisica } from '../contexts/PessoaFisicaContext';
import CadastroPFModal from '../components/CadastroPFModal';

const { Title, Text } = Typography;
const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface PessoaFisicaCardProps {
  pessoa: any;
  onEdit: (pessoa: any) => void;
  onDelete: (id: string) => void;
  onView: (pessoa: any) => void;
}

const PessoaFisicaCard: React.FC<PessoaFisicaCardProps> = ({ pessoa, onEdit, onDelete, onView }) => {
  const getInitials = (nome: string) => {
    return nome.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ativo': return 'green';
      case 'inativo': return 'red';
      case 'pendente': return 'orange';
      default: return 'default';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        hoverable
        style={{
          height: '100%',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}
        bodyStyle={{ padding: '16px' }}
      >
        <div style={{ textAlign: 'center', marginBottom: '16px' }}>
          <Avatar
            size={64}
            style={{
              backgroundColor: '#1890ff',
              marginBottom: '8px'
            }}
          >
            {getInitials(pessoa.nome)}
          </Avatar>
          <Title level={5} style={{ margin: 0, fontSize: '14px' }}>
            {pessoa.nome}
          </Title>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            CPF: {pessoa.cpf}
          </Text>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
            <MailOutlined style={{ marginRight: '8px', color: '#666' }} />
            <Text style={{ fontSize: '12px' }}>{pessoa.email}</Text>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
            <PhoneOutlined style={{ marginRight: '8px', color: '#666' }} />
            <Text style={{ fontSize: '12px' }}>{pessoa.celular}</Text>
          </div>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <EnvironmentOutlined style={{ marginRight: '8px', color: '#666' }} />
            <Text style={{ fontSize: '12px' }}>
              {pessoa.endereco.cidade} - {pessoa.endereco.estado}
            </Text>
          </div>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <Tag color={getStatusColor(pessoa.situacao)} style={{ marginBottom: '8px' }}>
            {pessoa.situacao.toUpperCase()}
          </Tag>
          <div style={{ fontSize: '11px', color: '#666' }}>
            <strong>Profissão:</strong> {pessoa.profissao}
          </div>
          <div style={{ fontSize: '11px', color: '#666' }}>
            <strong>Cadastro:</strong> {new Date(pessoa.dataCadastro).toLocaleDateString('pt-BR')}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space size="small">
            <Tooltip title="Visualizar">
              <Button
                type="text"
                size="small"
                icon={<EyeOutlined />}
                onClick={() => onView(pessoa)}
              />
            </Tooltip>
            <Tooltip title="Editar">
              <Button
                type="text"
                size="small"
                icon={<EditOutlined />}
                onClick={() => onEdit(pessoa)}
              />
            </Tooltip>
            <Tooltip title="Excluir">
              <Button
                type="text"
                size="small"
                icon={<DeleteOutlined />}
                danger
                onClick={() => onDelete(pessoa.id)}
              />
            </Tooltip>
          </Space>
        </div>
      </Card>
    </motion.div>
  );
};

const CadastroPF: React.FC = () => {
  const { pessoasFisicas, loading, error, deletarPessoaFisica, buscarPessoasPorFiltro } = usePessoaFisica();
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('todos');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingPessoa, setEditingPessoa] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('cards');
  const [filteredPessoas, setFilteredPessoas] = useState(pessoasFisicas);

  // Estatísticas
  const totalPessoas = pessoasFisicas.length;
  const pessoasAtivas = pessoasFisicas.filter(p => p.situacao === 'ativo').length;
  const pessoasPendentes = pessoasFisicas.filter(p => p.situacao === 'pendente').length;

  // Aplicar filtros
  React.useEffect(() => {
    let filtered = pessoasFisicas;

    // Filtro por texto
    if (searchText) {
      filtered = filtered.filter(pessoa =>
        pessoa.nome.toLowerCase().includes(searchText.toLowerCase()) ||
        pessoa.cpf.includes(searchText) ||
        pessoa.email.toLowerCase().includes(searchText.toLowerCase())
      );
    }

    // Filtro por status
    if (statusFilter !== 'todos') {
      filtered = filtered.filter(pessoa => pessoa.situacao === statusFilter);
    }

    setFilteredPessoas(filtered);
  }, [searchText, statusFilter, pessoasFisicas]);

  const handleDelete = async (id: string) => {
    Modal.confirm({
      title: 'Confirmar exclusão',
      content: 'Tem certeza que deseja excluir esta pessoa física?',
      okText: 'Excluir',
      cancelText: 'Cancelar',
      onOk: async () => {
        try {
          await deletarPessoaFisica(id);
          message.success('Pessoa física excluída com sucesso!');
        } catch (error) {
          message.error('Erro ao excluir pessoa física');
        }
      }
    });
  };

  const handleEdit = (pessoa: any) => {
    setEditingPessoa(pessoa);
    setIsModalVisible(true);
  };

  const handleView = (pessoa: any) => {
    setEditingPessoa(pessoa);
    setViewMode('cards');
  };

  const handleAdd = () => {
    setEditingPessoa(null);
    setIsModalVisible(true);
  };

  const handleModalClose = () => {
    setIsModalVisible(false);
    setEditingPessoa(null);
  };

  const columns = [
    {
      title: 'Nome',
      dataIndex: 'nome',
      key: 'nome',
      render: (nome: string, record: any) => (
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Avatar
            size="small"
            style={{ marginRight: '8px', backgroundColor: '#1890ff' }}
          >
            {nome.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
          </Avatar>
          <span>{nome}</span>
        </div>
      )
    },
    {
      title: 'CPF',
      dataIndex: 'cpf',
      key: 'cpf'
    },
    {
      title: 'E-mail',
      dataIndex: 'email',
      key: 'email'
    },
    {
      title: 'Telefone',
      dataIndex: 'celular',
      key: 'celular'
    },
    {
      title: 'Cidade',
      dataIndex: ['endereco', 'cidade'],
      key: 'cidade'
    },
    {
      title: 'Profissão',
      dataIndex: 'profissao',
      key: 'profissao'
    },
    {
      title: 'Status',
      dataIndex: 'situacao',
      key: 'situacao',
      render: (situacao: string) => {
        const colors = {
          ativo: 'green',
          inativo: 'red',
          pendente: 'orange'
        };
        return <Tag color={colors[situacao as keyof typeof colors]}>{situacao.toUpperCase()}</Tag>;
      }
    },
    {
      title: 'Ações',
      key: 'acoes',
      render: (record: any) => (
        <Space size="small">
          <Tooltip title="Visualizar">
            <Button type="text" size="small" icon={<EyeOutlined />} onClick={() => handleView(record)} />
          </Tooltip>
          <Tooltip title="Editar">
            <Button type="text" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          </Tooltip>
          <Tooltip title="Excluir">
            <Button type="text" size="small" icon={<DeleteOutlined />} danger onClick={() => handleDelete(record.id)} />
          </Tooltip>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px', background: '#f0f2f5', minHeight: '100vh' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Cabeçalho */}
        <div style={{ marginBottom: '24px' }}>
          <Title level={2} style={{ margin: 0, color: '#1e3c72' }}>
            <IdcardOutlined style={{ marginRight: '12px' }} />
            Cadastro de Pessoas Físicas
          </Title>
          <Text type="secondary">
            Gerencie os cadastros de pessoas físicas no Sistema Estadual de Cultura
          </Text>
        </div>

        {/* Estatísticas */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="Total de Cadastros"
                value={totalPessoas}
                prefix={<TeamOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="Pessoas Ativas"
                value={pessoasAtivas}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="Pendentes"
                value={pessoasPendentes}
                prefix={<ReloadOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Filtros e Ações */}
        <Card style={{ marginBottom: '24px' }}>
          <Row gutter={[16, 16]} align="middle">
            <Col xs={24} sm={8} md={6}>
              <Search
                placeholder="Buscar por nome, CPF ou e-mail"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                prefix={<SearchOutlined />}
              />
            </Col>
            <Col xs={24} sm={8} md={4}>
              <Select
                style={{ width: '100%' }}
                placeholder="Filtrar por status"
                value={statusFilter}
                onChange={setStatusFilter}
                suffixIcon={<FilterOutlined />}
              >
                <Option value="todos">Todos</Option>
                <Option value="ativo">Ativo</Option>
                <Option value="inativo">Inativo</Option>
                <Option value="pendente">Pendente</Option>
              </Select>
            </Col>
            <Col xs={24} sm={8} md={6}>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleAdd}
                block
              >
                Cadastrar Pessoa Física
              </Button>
            </Col>
            <Col xs={24} sm={8} md={8} style={{ textAlign: 'right' }}>
              <Space>
                <Button icon={<ReloadOutlined />} onClick={() => window.location.reload()}>
                  Atualizar
                </Button>
                <Button icon={<DownloadOutlined />}>
                  Exportar
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        {/* Toggle entre Table e Cards */}
        <div style={{ marginBottom: '16px', textAlign: 'right' }}>
          <Space>
            <Text>Visualização:</Text>
            <Button
              type={viewMode === 'cards' ? 'primary' : 'default'}
              size="small"
              onClick={() => setViewMode('cards')}
            >
              Cards
            </Button>
            <Button
              type={viewMode === 'table' ? 'primary' : 'default'}
              size="small"
              onClick={() => setViewMode('table')}
            >
              Tabela
            </Button>
          </Space>
        </div>

        {/* Resultados */}
        {error && (
          <Card style={{ marginBottom: '16px' }}>
            <Text type="danger">{error}</Text>
          </Card>
        )}

        {viewMode === 'cards' ? (
          <Row gutter={[16, 16]}>
            {filteredPessoas.map((pessoa) => (
              <Col xs={24} sm={12} md={8} lg={6} key={pessoa.id}>
                <PessoaFisicaCard
                  pessoa={pessoa}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                  onView={handleView}
                />
              </Col>
            ))}
          </Row>
        ) : (
          <Table
            columns={columns}
            dataSource={filteredPessoas}
            loading={loading}
            rowKey="id"
            pagination={{
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) =>
                `${range[0]}-${range[1]} de ${total} cadastros`
            }}
            scroll={{ x: 800 }}
          />
        )}

        {/* Modal de Cadastro/Edição */}
        <CadastroPFModal
          visible={isModalVisible}
          pessoa={editingPessoa}
          onClose={handleModalClose}
        />
      </motion.div>
    </div>
  );
};

export default CadastroPF;
