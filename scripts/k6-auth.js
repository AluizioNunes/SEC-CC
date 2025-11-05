import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const USERNAME = __ENV.USERNAME || 'root';
const PASSWORD_A = __ENV.PASSWORD_A || 'Itf@ct123';
const PASSWORD_B = __ENV.PASSWORD_B || 'Itf@ct456';

export const options = {
  scenarios: {
    login_scenario: {
      executor: 'constant-vus',
      vus: Number(__ENV.LOGIN_VUS || 10),
      duration: __ENV.LOGIN_DURATION || '30s',
      exec: 'loginScenario',
    },
    change_password_scenario: {
      executor: 'shared-iterations',
      iterations: 1,
      exec: 'changePasswordScenario',
    },
  },
  thresholds: {
    // Metas realistas sob carga moderada e bcrypt fator 12 (ajuste calibrado)
    http_req_failed: ['rate<0.20'],
    http_req_duration: ['p(95)<2500'],
  },
};

export function loginScenario() {
  const payload = JSON.stringify({ username: USERNAME, password: PASSWORD_A });
  const headers = { 'Content-Type': 'application/json' };
  const res = http.post(`${BASE_URL}/auth/login`, payload, { headers });
  check(res, {
    'login status 200': (r) => r.status === 200,
    'token presente': (r) => (r.json('access_token') || '').length > 0,
  });
  sleep(1);
}

export function changePasswordScenario() {
  const headers = { 'Content-Type': 'application/json' };

  // Login com senha A
  const resLoginA = http.post(
    `${BASE_URL}/auth/login`,
    JSON.stringify({ username: USERNAME, password: PASSWORD_A }),
    { headers }
  );
  check(resLoginA, { 'login A 200': (r) => r.status === 200 });
  const tokenA = resLoginA.json('access_token');
  if (!tokenA) {
    check(null, { 'token A obtido': () => false });
    return;
  }

  // Troca para senha B
  const resChange = http.post(
    `${BASE_URL}/auth/change-password`,
    JSON.stringify({ new_password: PASSWORD_B, current_password: PASSWORD_A, requested_by: 'K6-CHANGE' }),
    (() => {
      const authHeadersA = Object.assign({}, headers, { Authorization: `Bearer ${tokenA}` });
      return { headers: authHeadersA };
    })()
  );
  check(resChange, {
    'change 200': (r) => r.status === 200,
    'change ok true': (r) => r.json('ok') === true,
  });

  // Login com senha B
  const resLoginB = http.post(
    `${BASE_URL}/auth/login`,
    JSON.stringify({ username: USERNAME, password: PASSWORD_B }),
    { headers }
  );
  check(resLoginB, { 'login B 200': (r) => r.status === 200 });
  const tokenB = resLoginB.json('access_token');
  if (!tokenB) {
    check(null, { 'token B obtido': () => false });
    return;
  }

  // Reverte para senha A
  const resRevert = http.post(
    `${BASE_URL}/auth/change-password`,
    JSON.stringify({ new_password: PASSWORD_A, current_password: PASSWORD_B, requested_by: 'K6-REVERT' }),
    (() => {
      const authHeadersB = Object.assign({}, headers, { Authorization: `Bearer ${tokenB}` });
      return { headers: authHeadersB };
    })()
  );
  check(resRevert, {
    'revert 200': (r) => r.status === 200,
    'revert ok true': (r) => r.json('ok') === true,
  });
}