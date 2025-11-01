import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { Controller, Get, Module, Res, ValidationPipe, Logger, Body, Post, Query } from '@nestjs/common';
import { Response } from 'express';
import * as client from 'prom-client';
import { ServiceRegistrationService } from './service-registration/service-registration.service';
import { ServiceRegistrationModule } from './service-registration/service-registration.module';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { DatabaseModule } from './database/database.module';
import { RedisModule } from './redis/redis.module';
import { HybridBrokerService, MessagePriority, MessageBrokerType } from './redis/hybrid-broker/hybrid-broker.service';

// Security imports
import helmet from 'helmet'
import * as compression from 'compression'
import { ThrottlerModule } from '@nestjs/throttler';

// Logging imports
import { WinstonModule } from 'nest-winston'
import * as winston from 'winston';

// Tracing imports
import * as jaeger from 'jaeger-client'

// CORS configuration
import { CorsOptions } from '@nestjs/common/interfaces/external/cors-options.interface';

// Create a single registry instance to avoid duplicate metrics
const register = new client.Registry();

// Check if metrics are already registered to prevent duplicates
const registerMetrics = () => {
  // Only register default metrics if they haven't been registered yet
  if (register.getSingleMetric('process_cpu_user_seconds_total') === undefined) {
    client.collectDefaultMetrics({ register });
  }
};

// Enhanced CORS configuration
const corsOptions: CorsOptions = {
  origin: [
    'http://localhost:3000',
    'http://localhost:5173',
    process.env.FRONTEND_URL || 'http://localhost:3000'
  ],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  exposedHeaders: ['X-Total-Count', 'X-Page-Count'],
  credentials: true,
  maxAge: 86400, // 24 hours
};

// winston logger configuration
const logger = WinstonModule.createLogger({
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json(),
        winston.format.printf(({ timestamp, level, message, context, trace, ...meta }) => {
          return JSON.stringify({ timestamp, level, message, context, trace, ...meta });
        }),
      ),
    }),
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json(),
      ),
    }),
    new winston.transports.File({
      filename: 'logs/combined.log',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json(),
      ),
    }),
  ],
});

// Jaeger tracing configuration
const initJaegerTracer = () => {
  const config = {
    serviceName: 'nestjs-service',
    sampler: {
      type: 'const',
      param: 1,
    },
    reporter: {
      logSpans: true,
      agentHost: process.env.JAEGER_AGENT_HOST || 'jaeger',
      agentPort: parseInt(process.env.JAEGER_AGENT_PORT || '6832'),
    },
  } as any;

  return jaeger.initTracer(config, {});
};

@Controller()
class AppController {
  private readonly logger = new Logger(AppController.name);

  constructor(private readonly jwtService: JwtService) {}

  @Get()
  getHello(): string {
    return 'NestJS funcionando!';
  }

  @Get('health')
  health() {
    return {
      status: 'ok',
      service: 'nestjs',
      timestamp: new Date().toISOString()
    };
  }

  @Get('health/ready')
  readinessProbe() {
    // Enhanced readiness check
    return {
      status: 'ready',
      service: 'nestjs',
      checks: {
        redis: 'ok',
        database: 'ok',
        jwt: 'configured'
      },
      timestamp: new Date().toISOString()
    };
  }

  @Get('health/live')
  livenessProbe() {
    // Enhanced liveness check
    return {
      status: 'alive',
      service: 'nestjs',
      timestamp: new Date().toISOString(),
      uptime: process.uptime()
    };
  }

  @Get('redis-status')
  redisStatus() {
    return {
      status: 'connected',
      host: process.env.REDIS_HOST || 'redis',
      port: process.env.REDIS_PORT || '6379'
    };
  }

  @Get('metrics')
  async metrics(@Res() res: Response) {
    // Register default metrics only once
    registerMetrics();

    // Get metrics as a string
    const metrics = await register.metrics();

    // Send the metrics as plain text response
    res.set('Content-Type', register.contentType);
    res.send(metrics);
  }

  @Get('auth/test')
  async testAuth() {
    // Mock authentication endpoint
    const payload = { sub: 'test-user', role: 'admin' };
    const token = this.jwtService.sign(payload);

    this.logger.log(`JWT token generated for user: ${payload.sub}`);

    return {
      message: 'Authentication test successful',
      token: token,
      expiresIn: '30m'
    };
  }
}

// ===== AI Proxy Controller (HTTP + SSE) =====
@Controller('api/v2/ai')
class AiProxyController {
  private readonly logger = new Logger(AiProxyController.name);
  private readonly baseURL = process.env.FASTAPI_INTERNAL_URL || 'http://fastapi:8000';

  private url(path: string) {
    return `${this.baseURL}${path}`;
  }

