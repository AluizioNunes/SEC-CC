import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import ptBR from 'antd/locale/pt_BR';
import { AuthProvider } from './contexts/AuthContext';
import { PessoaFisicaProvider } from './contexts/PessoaFisicaContext';
import { AdminProvider } from './contexts/AdminContext';
import Layout from './layout/Layout';
import Home from './pages/Home';
import Sobre from './pages/Sobre';
import Login from './pages/Login';
import Cadastros from './pages/Cadastros';
import Dashboard from './pages/Dashboard';
import CadastroPF from './pages/CadastroPF';
import Oportunidades from './pages/Oportunidades';
import Eventos from './pages/Eventos';
import Espacos from './pages/Espacos';
import Agentes from './pages/Agentes';
import Projetos from './pages/Projetos';
import Cursos from './pages/Cursos';
import OportunidadeDetalhe from './pages/OportunidadeDetalhe';
import EventoDetalhe from './pages/EventoDetalhe';
import EspacoDetalhe from './pages/EspacoDetalhe';
import AgenteDetalhe from './pages/AgenteDetalhe';
import ProjetoDetalhe from './pages/ProjetoDetalhe';
import CursoDetalhe from './pages/CursoDetalhe';
import Usuarios from './pages/admin/Usuarios';
import Perfil from './pages/admin/Perfil';
import Permissoes from './pages/admin/Permissoes';
import Auditoria from './pages/admin/Auditoria';
import { useAuth } from './contexts/AuthContext';
import ChatWidget from './components/ChatWidget';

function AdminOnly({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  if (user?.profile !== 'admin') {
    return <Layout><Home /></Layout>;
  }
  return <>{children}</>;
}

function App() {
  return (
    <div style={{ backgroundColor: '#f0f2f5', minHeight: '100vh' }}>
      <ConfigProvider locale={ptBR}>
        <AuthProvider>
          <PessoaFisicaProvider>
            <AdminProvider>
              <Router>
                <Routes>
                  {/* Página inicial é o login */}
                  <Route path="/" element={<Login />} />

                  {/* Páginas públicas sem layout */}
                  <Route path="/login" element={<Login />} />
                  <Route path="/Cadastros" element={<Cadastros />} />

                  {/* Todas as outras páginas com layout */}
                  <Route path="/home" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/sobre" element={
                    <Layout>
                      <Sobre />
                    </Layout>
                  } />
                  <Route path="/contato" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/resultados" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/dashboard" element={
                    <Layout>
                      <Dashboard />
                    </Layout>
                  } />
                  <Route path="/oportunidades" element={
                    <Layout>
                      <Oportunidades />
                    </Layout>
                  } />
                  <Route path="/oportunidades/:id" element={
                    <Layout>
                      <OportunidadeDetalhe />
                    </Layout>
                  } />
                  <Route path="/eventos" element={
                    <Layout>
                      <Eventos />
                    </Layout>
                  } />
                  <Route path="/eventos/:id" element={
                    <Layout>
                      <EventoDetalhe />
                    </Layout>
                  } />
                  <Route path="/espacos" element={
                    <Layout>
                      <Espacos />
                    </Layout>
                  } />
                  <Route path="/espacos/:id" element={
                    <Layout>
                      <EspacoDetalhe />
                    </Layout>
                  } />
                  <Route path="/agentes" element={
                    <Layout>
                      <Agentes />
                    </Layout>
                  } />
                  <Route path="/agentes/:id" element={
                    <Layout>
                      <AgenteDetalhe />
                    </Layout>
                  } />
                  <Route path="/projetos" element={
                    <Layout>
                      <Projetos />
                    </Layout>
                  } />
                  <Route path="/projetos/:id" element={
                    <Layout>
                      <ProjetoDetalhe />
                    </Layout>
                  } />
                  <Route path="/cursos" element={
                    <Layout>
                      <Cursos />
                    </Layout>
                  } />
                  <Route path="/cursos/:id" element={
                    <Layout>
                      <CursoDetalhe />
                    </Layout>
                  } />
                  <Route path="/CadastroPF" element={
                    <Layout>
                      <CadastroPF />
                    </Layout>
                  } />
                  {/* Rotas administrativas */}
                  <Route path="/admin/usuarios" element={
                    <AdminOnly>
                      <Layout>
                        <Usuarios />
                      </Layout>
                    </AdminOnly>
                  } />
                  <Route path="/admin/perfil" element={
                    <AdminOnly>
                      <Layout>
                        <Perfil />
                      </Layout>
                    </AdminOnly>
                  } />
                  <Route path="/admin/permissoes" element={
                    <AdminOnly>
                      <Layout>
                        <Permissoes />
                      </Layout>
                    </AdminOnly>
                  } />
                  <Route path="/admin/auditoria" element={
                    <AdminOnly>
                      <Layout>
                        <Auditoria />
                      </Layout>
                    </AdminOnly>
                  } />

                  {/* Resto */}
                  <Route path="/meu-cadastro" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/solicitacoes" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/renovacao" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/recurso" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/notificacoes" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/perfil" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/configuracoes" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/faq" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/suporte" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/lgpd" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/privacidade" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/termos" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                  <Route path="/esqueci-senha" element={
                    <Layout>
                      <Home />
                    </Layout>
                  } />
                </Routes>
              </Router>
            </AdminProvider>
          </PessoaFisicaProvider>
        </AuthProvider>
      </ConfigProvider>
      <ChatWidget />
    </div>
  );
}

export default App;
