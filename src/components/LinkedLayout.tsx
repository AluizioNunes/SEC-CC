import React from 'react';
import { Layout as AntLayout, Card, Typography, Space, Grid } from 'antd';

const { Header, Sider, Content } = AntLayout;
const { Title, Paragraph } = Typography;

interface LinkedLayoutProps {
  title: string;
  subtitle?: string;
  left?: React.ReactNode;
  right?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
}

const LinkedLayout: React.FC<LinkedLayoutProps> = ({ title, subtitle, left, right, actions, children }) => {
  const screens = Grid.useBreakpoint();
  const isDesktop = screens.lg;

  // Larguras dinâmicas para aproveitar toda a página em telas grandes
  const leftWidth = screens.xxl ? 340 : screens.xl ? 320 : 280;
  const rightWidth = screens.xxl ? 380 : screens.xl ? 340 : 300;

  return (
    <div className="linked-layout" style={{ background: '#f3f2ef', minHeight: '100%', padding: screens.xs ? 12 : 24 }}>
      {/* Cabeçalho */}
      <AntLayout style={{ background: 'transparent', margin: 0 }}>
        <Header style={{ background: 'transparent', padding: 0 }}>
          <Card styles={{ body: { padding: 20 } }}>
            <Space style={{ width: '100%', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
              <div style={{ minWidth: 200 }}>
                <Title level={2} style={{ marginBottom: 4 }}>{title}</Title>
                {subtitle && <Paragraph type="secondary" style={{ margin: 0 }}>{subtitle}</Paragraph>}
              </div>
              {actions && <div>{actions}</div>}
            </Space>
          </Card>
        </Header>

        {isDesktop ? (
          // Layout 3 colunas em telas grandes, sem limite de largura
          <AntLayout style={{ background: 'transparent' }}>
            {left && (
              <Sider width={leftWidth} breakpoint="lg" collapsedWidth={0} style={{ background: 'transparent' }}>
                <Card styles={{ body: { padding: 16 } }}>{left}</Card>
              </Sider>
            )}

            <Content style={{ background: 'transparent', minWidth: 0 }}>
              <Card styles={{ body: { padding: 16 } }}>{children}</Card>
            </Content>

            {right && (
              <Sider width={rightWidth} breakpoint="xl" collapsedWidth={0} style={{ background: 'transparent' }}>
                <Card styles={{ body: { padding: 16 } }}>{right}</Card>
              </Sider>
            )}
          </AntLayout>
        ) : (
          // Em telas pequenas, empilha: filtros, conteúdo e sugestões
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {left && <Card styles={{ body: { padding: 16 } }}>{left}</Card>}
            <Card styles={{ body: { padding: 16 } }}>{children}</Card>
            {right && <Card styles={{ body: { padding: 16 } }}>{right}</Card>}
          </div>
        )}
      </AntLayout>
    </div>
  );
};

export default LinkedLayout;