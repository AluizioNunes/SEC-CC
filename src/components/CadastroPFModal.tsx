import React, { useEffect, useState } from 'react';
import {
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  Button,
  Row,
  Col,
  Card,
  Typography,
  Divider,
  Space,
  Tabs,
  message,
  Checkbox,
  Radio,
  Steps
} from 'antd';
import {
  SaveOutlined,
  CloseOutlined,
  UserOutlined,
  IdcardOutlined,
  EnvironmentOutlined,
  PhoneOutlined,
  MailOutlined,
  TeamOutlined,
  BookOutlined
} from '@ant-design/icons';
import type { PessoaFisica } from '../contexts/PessoaFisicaContext';
import { usePessoaFisica } from '../contexts/PessoaFisicaContext';
import dayjs from 'dayjs';
import { format } from 'date-fns';
import SECGovLogo from '../Images/SEC_GOV-LogoOficial.png';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;
const { TextArea } = Input;

interface CadastroPFModalProps {
  visible: boolean;
  pessoa?: PessoaFisica | null;
  onClose: () => void;
}

const CadastroPFModal: React.FC<CadastroPFModalProps> = ({ visible, pessoa, onClose }) => {
  const [form] = Form.useForm();
  const { criarPessoaFisica, atualizarPessoaFisica, loading } = usePessoaFisica();
  const [activeTabKey, setActiveTabKey] = useState<string>('dados-pessoais');

  // Exceções para não converter em MAIÚSCULO
  const uppercaseExceptions = new Set([
    'email',
    'instagram',
    'facebook',
    'twitter',
    'linkedin',
    'youtube',
    'site',
    'website',
    'portfolio',
    'portifolio',
    'redeSocial',
    'redesSociais'
  ]);

  const isExceptionKey = (key: string) => uppercaseExceptions.has(key.toLowerCase());

  const toUpperDeep = (obj: any, path: string[] = []) => {
    if (!obj || typeof obj !== 'object') return obj;
    const result: any = Array.isArray(obj) ? [] : {};
    for (const key of Object.keys(obj)) {
      const val = (obj as any)[key];
      const lastKey = key;
      if (typeof val === 'string' && !isExceptionKey(lastKey)) {
        result[key] = val.toUpperCase();
      } else if (val && typeof val === 'object' && !dayjs.isDayjs(val)) {
        result[key] = toUpperDeep(val, [...path, key]);
      } else {
        result[key] = val;
      }
    }
    return result;
  };

  const hasDiff = (a: any, b: any): boolean => {
    if (a === b) return false;
    if (!a || !b) return false;
    if (typeof a !== 'object' || typeof b !== 'object') return false;
    for (const key of Object.keys(a)) {
      const v1 = a[key];
      const v2 = b[key];
      if (typeof v1 === 'string' && v1 !== v2) return true;
      if (v1 && typeof v1 === 'object') {
        if (hasDiff(v1, v2)) return true;
      }
    }
    return false;
  };

  const stepItems = [
    { key: 'dados-pessoais', title: 'Dados Pessoais', icon: <UserOutlined /> },
    { key: 'contato', title: 'Contato', icon: <MailOutlined /> },
    { key: 'endereco', title: 'Endereço', icon: <EnvironmentOutlined /> },
    { key: 'naturalidade', title: 'Naturalidade', icon: <IdcardOutlined /> },
    { key: 'documentos', title: 'Documentos', icon: <IdcardOutlined /> },
    { key: 'informacoes-culturais', title: 'Informações Culturais', icon: <BookOutlined /> },
    { key: 'situacao', title: 'Situação', icon: <TeamOutlined /> },
  ];
  const currentStep = stepItems.findIndex((s) => s.key === activeTabKey);

  // Estados brasileiros
  const estadosBrasileiros = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
    'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
  ];

  // Áreas de atuação cultural
  const areasAtuacao = [
    'Artes Visuais',
    'Artes Cênicas',
    'Música',
    'Dança',
    'Literatura',
    'Audiovisual',
    'Artesanato',
    'Cultura Popular',
    'Patrimônio Cultural',
    'Gestão Cultural',
    'Produção Cultural',
    'Educação Artística',
    'Curadoria',
    'Crítica Cultural',
    'Pesquisa Cultural'
  ];

  // Níveis de formação
  const niveisFormacao = [
    'Ensino Fundamental',
    'Ensino Médio',
    'Ensino Técnico',
    'Ensino Superior',
    'Pós-graduação',
    'Mestrado',
    'Doutorado',
    'Pós-doutorado'
  ];

  useEffect(() => {
    if (pessoa) {
      form.setFieldsValue({
        ...pessoa,
        dataNascimento: pessoa.dataNascimento ? dayjs(pessoa.dataNascimento) : null,
        documentos: {
          ...pessoa.documentos,
          dataExpedicao: pessoa.documentos?.dataExpedicao ? dayjs(pessoa.documentos.dataExpedicao) : null
        }
      });
    } else {
      form.resetFields();
    }
  }, [pessoa, form]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();

      // Estrutura os dados conforme a interface PessoaFisica
      const pessoaData = {
        cpf: values.cpf,
        nome: values.nome,
        dataNascimento: format(values.dataNascimento.toDate(), 'yyyy-MM-dd'),
        email: values.email,
        telefone: values.telefone,
        celular: values.celular,
        endereco: {
          cep: values.endereco.cep,
          logradouro: values.endereco.logradouro,
          numero: values.endereco.numero,
          complemento: values.endereco.complemento,
          bairro: values.endereco.bairro,
          cidade: values.endereco.cidade,
          estado: values.endereco.estado,
          pais: values.endereco.pais || 'Brasil'
        },
        profissao: values.profissao,
        estadoCivil: values.estadoCivil,
        nacionalidade: values.nacionalidade,
        naturalidade: {
          cidade: values.naturalidade.cidade,
          estado: values.naturalidade.estado,
          pais: values.naturalidade.pais || 'Brasil'
        },
        documentos: {
          rg: values.documentos.rg,
          orgaoExpedidor: values.documentos.orgaoExpedidor,
          dataExpedicao: format(values.documentos.dataExpedicao.toDate(), 'yyyy-MM-dd'),
          tituloEleitor: values.documentos.tituloEleitor,
          carteiraTrabalho: values.documentos.carteiraTrabalho,
          certificadoReservista: values.documentos.certificadoReservista
        },
        informacoesCulturais: {
          areaAtuacao: values.informacoesCulturais.areaAtuacao,
          experiencia: values.informacoesCulturais.experiencia,
          formacao: values.informacoesCulturais.formacao,
          interesses: values.informacoesCulturais.interesses,
          disponibilidade: values.informacoesCulturais.disponibilidade
        },
        situacao: values.situacao || 'pendente',
        observacoes: values.observacoes
      };

      if (pessoa) {
        await atualizarPessoaFisica(pessoa.id, pessoaData);
        message.success('Pessoa física atualizada com sucesso!');
      } else {
        await criarPessoaFisica(pessoaData);
        message.success('Pessoa física cadastrada com sucesso!');
      }

      onClose();
    } catch (error) {
      message.error('Erro ao salvar pessoa física');
    }
  };

  const validarCPF = (cpf: string) => {
    // Remove caracteres não numéricos
    cpf = cpf.replace(/[^\d]/g, '');

    // Verifica se tem 11 dígitos
    if (cpf.length !== 11) return false;

    // Verifica se todos os dígitos são iguais
    if (/^(\d)\1+$/.test(cpf)) return false;

    // Calcula os dígitos verificadores
    let soma = 0;
    for (let i = 0; i < 9; i++) {
      soma += parseInt(cpf.charAt(i)) * (10 - i);
    }

    let resto = (soma * 10) % 11;
    if (resto === 10 || resto === 11) resto = 0;

    if (resto !== parseInt(cpf.charAt(9))) return false;

    soma = 0;
    for (let i = 0; i < 10; i++) {
      soma += parseInt(cpf.charAt(i)) * (11 - i);
    }

    resto = (soma * 10) % 11;
    if (resto === 10 || resto === 11) resto = 0;

    return resto === parseInt(cpf.charAt(10));
  };

  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <img src={SECGovLogo} alt="Logo SEC" style={{ height: 40 }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <IdcardOutlined style={{ color: '#1890ff' }} />
            {pessoa ? 'Editar Pessoa Física' : 'Cadastrar Pessoa Física'}
          </div>
        </div>
      }
      visible={visible}
      onCancel={onClose}
      centered
      width={'75%'}
      styles={{
        content: { height: '84vh' },
        body: { minHeight: '80vh', maxHeight: '80vh', overflowY: 'auto' }
      }}
      footer={[
        <Button key="cancel" onClick={onClose} icon={<CloseOutlined />}>
          Cancelar
        </Button>,
        <Button
          key="submit"
          type="primary"
          loading={loading}
          onClick={handleSubmit}
          icon={<SaveOutlined />}
        >
          {pessoa ? 'Atualizar' : 'Cadastrar'}
        </Button>
      ]}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          situacao: 'pendente',
          nacionalidade: 'Brasileira',
          endereco: { pais: 'Brasil' },
          naturalidade: { pais: 'Brasil' }
        }}
        onValuesChange={(changed) => {
          const converted = toUpperDeep(changed);
          if (hasDiff(changed, converted)) {
            form.setFieldsValue(converted);
          }
        }}
      >
        <div style={{ marginBottom: 16 }}>
          <Steps
            size="small"
            current={currentStep}
            onChange={(index) => setActiveTabKey(stepItems[index].key)}
            items={stepItems.map((s) => ({ title: s.title, icon: s.icon }))}
          />
        </div>

        <Tabs activeKey={activeTabKey} onChange={setActiveTabKey} type="card">
          {/* Dados Pessoais */}
          <TabPane tab="Dados Pessoais" key="dados-pessoais">
            <Row gutter={16}>
              <Col span={24}>
                <Card title="Informações Básicas" size="small">
                  <Row gutter={16}>
                    <Col xs={24} sm={8}>
                      <Form.Item
                        label="CPF"
                        name="cpf"
                        rules={[
                          { required: true, message: 'CPF é obrigatório!' },
                          {
                            validator: (_, value) => {
                              if (!value || validarCPF(value)) {
                                return Promise.resolve();
                              }
                              return Promise.reject('CPF inválido!');
                            }
                          }
                        ]}
                      >
                        <Input placeholder="000.000.000-00" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={16}>
                      <Form.Item
                        label="Nome Completo"
                        name="nome"
                        rules={[
                          { required: true, message: 'Nome é obrigatório!' },
                          { min: 3, message: 'Nome deve ter pelo menos 3 caracteres!' }
                        ]}
                      >
                        <Input placeholder="Nome completo" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col xs={24} sm={8}>
                      <Form.Item
                        label="Data de Nascimento"
                        name="dataNascimento"
                        rules={[
                          { required: true, message: 'Data de nascimento é obrigatória!' }
                        ]}
                      >
                        <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={8}>
                      <Form.Item
                        label="Estado Civil"
                        name="estadoCivil"
                        rules={[
                          { required: true, message: 'Estado civil é obrigatório!' }
                        ]}
                      >
                        <Select placeholder="Selecione o estado civil">
                          <Option value="solteiro">Solteiro(a)</Option>
                          <Option value="casado">Casado(a)</Option>
                          <Option value="divorciado">Divorciado(a)</Option>
                          <Option value="viuvo">Viúvo(a)</Option>
                          <Option value="separado">Separado(a)</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={8}>
                      <Form.Item
                        label="Nacionalidade"
                        name="nacionalidade"
                        rules={[
                          { required: true, message: 'Nacionalidade é obrigatória!' }
                        ]}
                      >
                        <Input placeholder="Ex: Brasileira" />
                      </Form.Item>
                    </Col>
                  </Row>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Contato */}
          <TabPane tab="Contato" key="contato">
            <Row gutter={16}>
              <Col span={24}>
                <Card title="Informações de Contato" size="small">
                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="E-mail"
                        name="email"
                        rules={[
                          { required: true, message: 'E-mail é obrigatório!' },
                          { type: 'email', message: 'E-mail inválido!' }
                        ]}
                      >
                        <Input prefix={<MailOutlined />} placeholder="seu@email.com" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={6}>
                      <Form.Item
                        label="Telefone"
                        name="telefone"
                      >
                        <Input prefix={<PhoneOutlined />} placeholder="(00) 0000-0000" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={6}>
                      <Form.Item
                        label="Celular"
                        name="celular"
                        rules={[
                          { required: true, message: 'Celular é obrigatório!' }
                        ]}
                      >
                        <Input prefix={<PhoneOutlined />} placeholder="(00) 00000-0000" />
                      </Form.Item>
                    </Col>
                  </Row>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Endereço */}
          <TabPane tab="Endereço" key="endereco">
            <Row gutter={16}>
              <Col span={24}>
                <Card title="Endereço Residencial" size="small">
                  <Row gutter={16}>
                    <Col xs={24} sm={8}>
                      <Form.Item
                        label="CEP"
                        name={['endereco', 'cep']}
                        rules={[
                          { required: true, message: 'CEP é obrigatório!' }
                        ]}
                      >
                        <Input placeholder="00000-000" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={16}>
                      <Form.Item
                        label="Logradouro"
                        name={['endereco', 'logradouro']}
                        rules={[
                          { required: true, message: 'Logradouro é obrigatório!' }
                        ]}
                      >
                        <Input placeholder="Rua, Avenida, etc." />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col xs={24} sm={6}>
                      <Form.Item
                        label="Número"
                        name={['endereco', 'numero']}
                        rules={[
                          { required: true, message: 'Número é obrigatório!' }
                        ]}
                      >
                        <Input placeholder="123" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={6}>
                      <Form.Item
                        label="Complemento"
                        name={['endereco', 'complemento']}
                      >
                        <Input placeholder="Sala, Apto, etc." />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="Bairro"
                        name={['endereco', 'bairro']}
                        rules={[
                          { required: true, message: 'Bairro é obrigatório!' }
                        ]}
                      >
                        <Input placeholder="Nome do bairro" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="Cidade"
                        name={['endereco', 'cidade']}
                        rules={[
                          { required: true, message: 'Cidade é obrigatória!' }
                        ]}
                      >
                        <Input placeholder="Nome da cidade" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={6}>
                      <Form.Item
                        label="Estado"
                        name={['endereco', 'estado']}
                        rules={[
                          { required: true, message: 'Estado é obrigatório!' }
                        ]}
                      >
                        <Select placeholder="UF">
                          {estadosBrasileiros.map(estado => (
                            <Option key={estado} value={estado}>{estado}</Option>
                          ))}
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={6}>
                      <Form.Item
                        label="País"
                        name={['endereco', 'pais']}
                        initialValue="Brasil"
                      >
                        <Input placeholder="Brasil" />
                      </Form.Item>
                    </Col>
                  </Row>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Naturalidade */}
          <TabPane tab="Naturalidade" key="naturalidade">
            <Row gutter={16}>
              <Col span={24}>
                <Card title="Naturalidade" size="small">
                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="Cidade de Nascimento"
                        name={['naturalidade', 'cidade']}
                        rules={[
                          { required: true, message: 'Cidade de nascimento é obrigatória!' }
                        ]}
                      >
                        <Input placeholder="Cidade natal" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={6}>
                      <Form.Item
                        label="Estado de Nascimento"
                        name={['naturalidade', 'estado']}
                        rules={[
                          { required: true, message: 'Estado de nascimento é obrigatório!' }
                        ]}
                      >
                        <Select placeholder="UF">
                          {estadosBrasileiros.map(estado => (
                            <Option key={estado} value={estado}>{estado}</Option>
                          ))}
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={6}>
                      <Form.Item
                        label="País de Nascimento"
                        name={['naturalidade', 'pais']}
                        initialValue="Brasil"
                      >
                        <Input placeholder="Brasil" />
                      </Form.Item>
                    </Col>
                  </Row>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Documentos */}
          <TabPane tab="Documentos" key="documentos">
            <Row gutter={16}>
              <Col span={24}>
                <Card title="Documentos de Identificação" size="small">
                  <Row gutter={16}>
                    <Col xs={24} sm={8}>
                      <Form.Item
                        label="RG"
                        name={['documentos', 'rg']}
                        rules={[
                          { required: true, message: 'RG é obrigatório!' }
                        ]}
                      >
                        <Input placeholder="00.000.000-0" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={8}>
                      <Form.Item
                        label="Órgão Expedidor"
                        name={['documentos', 'orgaoExpedidor']}
                        rules={[
                          { required: true, message: 'Órgão expedidor é obrigatório!' }
                        ]}
                      >
                        <Input placeholder="SSP, IFP, etc." />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={8}>
                      <Form.Item
                        label="Data de Expedição"
                        name={['documentos', 'dataExpedicao']}
                        rules={[
                          { required: true, message: 'Data de expedição é obrigatória!' }
                        ]}
                      >
                        <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col xs={24} sm={8}>
                      <Form.Item
                        label="Título de Eleitor"
                        name={['documentos', 'tituloEleitor']}
                      >
                        <Input placeholder="0000.0000.0000" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={8}>
                      <Form.Item
                        label="Carteira de Trabalho"
                        name={['documentos', 'carteiraTrabalho']}
                      >
                        <Input placeholder="00000000-00" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={8}>
                      <Form.Item
                        label="Certificado Reservista"
                        name={['documentos', 'certificadoReservista']}
                      >
                        <Input placeholder="Número do certificado" />
                      </Form.Item>
                    </Col>
                  </Row>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Informações Culturais */}
          <TabPane tab="Informações Culturais" key="informacoes-culturais">
            <Row gutter={16}>
              <Col span={24}>
                <Card title="Perfil Cultural" size="small">
                  <Form.Item
                    label="Áreas de Atuação"
                    name={['informacoesCulturais', 'areaAtuacao']}
                    rules={[
                      { required: true, message: 'Áreas de atuação são obrigatórias!' }
                    ]}
                  >
                    <Checkbox.Group style={{ width: '100%' }}>
                      <Row>
                        {areasAtuacao.map(area => (
                          <Col span={8} key={area}>
                            <Checkbox value={area}>{area}</Checkbox>
                          </Col>
                        ))}
                      </Row>
                    </Checkbox.Group>
                  </Form.Item>

                  <Form.Item
                    label="Profissão/Cargo"
                    name="profissao"
                    rules={[
                      { required: true, message: 'Profissão é obrigatória!' }
                    ]}
                  >
                    <Input placeholder="Ex: Artista Plástico, Músico, Escritor, etc." />
                  </Form.Item>

                  <Row gutter={16}>
                    <Col span={24}>
                      <Form.Item
                        label="Experiência Profissional"
                        name={['informacoesCulturais', 'experiencia']}
                        rules={[
                          { required: true, message: 'Experiência profissional é obrigatória!' }
                        ]}
                      >
                        <TextArea
                          rows={4}
                          placeholder="Descreva sua experiência profissional na área cultural..."
                        />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col span={24}>
                      <Form.Item
                        label="Formação Acadêmica"
                        name={['informacoesCulturais', 'formacao']}
                        rules={[
                          { required: true, message: 'Formação acadêmica é obrigatória!' }
                        ]}
                      >
                        <TextArea
                          rows={3}
                          placeholder="Descreva sua formação acadêmica e cursos relacionados à cultura..."
                        />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    label="Interesses Culturais"
                    name={['informacoesCulturais', 'interesses']}
                  >
                    <Checkbox.Group style={{ width: '100%' }}>
                      <Row>
                        {areasAtuacao.map(area => (
                          <Col span={8} key={area}>
                            <Checkbox value={area}>{area}</Checkbox>
                          </Col>
                        ))}
                      </Row>
                    </Checkbox.Group>
                  </Form.Item>

                  <Form.Item
                    label="Disponibilidade para Atividades Culturais"
                    name={['informacoesCulturais', 'disponibilidade']}
                    rules={[
                      { required: true, message: 'Disponibilidade é obrigatória!' }
                    ]}
                  >
                    <Radio.Group>
                      <Radio value="Tempo integral">Tempo integral</Radio>
                      <Radio value="Meio período">Meio período</Radio>
                      <Radio value="Finais de semana">Finais de semana</Radio>
                      <Radio value="Eventual">Eventual</Radio>
                      <Radio value="Voluntário">Voluntário</Radio>
                    </Radio.Group>
                  </Form.Item>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Situação e Observações */}
          <TabPane tab="Situação" key="situacao">
            <Row gutter={16}>
              <Col span={24}>
                <Card title="Situação do Cadastro" size="small">
                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        label="Situação do Cadastro"
                        name="situacao"
                        rules={[
                          { required: true, message: 'Situação é obrigatória!' }
                        ]}
                      >
                        <Select placeholder="Selecione a situação">
                          <Option value="pendente">Pendente</Option>
                          <Option value="ativo">Ativo</Option>
                          <Option value="inativo">Inativo</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    label="Observações"
                    name="observacoes"
                  >
                    <TextArea
                      rows={4}
                      placeholder="Observações adicionais sobre o cadastro..."
                    />
                  </Form.Item>
                </Card>
              </Col>
            </Row>
          </TabPane>
        </Tabs>
      </Form>
    </Modal>
  );
};

export default CadastroPFModal;