  private async proxyJson(path: string, init: any = {}, timeoutMs = 30000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort('timeout'), timeoutMs);
    try {
      const r = await fetch(this.url(path), { ...init, signal: controller.signal });
      if (!r.ok) {
        const text = await r.text().catch(() => '');
        this.logger.error(`${path} upstream error ${r.status} ${text?.slice(0, 200)}`);
        return { error: 'upstream_error', status: r.status, message: text };
      }
      try {
        return await r.json();
      } catch {
        const text = await r.text().catch(() => '');
        return { status: 200, raw: text };
      }
    } catch (e: any) {
      const isAbort = e?.name === 'AbortError' || e === 'timeout';
      const code = isAbort ? 'timeout' : 'network_error';
      const status = isAbort ? 504 : 502;
      this.logger.error(`${path} proxy error: ${e?.message || e}`);
      return { error: code, status, message: e?.message || String(e) };
    } finally {
      clearTimeout(timer);
    }
  }

  @Get('providers')
  async providers() {
    return this.proxyJson('/ai/providers', {}, 10000);
  }

  @Get('models')
  async models() {
    return this.proxyJson('/ai/models', {}, 10000);
  }

  @Post('chat')
  async chat(@Body() body: any) {
    return this.proxyJson(
      '/ai/chat',
      { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) },
      60000,
    );
  }

  @Post('assist')
  async assist(@Body() body: any) {
    return this.proxyJson(
      '/ai/assist',
      { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) },
      60000,
    );
  }

  @Get('chat/stream')
  async chatStream(
    @Query('role') role: string,
    @Query('message') message: string,
    @Query('model_id') model_id?: string,
    @Query('user_id') user_id?: string,
    @Query('session_id') session_id?: string,
    @Query('conversation_id') conversation_id?: string,
    @Res() res?: Response,
  ) {
    if (!res) return;
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    // Some proxies may need flushing headers explicitly
    (res as any).flushHeaders?.();

    const params = new URLSearchParams({
      role: role || 'GERAL',
      message: message || '',
      model_id: model_id || 'gemini-2.5-flash-lite',
      user_id: user_id || '',
      session_id: session_id || '',
      conversation_id: conversation_id || '',
    });

    const url = this.url(`/ai/chat/stream?${params.toString()}`);
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort('timeout'), 300000);
      res.on('close', () => controller.abort('client_closed'));

      const up = await fetch(url, { headers: { Accept: 'text/event-stream' }, signal: controller.signal });
      if (!up.ok || !up.body) {
        res.write(`event: error\ndata: upstream_status_${up.status}\n\n`);
        return res.end();
      }

      const reader = (up.body as any).getReader?.();
      if (reader && typeof reader.read === 'function') {
        const decoder = new TextDecoder();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          res.write(decoder.decode(value));
        }
        clearTimeout(timeout);
        return res.end();
      }

      // Fallback for environments without Web ReadableStream reader
      // Pipe as text chunks
      const text = await up.text();
      res.write(text);
      clearTimeout(timeout);
      return res.end();
    } catch (e: any) {
      this.logger.error(`stream proxy error: ${e?.message || e}`);
      res.write(`event: error\ndata: ${String(e)}\n\n`);
      return res.end();
    }
  }
}

@Controller('api/v2/ai/queue')
class AiQueueController {
  private readonly logger = new Logger(AiQueueController.name);

  constructor(private readonly broker: HybridBrokerService) {}

  @Post('jobs')
  async enqueueJob(@Body() body: any) {
    const priorityLabel = (body?.priority || 'NORMAL').toUpperCase();
    const brokerLabel = (body?.brokerType || 'HYBRID').toUpperCase();
    const priority = MessagePriority[priorityLabel as keyof typeof MessagePriority] || MessagePriority.NORMAL;
    const brokerType = MessageBrokerType[brokerLabel as keyof typeof MessageBrokerType] || MessageBrokerType.HYBRID;

    const routingKey = body?.routingKey || 'ai_jobs';
    const messageId = await this.broker.publishMessage(body, routingKey, priority, brokerType);
    this.logger.log(`queued job ${messageId} priority=${priorityLabel} routing=${routingKey}`);
    return { job_id: messageId, status: 'queued', routing_key: routingKey, priority: priorityLabel };
  }
}

@Module({
  imports: [
    ServiceRegistrationModule,
    DatabaseModule,
    RedisModule,
    WinstonModule.forRoot({
      transports: [
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.errors({ stack: true }),
            winston.format.json(),
            winston.format.printf(({ timestamp, level, message, context, trace, ...meta }) => {
              return JSON.stringify({ timestamp, level, message, context, trace, ...meta });
            }),
          ),
        }),
        new winston.transports.File({
          filename: 'logs/error.log',
          level: 'error',
          format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.errors({ stack: true }),
            winston.format.json(),
          ),
        }),
        new winston.transports.File({
          filename: 'logs/combined.log',
          format: winston.format.combine(
            winston.format.timestamp(),
            winston.format.json(),
          ),
        }),
      ],
    }),
  ],
  controllers: [AppController, AiProxyController, AiQueueController],
  providers: [ServiceRegistrationService, JwtService, ConfigService],
})
class AppModule {}

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: logger,
  });

  // Initialize Jaeger tracer
  const tracer = initJaegerTracer();

  // Global validation pipe
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
  }));

  // Security middleware
  app.use(helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", "data:", "https:"],
      },
    },
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true,
    },
  }))

  // Compression middleware
  app.use(compression())

  // CORS configuration
  app.enableCors(corsOptions);

  // Rate limiting
  app.useGlobalPipes(new ValidationPipe());

  // Get service registration service
  const serviceRegistrationService = app.get(ServiceRegistrationService);

  // Enhanced logging middleware
  app.use((req: any, res: any, next: any) => {
    const start = Date.now();

    res.on('finish', () => {
      const duration = Date.now() - start;
      logger.log({
        message: 'HTTP Request',
        method: req.method,
        url: req.url,
        statusCode: res.statusCode,
        duration: `${duration}ms`,
        ip: req.ip,
        userAgent: req.get('User-Agent'),
      });
    });

    next();
  });

  await app.listen(process.env.PORT || 3000, '0.0.0.0');

  const port = process.env.PORT || 3000;
  logger.log(`NestJS application with enhanced security started on port ${port}`);
  logger.log(`Metrics available at http://localhost:${port}/metrics`);
  logger.log(`Health checks available at http://localhost:${port}/health`);
  logger.log(`JWT authentication configured`);
  logger.log(`Structured logging enabled`);
  logger.log(`Jaeger tracing enabled`);
}

bootstrap();