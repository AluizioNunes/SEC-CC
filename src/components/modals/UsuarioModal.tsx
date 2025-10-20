import React, { useEffect } from 'react';
import { Modal, Form, Input, Select } from 'antd';
import { useAdmin, type AdminUser, type Profile } from '../../contexts/AdminContext';
import { useAuth } from '../../contexts/AuthContext';

interface UsuarioModalProps {
  open: boolean;
  onClose: () => void;
  initial?: AdminUser | null;
}

const UsuarioModal: React.FC<UsuarioModalProps> = ({ open, onClose, initial }) => {
  const [form] = Form.useForm();
  const { profiles, addUser, updateUser } = useAdmin();
  const { user } = useAuth();

  useEffect(() => {
    if (initial) {
      form.setFieldsValue({
        name: initial.name,
        email: initial.email,
        type: initial.type,
        status: initial.status || 'approved',
        profileId: initial.profileId,
      });
    } else {
      form.resetFields();
    }
  }, [initial, form]);

  const handleOk = async () => {
    const values = await form.validateFields();
    const actor = user ? { id: user.id, name: user.name } : undefined;
    if (initial) {
      updateUser(initial.id, {
        name: values.name,
        email: values.email,
        type: values.type,
        status: values.status,
        profileId: values.profileId,
      }, actor);
    } else {
      if (!user) return;
      addUser({
        name: values.name,
        email: values.email,
        type: values.type,
        status: values.status,
        profileId: values.profileId,
        createdBy: { id: user.id, name: user.name },
        createdAt: Date.now(),
      }, actor);
    }
    onClose();
  };

  return (
    <Modal
      title={initial ? 'Editar Usuário' : 'Novo Usuário'}
      open={open}
      onCancel={onClose}
      onOk={handleOk}
      okText={initial ? 'Salvar' : 'Cadastrar'}
    >
      <Form layout="vertical" form={form}>
        <Form.Item label="Nome" name="name" rules={[{ required: true, message: 'Informe o nome' }]}> 
          <Input />
        </Form.Item>
        <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email' }]}> 
          <Input />
        </Form.Item>
        <Form.Item label="Tipo" name="type" rules={[{ required: true }]}> 
          <Select options={[{ value: 'PF', label: 'Pessoa Física' }, { value: 'PJ', label: 'Pessoa Jurídica' }]} />
        </Form.Item>
        <Form.Item label="Perfil" name="profileId" rules={[{ required: true, message: 'Selecione o perfil' }]}> 
          <Select options={profiles.map((p: Profile) => ({ value: p.id, label: p.name }))} />
        </Form.Item>
        <Form.Item label="Status" name="status" initialValue={'approved'}> 
          <Select options={[{ value: 'approved', label: 'Aprovado' }, { value: 'pending', label: 'Pendente' }, { value: 'active', label: 'Ativo' }, { value: 'inactive', label: 'Inativo' }]} />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default UsuarioModal;