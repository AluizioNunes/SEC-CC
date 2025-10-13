import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import ptBR from 'antd/locale/pt_BR';
import { motion } from 'framer-motion';
import './App.css';

// Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import IndividualRegistrationPage from './pages/IndividualRegistrationPage';
import EntityRegistrationPage from './pages/EntityRegistrationPage';
import DashboardPage from './pages/DashboardPage';
import AdminPage from './pages/AdminPage';

const App: React.FC = () => {
  return (
    <ConfigProvider locale={ptBR}>
      <Router>
        <div className="App">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/register/individual" element={<IndividualRegistrationPage />} />
              <Route path="/register/entity" element={<EntityRegistrationPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/admin" element={<AdminPage />} />
            </Routes>
          </motion.div>
        </div>
      </Router>
    </ConfigProvider>
  );
};

export default App;
