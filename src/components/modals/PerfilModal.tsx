import React, { useEffect } from 'react';
import { Modal, Form, Input } from 'antd';
import { useAdmin, type Profile } from '../../contexts/AdminContext';
import { useAuth } from '../../contexts/AuthContext';
import NavbarCompact from '../NavbarCompact';

interface PerfilModalProps {
  open: boolean;
  onClose: () => void;
  initial?: Profile | null;
}

const PerfilModal: React.FC<PerfilModalProps> = ({ open, onClose, initial }) => {
  const [form] = Form.useForm();
  const { addProfile, updateProfile } = useAdmin();
  const { user } = useAuth();

  useEffect(() => {
    if (initial) {
      form.setFieldsValue({
        name: initial.name,
        description: initial.description,
      });
    } else {
      form.resetFields();
    }
  }, [initial, form]);

  const handleOk = async () => {
    const values = await form.validateFields();
    const actor = user ? { id: user.id, name: user.name } : undefined;
    if (initial) {
      updateProfile(initial.id, { name: values.name, description: values.description }, actor);
    } else {
      addProfile({ name: values.name, description: values.description }, actor);
    }
    onClose();
  };

  return (
    <Modal
      title={<NavbarCompact variant="modalHeader" />}
      open={open}
      onCancel={onClose}
      onOk={handleOk}
      okText={initial ? 'Salvar' : 'Cadastrar'}
      width={800}
    >
      {/* Removido header dentro do corpo, substituído por title custom */}
      <Form layout="vertical" form={form}>
        <Form.Item label="Nome do Perfil" name="name" rules={[{ required: true, message: 'Informe o nome do perfil' }]}> 
          <Input />
        </Form.Item>
        <Form.Item label="Descrição" name="description"> 
          <Input.TextArea rows={4} />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default PerfilModal;