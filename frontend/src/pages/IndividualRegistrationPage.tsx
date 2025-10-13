import React, { useState } from 'react';
import { Form, Input, Select, DatePicker, Upload, Button, Typography, Steps, message, Card, Row, Col } from 'antd';
import { UploadOutlined, UserOutlined, HomeOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import axios from 'axios';
import { format } from 'date-fns';
import ptBR from 'date-fns/locale/pt-BR';

const { Title, Paragraph } = Typography;
const { Option } = Select;
const { Step } = Steps;

const IndividualRegistrationPage: React.FC = () => {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);

  const culturalAreas: string[] = [
    'Artes Cênicas', 'Música', 'Artes Visuais', 'Literatura', 'Artesanato',
    'Cultura Popular', 'Audiovisual', 'Gestão Cultural', 'Dança', 'Teatro'
  ];

  const documentTypes = [
    { label: 'Comprovante de Residência', value: 'proof_of_residence' },
    { label: 'Portfólio/Currículo', value: 'portfolio' },
    { label: 'Comprovação de Atuação', value: 'proof_experience' },
    { label: 'RG/CPF', value: 'id_document' }
  ];

  const steps = [
    { title: 'Dados Pessoais', icon: <UserOutlined /> },
    { title: 'Endereço', icon: <HomeOutlined /> },
    { title: 'Atuação Cultural', icon: <UserOutlined /> },
    { title: 'Documentos', icon: <UploadOutlined /> }
  ];

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      // Preparar dados para envio
      const formattedValues = {
        ...values,
        birth_date: values.birth_date ? format(values.birth_date.toDate(), 'yyyy-MM-dd') : null,
        cultural_areas: values.cultural_areas?.join(', '),
        // Aqui você pode adicionar lógica para upload de arquivos
      };
      
      const response = await axios.post('/api/registrations/individual', formattedValues);
      message.success('Cadastro enviado com sucesso!');
      console.log('Dados enviados:', response.data);
    } catch (error) {
      message.error('Erro ao enviar cadastro. Tente novamente.');
      console.error('Erro:', error);
    }
    setLoading(false);
  };

  const next = () => {
    form.validateFields().then(() => {
      setCurrentStep(currentStep + 1);
    });
  };

  const prev = () => {
    setCurrentStep(currentStep - 1);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Title level={2}>Cadastro de Pessoa Física - Trabalhador da Cultura</Title>
        <Paragraph>
          Preencha os dados abaixo conforme a Lei N.º 6.306/2023
        </Paragraph>

        <Steps current={currentStep} style={{ marginBottom: '30px' }}>
          {steps.map((item, index) => (
            <Step key={index} title={item.title} icon={item.icon} />
          ))}
        </Steps>

        <Card>
          <Form form={form} layout="vertical" onFinish={onFinish}>
            {/* Passo 1: Dados Pessoais */}
            {currentStep === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Row gutter={16}>
                  <Col span={24}>
                    <Form.Item
                      name="full_name"
                      label="Nome Completo"
                      rules={[{ required: true, message: 'Nome completo é obrigatório' }]}
                    >
                      <Input placeholder="Digite seu nome completo" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name="cpf"
                      label="CPF"
                      rules={[
                        { required: true, message: 'CPF é obrigatório' },
                        { pattern: /^\d{3}\.\d{3}\.\d{3}-\d{2}$/, message: 'CPF inválido' }
                      ]}
                    >
                      <Input placeholder="000.000.000-00" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name="birth_date"
                      label="Data de Nascimento"
                      rules={[{ required: true, message: 'Data de nascimento é obrigatória' }]}
                    >
                      <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name="nationality"
                      label="Nacionalidade"
                      rules={[{ required: true, message: 'Nacionalidade é obrigatória' }]}
                    >
                      <Select placeholder="Selecione">
                        <Option value="brasil">Brasil</Option>
                        <Option value="outros">Outros</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name="rg_document_type"
                      label="Tipo de Documento"
                      rules={[{ required: true, message: 'Tipo de documento é obrigatório' }]}
                    >
                      <Select placeholder="Selecione">
                        <Option value="rg">RG</Option>
                        <Option value="cnh">CNH</Option>
                        <Option value="passaporte">Passaporte</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name="rg_number"
                      label="Número do Documento"
                      rules={[{ required: true, message: 'Número do documento é obrigatório' }]}
                    >
                      <Input placeholder="Número do RG/CNH/Passaporte" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name="rg_issuer"
                      label="Órgão Expedidor"
                      rules={[{ required: true, message: 'Órgão expedidor é obrigatório' }]}
                    >
                      <Input placeholder="Ex: SSP-AM" />
                    </Form.Item>
                  </Col>
                </Row>
              </motion.div>
            )}

            {/* Passo 2: Endereço */}
            {currentStep === 1 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Row gutter={16}>
                  <Col span={8}>
                    <Form.Item
                      name="address_cep"
                      label="CEP"
                      rules={[{ required: true, message: 'CEP é obrigatório' }]}
                    >
                      <Input placeholder="00000-000" />
                    </Form.Item>
                  </Col>
                  <Col span={16}>
                    <Form.Item
                      name="address_street"
                      label="Endereço (Rua/Avenida)"
                      rules={[{ required: true, message: 'Endereço é obrigatório' }]}
                    >
                      <Input placeholder="Nome da rua ou avenida" />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item
                      name="address_number"
                      label="Número"
                      rules={[{ required: true, message: 'Número é obrigatório' }]}
                    >
                      <Input placeholder="Número" />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item
                      name="address_complement"
                      label="Complemento"
                    >
                      <Input placeholder="Apto, Sala, etc." />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item
                      name="address_neighborhood"
                      label="Bairro"
                      rules={[{ required: true, message: 'Bairro é obrigatório' }]}
                    >
                      <Input placeholder="Nome do bairro" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name="address_city"
                      label="Município"
                      rules={[{ required: true, message: 'Município é obrigatório' }]}
                    >
                      <Input placeholder="Nome do município" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name="address_state"
                      label="Estado"
                      initialValue="Amazonas"
                      rules={[{ required: true, message: 'Estado é obrigatório' }]}
                    >
                      <Select>
                        <Option value="amazonas">Amazonas</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>
              </motion.div>
            )}

            {/* Passo 3: Atuação Cultural */}
            {currentStep === 2 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Form.Item
                  name="cultural_areas"
                  label="Áreas de Atuação Cultural"
                  rules={[{ required: true, message: 'Selecione pelo menos uma área' }]}
                >
                  <Select
                    mode="multiple"
                    placeholder="Selecione suas áreas de atuação"
                    style={{ width: '100%' }}
                  >
                    {culturalAreas.map(area => (
                      <Option key={area} value={area}>{area}</Option>
                    ))}
                  </Select>
                </Form.Item>
                <Form.Item
                  name="portfolio_url"
                  label="Portfólio ou Currículo Artístico (URL)"
                >
                  <Input placeholder="https://..." />
                </Form.Item>
                <Form.Item
                  name="experience_description"
                  label="Descrição da Atuação (mínimo 2 anos)"
                  rules={[{ required: true, message: 'Descreva sua experiência' }]}
                >
                  <Input.TextArea
                    rows={4}
                    placeholder="Descreva suas experiências profissionais na área cultural"
                  />
                </Form.Item>
              </motion.div>
            )}

            {/* Passo 4: Documentos */}
            {currentStep === 3 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Paragraph>Faça upload dos documentos necessários:</Paragraph>
                {documentTypes.map(doc => (
                  <Form.Item key={doc.value} label={doc.label}>
                    <Upload
                      name={doc.value}
                      listType="picture"
                      beforeUpload={() => false}
                      maxCount={1}
                    >
                      <Button icon={<UploadOutlined />}>Selecionar arquivo</Button>
                    </Upload>
                  </Form.Item>
                ))}
              </motion.div>
            )}

            <div style={{ marginTop: '20px', textAlign: 'center' }}>
              {currentStep > 0 && (
                <Button style={{ margin: '0 8px' }} onClick={prev}>
                  Anterior
                </Button>
              )}
              {currentStep < steps.length - 1 && (
                <Button type="primary" onClick={next}>
                  Próximo
                </Button>
              )}
              {currentStep === steps.length - 1 && (
                <Button type="primary" htmlType="submit" loading={loading}>
                  Enviar Cadastro
                </Button>
              )}
            </div>
          </Form>
        </Card>
      </motion.div>
    </div>
  );
};

export default IndividualRegistrationPage;
