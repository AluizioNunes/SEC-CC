import '@testing-library/jest-dom';

// Polyfills simples úteis em ambiente de teste
// Ant Design e framer-motion podem consultar matchMedia
if (!window.matchMedia) {
  // @ts-expect-error test polyfill
  window.matchMedia = (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  });
}

// Mocks para evitar transformações pesadas e dependências não essenciais nos testes
import { vi } from 'vitest';

// Mock de antd: componentes mínimos suficientes para o fluxo do Login
vi.mock('antd', () => {
  const React = require('react');
  const FormItem = ({ children }: any) => React.createElement('div', null, children);
  const FormComp: any = ({ children, onFinish }: any) =>
    React.createElement(
      'form',
      {
        onSubmit: (e: any) => {
          e.preventDefault();
          // Valores mínimos para acionar o onFinish
          onFinish && onFinish({ usuario: 'teste', password: 'senha123' });
        },
      },
      children
    );
  FormComp.Item = FormItem;
  FormComp.useForm = () => [{}];

  const Input = ({ placeholder, ...props }: any) =>
    React.createElement('input', { placeholder, ...props });
  Input.Password = ({ placeholder, ...props }: any) =>
    React.createElement('input', { type: 'password', placeholder, ...props });

  const Button = ({ children, htmlType, onClick, ...props }: any) =>
    React.createElement('button', { type: htmlType || 'button', onClick, ...props }, children);

  const Typography = {
    Title: ({ children }: any) => React.createElement('div', null, children),
    Paragraph: ({ children }: any) => React.createElement('div', null, children),
    Text: ({ children }: any) => React.createElement('span', null, children),
  };

  const Alert = ({ message }: any) => React.createElement('div', null, message);
  const Row = ({ children }: any) => React.createElement('div', null, children);
  const Col = ({ children }: any) => React.createElement('div', null, children);
  const Divider = () => React.createElement('hr');

  return { Form: FormComp, Input, Button, Typography, Alert, Row, Col, Divider };
});

// Mock de ícones do Ant Design
vi.mock('@ant-design/icons', () => {
  const React = require('react');
  const Noop = () => null;
  return {
    UserOutlined: Noop,
    LockOutlined: Noop,
    LoginOutlined: Noop,
    EyeInvisibleOutlined: Noop,
    EyeOutlined: Noop,
    QuestionCircleOutlined: Noop,
    BugOutlined: Noop,
    GoogleOutlined: Noop,
    MailOutlined: Noop,
    LinkedinOutlined: Noop,
    InstagramOutlined: Noop,
    ArrowRightOutlined: Noop,
  };
});

// Mock de framer-motion para evitar transformações complexas
vi.mock('framer-motion', () => {
  const React = require('react');
  return {
    motion: {
      div: ({ children, ...props }: any) => React.createElement('div', props, children),
    },
  };
});