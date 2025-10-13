import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import ptBR from 'antd/locale/pt_BR';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './layout/Layout';
import Home from './pages/Home';
import Sobre from './pages/Sobre';
import Login from './pages/Login';
import Cadastro from './pages/Cadastro';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <ConfigProvider locale={ptBR}>
      <AuthProvider>
        <Router>
          <div className="App">
            <Routes>
              {/* Páginas públicas sem layout */}
              <Route path="/login" element={<Login />} />
              <Route path="/cadastro" element={<Cadastro />} />

              {/* Todas as outras páginas com layout */}
              <Route path="/*" element={
                <Layout>
                  <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/sobre" element={<Sobre />} />
                    <Route path="/contato" element={<Home />} />
                    <Route path="/resultados" element={<Home />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/meu-cadastro" element={<Home />} />
                    <Route path="/solicitacoes" element={<Home />} />
                    <Route path="/renovacao" element={<Home />} />
                    <Route path="/recurso" element={<Home />} />
                    <Route path="/notificacoes" element={<Home />} />
                    <Route path="/perfil" element={<Home />} />
                    <Route path="/configuracoes" element={<Home />} />
                    <Route path="/faq" element={<Home />} />
                    <Route path="/suporte" element={<Home />} />
                    <Route path="/lgpd" element={<Home />} />
                    <Route path="/privacidade" element={<Home />} />
                    <Route path="/termos" element={<Home />} />
                    <Route path="/esqueci-senha" element={<Home />} />
                  </Routes>
                </Layout>
              } />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </ConfigProvider>
  );
}

export default App;
