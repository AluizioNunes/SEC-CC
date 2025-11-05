import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Login from '../pages/Login';
import { I18nProvider } from '../i18n/I18nContext';

// Mock de asset estático para evitar falha de import em testes
vi.mock('../Images/SEC_GOV-LogoOficial.png', () => ({ default: 'logo.png' }));

// Mock do AuthContext para controlar sucesso do login
vi.mock('../contexts/AuthContext', () => {
  return {
    useAuth: () => ({
      login: vi.fn(async () => true),
      loginGuest: vi.fn(async () => true),
    }),
  };
});

// Helper para preparar localStorage com perfil
const setProfile = (profile: string) => {
  localStorage.setItem(
    'sec-user',
    JSON.stringify({ id: '1', name: 'Teste', email: 't@t.com', profile })
  );
};

const renderWithRoutes = () => {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <Routes>
        <Route
          path="/login"
          element={
            <I18nProvider>
              <Login />
            </I18nProvider>
          }
        />
        <Route path="/admin" element={<div data-testid="route">admin</div>} />
        <Route path="/home" element={<div data-testid="route">home</div>} />
        <Route path="/eventos" element={<div data-testid="route">eventos</div>} />
        <Route path="/dashboard" element={<div data-testid="route">dashboard</div>} />
      </Routes>
    </MemoryRouter>
  );
};

const submitLogin = async () => {
  const user = userEvent.setup();
  const userInput = screen.getByPlaceholderText('usuario ou email');
  const passInput = screen.getByPlaceholderText('Digite sua senha');
  const submitBtn = screen.getByRole('button', { name: /entrar/i });
  await user.type(userInput, 'teste');
  await user.type(passInput, 'senha123');
  await user.click(submitBtn);
};

describe('Redirecionamento por perfil no Login', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('admin → /admin', async () => {
    setProfile('admin');
    renderWithRoutes();
    await submitLogin();
    const indicator = await screen.findByTestId('route');
    expect(indicator).toHaveTextContent('admin');
  });

  it('colaborador → /home', async () => {
    setProfile('colaborador');
    renderWithRoutes();
    await submitLogin();
    const indicator = await screen.findByTestId('route');
    expect(indicator).toHaveTextContent('home');
  });

  it('visitante → /eventos', async () => {
    setProfile('visitante');
    renderWithRoutes();
    await submitLogin();
    const indicator = await screen.findByTestId('route');
    expect(indicator).toHaveTextContent('eventos');
  });

  it('artista → /dashboard', async () => {
    setProfile('artista');
    renderWithRoutes();
    await submitLogin();
    const indicator = await screen.findByTestId('route');
    expect(indicator).toHaveTextContent('dashboard');
  });

  it('user/default → /home', async () => {
    setProfile('user');
    renderWithRoutes();
    await submitLogin();
    const indicator = await screen.findByTestId('route');
    expect(indicator).toHaveTextContent('home');
  });
});