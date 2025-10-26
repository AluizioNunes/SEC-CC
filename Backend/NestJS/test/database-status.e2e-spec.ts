import request from 'supertest';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

// Teste leve que valida o endpoint real em execução
// Útil para detectar regressões sem bootstrapping completo do AppModule

describe('HTTP /database/status (health)', () => {
  it('retorna 200 OK', async () => {
    const res = await request(BASE_URL).get('/database/status').timeout({ deadline: 5000 });
    expect(res.status).toBe(200);
    // Opcional: validar estrutura básica do corpo
    if (res.type === 'application/json') {
      const data = res.body;
      expect(data).toBeDefined();
    }
  });
});